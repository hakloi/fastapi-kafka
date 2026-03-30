import json
import uuid
from confluent_kafka import Consumer
from infrastructure.database import SessionLocal
from infrastructure.database_model import Seat, Outbox, ProcessedEvent

c = Consumer({
    "bootstrap.servers": "broker:9092",
    "group.id": "seats-service",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": "false"
})
c.subscribe(["bookings"])


def _outbox(session, topic, key, payload):
    session.add(Outbox(
        id=str(uuid.uuid4()),
        topic=topic,
        key=key,
        payload=json.dumps(payload)
    ))


while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue

    try:
        event = json.loads(msg.value().decode("utf-8"))

        if event["op"] != "BookingRequested":
            c.commit(msg)
            continue

        event_id = event["event_id"]

        with SessionLocal() as session:
            if session.query(ProcessedEvent).filter(ProcessedEvent.event_id == event_id).first():
                c.commit(msg)
                continue

            seat = (session.query(Seat)
                    .filter(Seat.hall_number == event["hall_number"],
                            Seat.seat_number == event["seat_number"],
                            Seat.is_reserved == False)
                    .first())

            op = "SeatsReserved" if seat else "SeatsUnavailable"
            if seat:
                seat.is_reserved = True

            _outbox(session, "seats", event["booking_id"], {
                "event_id": str(uuid.uuid4()),
                "op": op,
                "booking_id": event["booking_id"]
            })
            session.add(ProcessedEvent(event_id=event_id))
            session.commit()

    except Exception as e:
        print(f"Error: {e}")

    c.commit(msg)

c.close()
