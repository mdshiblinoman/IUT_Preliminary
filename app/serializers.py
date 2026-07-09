"""Shared response serialization for bookings."""
from .models import Booking
from .timeutils import iso_utc


def serialize_booking(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "reference_code": booking.reference_code,
        "room_id": booking.room_id,
        "user_id": booking.user_id,
        "start_time": iso_utc(booking.start_time),
        "end_time": iso_utc(booking.end_time),
        "status": booking.status,
        "price_cents": booking.price_cents,
        "created_at": iso_utc(booking.created_at),
    }
