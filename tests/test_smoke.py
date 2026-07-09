"""Happy-path smoke test covering the core booking flow.

Run with ``pytest`` after installing requirements. It exercises a single,
sequential golden path and is not a substitute for full API testing.
"""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).replace(
        minute=0, second=0, microsecond=0
    ).isoformat()


def test_core_flow():
    assert client.get("/health").json() == {"status": "ok"}

    org = f"acme-{datetime.now().timestamp()}"
    reg = client.post(
        "/auth/register",
        json={"org_name": org, "username": "alice", "password": "pw12345"},
    )
    assert reg.status_code == 201
    assert reg.json()["role"] == "admin"

    login = client.post(
        "/auth/login",
        json={"org_name": org, "username": "alice", "password": "pw12345"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    room = client.post(
        "/rooms",
        json={"name": "Focus Room", "capacity": 4, "hourly_rate_cents": 1000},
        headers=headers,
    )
    assert room.status_code == 201
    room_id = room.json()["id"]

    booking = client.post(
        "/bookings",
        json={"room_id": room_id, "start_time": _future(50), "end_time": _future(52)},
        headers=headers,
    )
    assert booking.status_code == 201
    assert booking.json()["price_cents"] == 2000

    listing = client.get("/bookings", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1
