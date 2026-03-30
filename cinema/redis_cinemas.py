import redis
import json


class RedisCinemas:
    redisObject = redis.from_url("redis://redis:6379")

    @classmethod
    def getCinemaDump(cls, id):
        res = cls.redisObject.get(id)
        if res is None:
            return None
        return json.loads(res)
