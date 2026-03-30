import uuid
import json
from infrastructure.database import SessionLocal
from infrastructure.database_model import Booking, Outbox, BookingStatus


def _outbox(session, topic: str, key: str, payload: dict):
    session.add(Outbox(
        id=str(uuid.uuid4()),
        topic=topic,
        key=key,
        payload=json.dumps(payload)
    ))


def request_booking(cinema_id: str, hall_number: int, seat_number: int) -> str:
    booking_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())

    with SessionLocal() as session:
        session.add(Booking(
            id=booking_id,
            cinema_id=cinema_id,
            hall_number=hall_number,
            seat_number=seat_number,
            status=BookingStatus.PENDING
        ))
        _outbox(session, "bookings", booking_id, {
            "event_id": event_id,
            "op": "BookingRequested",
            "booking_id": booking_id,
            "cinema_id": cinema_id,
            "hall_number": hall_number,
            "seat_number": seat_number
        })
        session.commit()

    return booking_id


def confirm_booking(session, booking_id: str):
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.status = BookingStatus.CONFIRMED
    _outbox(session, "bookings", booking_id, {
        "event_id": str(uuid.uuid4()),
        "op": "BookingConfirmed",
        "booking_id": booking_id
    })


def cancel_booking(session, booking_id: str):
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.status = BookingStatus.CANCELLED
    _outbox(session, "bookings", booking_id, {
        "event_id": str(uuid.uuid4()),
        "op": "BookingCancelled",
        "booking_id": booking_id
    })
