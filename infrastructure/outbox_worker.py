import time
from confluent_kafka import Producer
from infrastructure.database import SessionLocal
from infrastructure.database_model import Outbox

producer = Producer({"bootstrap.servers": "broker:9092"})

while True:
    with SessionLocal() as session:
        events = session.query(Outbox).filter(Outbox.sent == False).all()
        for event in events:
            producer.produce(
                topic=event.topic,
                key=event.key.encode("utf-8"),
                value=event.payload.encode("utf-8")
            )
            event.sent = True
        producer.flush()
        session.commit()
    time.sleep(1)
