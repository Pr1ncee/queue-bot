import pytest


@pytest.fixture
def db_session():
    import redis

    from src.settings.config import redis_config

    client = redis.Redis(
        host=redis_config.HOST,
        port=redis_config.PORT,
        encoding=redis_config.ENCODING,
        decode_responses=True
    )
    yield client

    client.delete(redis_config.TEST_QUEUE_NAME)
