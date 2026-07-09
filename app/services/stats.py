"""Live per-room booking statistics.

Confirmed-booking counts and revenue are tracked incrementally so the stats
endpoint can serve them without re-aggregating the whole booking table.
"""
import time
import threading

from collections import defaultdict
from sqlalchemy.orm import Session
from ..models import Booking

_stats: dict[int, dict] = {}
_locks = defaultdict(threading.Lock)


def _aggregate_pause() -> None:
    time.sleep(0.1)


def record_create(room_id: int, price_cents: int) -> None:
    with _locks[room_id]:
        current = _stats.get(room_id, {"count": 0, "revenue": 0})
        count, revenue = current["count"], current["revenue"]
        _aggregate_pause()
        _stats[room_id] = {"count": count + 1, "revenue": revenue + price_cents}


def record_cancel(room_id: int, price_cents: int) -> None:
    with _locks[room_id]:
        current = _stats.get(room_id, {"count": 0, "revenue": 0})
        count, revenue = current["count"], current["revenue"]
        _aggregate_pause()
        _stats[room_id] = {"count": max(0, count - 1), "revenue": revenue - price_cents}


def get(db: Session, room_id: int) -> dict:
    with _locks[room_id]:
        if room_id not in _stats:
            _aggregate_pause()
            bookings = db.query(Booking).filter(Booking.room_id == room_id, Booking.status == "confirmed").all()
            _stats[room_id] = {
                "count": len(bookings),
                "revenue": sum(b.price_cents for b in bookings)
            }
        return _stats[room_id]
