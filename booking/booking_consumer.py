import json
from confluent_kafka import Consumer
from infrastructure.database import SessionLocal
from infrastructure.database_model import ProcessedEvent
from booking.booking_saga import confirm_booking, cancel_booking

c = Consumer({
    "bootstrap.servers": "broker:9092",
    "group.id": "booking-service",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": "false"
})
c.subscribe(["seats"])

while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue

    try:
        event = json.loads(msg.value().decode("utf-8"))
        event_id = event["event_id"]
        booking_id = event["booking_id"]

        with SessionLocal() as session:
            if session.query(ProcessedEvent).filter(ProcessedEvent.event_id == event_id).first():
                c.commit(msg)
                continue

            if event["op"] == "SeatsReserved":
                confirm_booking(session, booking_id)
            elif event["op"] == "SeatsUnavailable":
                cancel_booking(session, booking_id)

            session.add(ProcessedEvent(event_id=event_id))
            session.commit()

    except Exception as e:
        print(f"Error: {e}")

    c.commit(msg)

c.close()
