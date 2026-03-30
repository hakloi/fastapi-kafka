import redis
import json
from cinema.cinema_es import CinemasEventSourcing, CinemaEventSourcing


def get_state(cinema: CinemaEventSourcing):
    return {
        'version': cinema.get_version(),
        'cinema_id': cinema.get_id(),
        'date': str(cinema.get_date()),
        'time': str(cinema.get_time()),
        'cinema': cinema.get_cinema(),
        'movie': cinema.get_movie(),
        'hall_number': cinema.get_hall_number(),
        'type': cinema.get_type(),
        'deleted': cinema.is_deleted(),
        'ids_event': cinema.get_ids_event(),
    }


redisObject = redis.from_url("redis://redis:6379")
cinemas = CinemasEventSourcing.load()

for cinema in cinemas:
    redisObject.set(cinema.get_id(), json.dumps(get_state(cinema)))
