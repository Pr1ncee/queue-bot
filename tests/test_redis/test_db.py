import pytest

from src.db.redis_client import RedisClient
from src.settings.config import redis_config


class TestRedisDB:
    def test_db_connection(self, db_session):
        is_connected = RedisClient.ping()

        assert is_connected is True

    def test_join_queue(self, db_session, test_username):
        response = RedisClient.join_queue(queue_name=redis_config.TEST_QUEUE_NAME, username=test_username)

        assert response == test_username
        assert RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME) == 1
        assert RedisClient.get_from_queue(queue_name=redis_config.TEST_QUEUE_NAME) == test_username

    def test_remove_from_queue(self, db_session, test_username, fill_db):
        response = RedisClient.remove_from_queue(queue_name=redis_config.TEST_QUEUE_NAME, username=test_username)

        assert response == test_username
        assert RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME) == 0
        assert RedisClient.list_queue(queue_name=redis_config.TEST_QUEUE_NAME) == []

    def test_get_queue_len_non_empty(self, db_session, fill_db):
        RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME)

        assert RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME) == 1

    def test_get_queue_len_empty(self, db_session):
        RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME)

        assert RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME) == 0

    def test_list_queue(self, db_session, test_username, fill_db):
        response = RedisClient.list_queue(queue_name=redis_config.TEST_QUEUE_NAME)

        assert isinstance(response, list)
        assert RedisClient.get_queue_len(queue_name=redis_config.TEST_QUEUE_NAME) == 1
        assert RedisClient.list_queue(queue_name=redis_config.TEST_QUEUE_NAME)[0] == test_username

    def test_list_existing_queues_non_empty(self, db_session, fill_db):
        existing_queues = RedisClient.list_existing_queues()

        assert isinstance(existing_queues, list)
        assert len(existing_queues) == 1
        assert existing_queues[0] == redis_config.TEST_QUEUE_NAME[len(redis_config.QUEUE_PREFIX):]

    def test_list_existing_queues_empty(self, db_session):
        existing_queues = RedisClient.list_existing_queues()

        assert isinstance(existing_queues, list)
        assert len(existing_queues) == 0