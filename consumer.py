import json
import uuid

from confluent_kafka import Consumer

from database import SessionLocal
from database_model import Cinema

c = Consumer({
    'bootstrap.servers': 'broker:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': 'false'
})

c.subscribe(['operations'])
session = SessionLocal()

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    try:
        object = json.loads(msg.value().decode('utf-8'))
        if object['op'] == 'c':
            db_cinema = Cinema(
                id=object['cinema']['cinema_id'],
                date=object['cinema']['date'],
                time=object['cinema']['time'],
                cinema=object['cinema']['cinema'],
                movie=object['cinema']['movie'],
                hall_number=object['cinema']['hall_number'],
                type=object['cinema']['type'],
            )
            session.add(db_cinema)
            session.commit()

        elif object['op'] == 'u':
            cinema = (session.query(Cinema)
                      .filter(Cinema.id == object['cinema']['cinema_id'])
                      .first())

            if not cinema:
                raise RuntimeError("Session not found")

            cinema.date = object['cinema']['date']
            cinema.time = object['cinema']['time']
            cinema.cinema = object['cinema']['cinema']
            cinema.movie = object['cinema']['movie']
            cinema.hall_number = object['cinema']['hall_number']
            cinema.type = object['cinema']['type']

            session.commit()


        elif object['op'] == 'd':
            cinema_id = object.get("cinema_id")

            db_cinema = session.query(Cinema).filter(Cinema.id == cinema_id).first()

            if not db_cinema:
                print(f"Cinema with id {cinema_id} not found, skipping delete")
                continue

            owner_id_from_msg = object.get("owner_id")
            if owner_id_from_msg and db_cinema.owner_id != owner_id_from_msg:
                print(f"Cannot delete cinema {cinema_id}: owner_id mismatch")
                continue

            session.delete(db_cinema)
            session.commit()
            print(f"Cinema with id {cinema_id} deleted successfully")

        else:
            raise RuntimeError('Not correct op: {}'.format(object.op))
    except Exception as e:
        print(e)
        pass

    print('Received message: {}'.format(msg.value().decode('utf-8')))
    c.commit(msg)

c.close()