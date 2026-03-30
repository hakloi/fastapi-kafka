import uuid

from confluent_kafka import Consumer, Producer
import json

from redis_cinemas import RedisCinemas


class CinemaEventProducer:
    __p__ = Producer({
        "bootstrap.servers": "broker:9092"
    })

    @classmethod
    def produce(cls, data: dict):
        if data["op"] in ["c", "u"]:
            key = data["cinema"]["cinema_id"]
        else:
            key = data["cinema_id"]

        cls.__p__.produce(
            topic="operations",
            value=json.dumps(data).encode("utf-8"),
            key=str(key).encode("utf-8")
        )

        cls.__p__.flush()

class CinemaEventConsumer:

    @classmethod
    def _make_consumer(cls):
        import uuid as _uuid
        return Consumer({
            'bootstrap.servers': 'broker:9092',
            'group.id': f'fastapi-reader-{_uuid.uuid4()}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

    @classmethod
    def _read_all(cls):
        c = cls._make_consumer()
        events = []
        c.subscribe(['operations'])
        while not c.assignment():
            c.poll(0.1)
        while True:
            msg = c.poll(0.1)
            if msg is None:
                break
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                break
            try:
                events.append(json.loads(msg.value().decode('utf-8')))
            except Exception as e:
                print(e)
        c.close()
        return events

    @classmethod
    def load_all_events(cls):
        return cls._read_all()

    @classmethod
    def load_events(cls, cinema_id):
        events = []
        for event in cls._read_all():
            if event['op'] in ['c', 'u'] and event['cinema']['cinema_id'] == cinema_id:
                events.append(event)
            elif event['op'] == 'd' and event['cinema_id'] == cinema_id:
                events.append(event)
        return events

def send_event_to_kafka(event):
    event['id_event'] = str(uuid.uuid4())
    CinemaEventProducer.produce(event)

class CinemaEventSourcing:
    def __init__(self, cinema_id, date=None, time=None, cinema=None, movie=None, hall_number=None, type=None, owner_id=None):
        self.__cinema_id__ = cinema_id
        self.__date__ = date
        self.__time__ = time
        self.__cinema__ = cinema
        self.__movie__ = movie
        self.__hall_number__ = hall_number
        self.__type__ = type
        self.__owner__ = owner_id
        self.__version__ = -1
        self.__deleted__ = False
        self.__ids_event__ = set()

    def load(self):
        dump = RedisCinemas.getCinemaDump(self.__cinema_id__)
        if not dump is None:
            self.__date__ = dump['date']
            self.__time__ = dump['time']
            self.__cinema__ = dump['cinema']
            self.__movie__ = dump['movie']
            self.__hall_number__ = dump['hall_number']
            self.__type__ = dump['type']
            self.__version__ = dump['version']
            self.__deleted__ = dump['deleted']
            ids_event = set()
            for event in dump['ids_event']:
                ids_event.add(event)
            self.__ids_event__ = ids_event

        events = CinemaEventConsumer.load_events(self.__cinema_id__)
        for event in events:
            event_id = event.get('id_event')
            if event_id is None or event_id not in self.__ids_event__:
                if event['op'] == 'c':
                    cinema = event['cinema']
                    self.__date__ = cinema['date']
                    self.__time__ = cinema['time']
                    self.__cinema__ = cinema.get('cinema', cinema.get('cinema_id'))
                    self.__movie__ = cinema['movie']
                    self.__hall_number__ = cinema['hall_number']
                    self.__type__ = cinema['type']
                    self.__owner__ = cinema.get('owner_id')
                    self.__version__ = 0
                elif event['op'] == 'u':
                    cinema = event['cinema']
                    self.__date__ = cinema['date']
                    self.__time__ = cinema['time']
                    self.__cinema__ = cinema.get('cinema', cinema.get('cinema_id'))
                    self.__movie__ = cinema['movie']
                    self.__hall_number__ = cinema['hall_number']
                    self.__type__ = cinema['type']
                    self.__owner__ = cinema.get('owner_id')
                    self.__version__ += 1
                elif event['op'] == 'd':
                    self.__deleted__ = True
            if event_id:
                self.__ids_event__.add(event_id)

    def update(self, old_version, date, time, cinema, movie, hall_number, type):
        if self.__deleted__:
            raise RuntimeError("Cannot update deleted event")
        if self.__version__ != old_version:
            raise RuntimeError(f"Not correct version: {old_version}")
        if date: self.__date__ = date
        if time: self.__time__ = time
        if cinema: self.__cinema__ = cinema
        if movie: self.__movie__ = movie
        if hall_number: self.__hall_number__ = hall_number
        if type: self.__type__ = type
        cinema_data = {
            "cinema_id": self.__cinema_id__,
            "date": str(self.__date__),
            "time": str(self.__time__),
            "cinema": self.__cinema__,
            "movie": self.__movie__,
            "hall_number": self.__hall_number__,
            "type": self.__type__,
            "owner_id": self.__owner__
        }
        send_event_to_kafka({"op": "u","cinema": cinema_data})
        self.__version__ += 1

    def delete(self, old_version):
        if self.__deleted__:
            raise RuntimeError("Cannot delete deleted event")
        if self.__version__ != old_version:
            raise RuntimeError(f"Not correct version: {old_version}")
        self.__deleted__ = True
        send_event_to_kafka({
            "op": "d",
            "cinema_id": self.__cinema_id__
        })

    def create(self):
        cinema = {
            "cinema_id": self.__cinema_id__,
            "date": str(self.__date__),
            "time": str(self.__time__),
            "cinema": self.__cinema__,
            "movie": self.__movie__,
            "hall_number": self.__hall_number__,
            "type": self.__type__,
        }
        self.__version__ = 0
        send_event_to_kafka({"op": "c", "cinema": cinema})

    def is_deleted(self):
        return self.__deleted__
    
    def get_id(self):
        return self.__cinema_id__

    def get_date(self):
        return self.__date__

    def get_time(self):
        return self.__time__

    def get_cinema(self):
        return self.__cinema__

    def get_movie(self):
        return self.__movie__

    def get_hall_number(self):
        return self.__hall_number__

    def get_type(self):
        return self.__type__

    def get_version(self):
        return self.__version__

    def get_ids_event(self):
        return list(self.__ids_event__)

class CinemasEventSourcing:
    @staticmethod
    def load():
        events = CinemaEventConsumer.load_all_events()

        ids = set()
        for event in events:
            if event['op'] == 'c':
                ids.add(event['cinema']['cinema_id'])

        cinemas = [CinemaEventSourcing(
            cinema_id=id,
            date=None,
            time=None,
            cinema=None,
            movie=None,
            hall_number=None,
            type=None
        ) for id in ids]

        for cinema in cinemas:
            # друнгой метод , могу передать каждому объекту свои события с 220тстрочки
            cinema.load()

        return [c for c in cinemas if not c.is_deleted()]