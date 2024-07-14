import pytest


@pytest.fixture
def test_username():
    return "Test User"


@pytest.fixture
def test_msg_id():
    return 1


@pytest.fixture
def fill_db(db_session, test_username, test_msg_id):
    from src.db.redis_client import RedisClient
    from src.settings.config import redis_config

    RedisClient.join_queue(
        queue_name=redis_config.TEST_QUEUE_NAME,
        username=test_username,
        msg_id=test_msg_id
    )
