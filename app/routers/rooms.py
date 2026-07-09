"""Room management, availability and live statistics."""
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import cache
from ..auth import get_current_user, require_admin
from ..database import get_db
from ..errors import AppError
from ..models import Booking, Room, User
from ..schemas import RoomCreateRequest
from ..services import stats
from ..timeutils import iso_utc

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _serialize_room(room: Room) -> dict:
    return {
        "id": room.id,
        "org_id": room.org_id,
        "name": room.name,
        "capacity": room.capacity,
        "hourly_rate_cents": room.hourly_rate_cents,
    }


def _get_org_room(db: Session, room_id: int, org_id: int) -> Room:
    room = db.query(Room).filter(Room.id == room_id, Room.org_id == org_id).first()
    if room is None:
        raise AppError(404, "ROOM_NOT_FOUND", "Room not found")
    return room


@router.get("")
def list_rooms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rooms = db.query(Room).filter(Room.org_id == user.org_id).order_by(Room.id.asc()).all()
    return [_serialize_room(r) for r in rooms]


@router.post("", status_code=201)
def create_room(
    payload: RoomCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    room = Room(
        org_id=admin.org_id,
        name=payload.name,
        capacity=payload.capacity,
        hourly_rate_cents=payload.hourly_rate_cents,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return _serialize_room(room)


@router.get("/{room_id}/availability")
def availability(
    room_id: int,
    date: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    room = _get_org_room(db, room_id, user.org_id)

    cached = cache.get_availability(room.id, date)
    if cached is not None:
        return cached

    try:
        day = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise AppError(400, "INVALID_BOOKING_WINDOW", "Invalid date")

    day_start = datetime.combine(day, time.min)
    day_end = day_start + timedelta(days=1)
    bookings = (
        db.query(Booking)
        .filter(
            Booking.room_id == room.id,
            Booking.status == "confirmed",
            Booking.start_time >= day_start,
            Booking.start_time < day_end,
        )
        .order_by(Booking.start_time.asc(), Booking.id.asc())
        .all()
    )
    result = {
        "room_id": room.id,
        "date": date,
        "busy": [
            {"start_time": iso_utc(b.start_time), "end_time": iso_utc(b.end_time)}
            for b in bookings
        ],
    }
    cache.set_availability(room.id, date, result)
    return result


@router.get("/{room_id}/stats")
def room_stats(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    room = _get_org_room(db, room_id, user.org_id)
    current = stats.get(room.id)
    return {
        "room_id": room.id,
        "total_confirmed_bookings": current["count"],
        "total_revenue_cents": current["revenue"],
    }
