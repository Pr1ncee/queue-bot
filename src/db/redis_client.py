import re

import redis

from src.settings.config import redis_config

client = redis.Redis(
    host=redis_config.HOST,
    port=redis_config.PORT,
    encoding=redis_config.ENCODING,
    decode_responses=True,
    password=redis_config.PASS
)


class RedisClient:
    PATTERN_MSG_ID = r'\?(\d*)'
    PATTERN_QUEUE_NAME = fr'{redis_config.QUEUE_PREFIX}(.*?)\?'

    @classmethod
    def join_queue(cls, msg_id: int, queue_name: str, username: str) -> tuple[str, str]:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        client.rpush(full_queue_name, username)

        return username, full_queue_name

    @classmethod
    def get_from_queue(cls, msg_id: int, queue_name: str) -> str:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        username = client.lpop(full_queue_name)
        return username

    @classmethod
    def remove_from_queue(cls, msg_id: int, queue_name: str, username: str) -> str:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        client.lrem(full_queue_name, 0, username)
        return username

    @classmethod
    def get_queue_len(cls, msg_id: int, queue_name: str) -> int:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        return client.llen(full_queue_name)

    @classmethod
    def list_queue(cls, msg_id: int, queue_name: str,) -> list:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        queue = client.lrange(full_queue_name, 0, -1)
        return queue

    @classmethod
    def queue_exists_in_chat_supervisor(cls, msg_id: int, queue_name: str) -> bool:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        return client.exists(full_queue_name)

    @classmethod
    def list_existing_queues(cls) -> list[str]:
        matching_keys = client.keys(f"{redis_config.QUEUE_PREFIX}*")
        queue_names = [key[len(redis_config.QUEUE_PREFIX):] for key in matching_keys]
        return queue_names

    @classmethod
    def clear_queue(cls, msg_id: int, queue_name: str) -> None:
        full_queue_name = f"{redis_config.QUEUE_PREFIX}{queue_name}?{msg_id}"
        client.delete(full_queue_name)

    @classmethod
    def add_queue_to_chat_supervisor(cls, chat_id: int, queue_name: str) -> str:
        full_chat_supervisor_name = redis_config.REDIS_CHAT_SUPERVISOR_PREFIX.format(chat_id)
        client.rpush(full_chat_supervisor_name, queue_name)

        return full_chat_supervisor_name

    @classmethod
    def list_current_queues_in_chat(cls, chat_id: int) -> tuple[list[str], list[int]]:
        chat_supervisor_name = redis_config.REDIS_CHAT_SUPERVISOR_PREFIX.format(chat_id)
        queue_names = client.lrange(chat_supervisor_name, 0, -1)

        queues_msg_id = [re.search(cls.PATTERN_MSG_ID, s).group(1) for s in queue_names]
        queue_names = [re.search(cls.PATTERN_QUEUE_NAME, s).group(1) for s in queue_names]
        return queue_names, queues_msg_id

    @classmethod
    def delete_queue_from_chat_supervisor(cls, chat_id: int):
        pass

    @classmethod
    def delete_outdated_queues_in_chat(cls, chat_id: int) -> list[int | None]:
        queue_names, queue_ids = cls.list_current_queues_in_chat(chat_id)

        for queue_name, queue_id in zip(queue_names, queue_ids):
            cls.clear_queue(queue_name=queue_name, msg_id=queue_id)

        full_chat_supervisor_name = redis_config.REDIS_CHAT_SUPERVISOR_PREFIX.format(chat_id)
        client.delete(full_chat_supervisor_name)

        return queue_ids

    @classmethod
    def add_active_chat(cls, chat_id: int) -> None:
        client.rpush(redis_config.ACTIVE_CHATS_LIST, chat_id)

    @classmethod
    def list_active_chats(cls) -> list[str]:
        queue = client.lrange(redis_config.ACTIVE_CHATS_LIST, 0, -1)
        return queue

    @classmethod
    def clear_db(cls) -> None:
        client.flushall()

    @classmethod
    def ping(cls) -> bool:
        return client.ping()

    @classmethod
    def get_redis_version(cls) -> str:
        return client.info()["redis_version"]
