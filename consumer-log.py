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

file = open("./log/log.txt", "w+")

while True:
    msg = c.poll()

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    try:
        object = json.loads(msg.value().decode('utf-8'))
        if object['op'] == 'c':
            file.write(f"Cinema created with id {object.cinema.cinema_id}\n")
        elif object['op'] == 'u':
            file.write(f"Cinema updated with id {object.cinema.cinema_id}\n")
        elif object['op'] == 'd':
            file.write(f"Cinema deleted with id {object.cinema.cinema_id}\n")
        else:
            raise RuntimeError('Not correct op: {}'.format(object.op))
        file.flush()
        c.commit(msg)
    finally:
        print("ok")

c.close()