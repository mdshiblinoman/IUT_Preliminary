"""CSV export of bookings for administrators."""
import csv
import io

from sqlalchemy.orm import Session

from ..models import Booking, Room
from ..timeutils import iso_utc

EXPORT_HEADER = [
    "id",
    "reference_code",
    "room_id",
    "user_id",
    "start_time",
    "end_time",
    "status",
    "price_cents",
]


def fetch_bookings_raw(db: Session, room_id: int, org_id: int) -> list[Booking]:
    """Load every booking for a single room, ordered by id."""
    return (
        db.query(Booking)
        .join(Room)
        .filter(Booking.room_id == room_id, Room.org_id == org_id)
        .order_by(Booking.id.asc())
        .all()
    )


def _fetch_scoped(db: Session, org_id: int, user_id: int | None, room_id: int | None) -> list[Booking]:
    query = db.query(Booking).join(Room).filter(Room.org_id == org_id)
    if user_id is not None:
        query = query.filter(Booking.user_id == user_id)
    if room_id is not None:
        query = query.filter(Booking.room_id == room_id)
    return query.order_by(Booking.id.asc()).all()


def generate_export(
    db: Session,
    org_id: int,
    user_id: int,
    room_id: int | None,
    include_all: bool,
) -> str:
    if include_all:
        if room_id is not None:
            rows = fetch_bookings_raw(db, room_id, org_id)
        else:
            rows = _fetch_scoped(db, org_id, None, None)
    else:
        rows = _fetch_scoped(db, org_id, user_id, room_id)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(EXPORT_HEADER)
    for b in rows:
        writer.writerow(
            [
                b.id,
                b.reference_code,
                b.room_id,
                b.user_id,
                iso_utc(b.start_time),
                iso_utc(b.end_time),
                b.status,
                b.price_cents,
            ]
        )
    return buffer.getvalue()
