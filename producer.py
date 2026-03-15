import json
from confluent_kafka import Producer

p = Producer({
    "bootstrap.servers": "broker:9092"
})


def produce(data: dict):

    if data["op"] in ["c", "u"]:
        key = data["cinema"]["cinema_id"]
    else:
        key = data["cinema_id"]

    p.produce(
        topic="operations",
        value=json.dumps(data).encode("utf-8"),
        key=str(key).encode("utf-8")
    )

    p.flush()