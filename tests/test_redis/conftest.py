import pytest


@pytest.fixture
def test_username():
    return "Test User"


@pytest.fixture
def fill_db(db_session, test_username):
    from src.db.redis_client import RedisClient
    from src.settings.config import redis_config

    RedisClient.join_queue(queue_name=redis_config.TEST_QUEUE_NAME, username=test_username)
