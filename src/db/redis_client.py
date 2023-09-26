import redis

from settings.config import redis_config

client = redis.Redis(
    host=redis_config.HOST,
    port=redis_config.PORT,
    encoding=redis_config.ENCODING,
    decode_responses=True
)


class RedisClient:
    @classmethod
    def join_queue(cls, queue_name: str, username: str) -> str:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}"
        client.rpush(full_queue_name, username)
        return username

    @classmethod
    def get_from_queue(cls, queue_name: str) -> str:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}"
        username = client.lpop(full_queue_name)
        return username

    @classmethod
    def remove_from_queue(cls, queue_name: str, username: str) -> str:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}"
        client.lrem(full_queue_name, 0, username)
        return username

    @classmethod
    def get_queue_len(cls, queue_name: str) -> int:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}"
        return client.llen(full_queue_name)

    @classmethod
    def list_queue(cls, queue_name: str,) -> list:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}"
        queue = client.lrange(full_queue_name, 0, -1)
        return queue

    @classmethod
    def list_existing_queues(cls) -> list[str]:
        matching_keys = client.keys(f"{redis_config.QUEUE_PREFIX}*")
        queue_names = [key[len(redis_config.QUEUE_PREFIX):] for key in matching_keys]
        return queue_names

    @classmethod
    def clear_queue(cls, queue_name: str) -> None:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}"
        client.delete(full_queue_name)

    @classmethod
    def clear_db(cls) -> None:
        client.flushall()

    @classmethod
    def ping(cls) -> bool:
        return client.ping()

    @classmethod
    def get_redis_version(cls) -> str:
        return client.info()["redis_version"]
