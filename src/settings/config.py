import os

from dotenv import load_dotenv


load_dotenv()


class RedisConfig:
    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = os.getenv("REDIS_PORT", "6379")
    QUEUE_PREFIX = os.getenv("REDIS_QUEUE_PREFIX", "queue:")
    ACTIVE_CHATS_LIST = os.getenv("REDIS_ACTIVE_CHATS_LIST", "active_chats")
    TEST_QUEUE_NAME = os.getenv("REDIS_TEST_QUEUE_NAME", "queue:test_queue_bot_db")
    REDIS_CHAT_SUPERVISOR_PREFIX = os.getenv("REDIS_CHAT_SUPERVISOR_PREFIX", "chat-supervisor?{0}")
    ENCODING = "utf-8"


class CeleryConfig:
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "")
    TASK_REPEAT_EVERY_HOURS = int(os.getenv("CELERY_TASK_REPEAT_EVERY_HOURS", "24"))
    TASK_MAX_RETRY = 100
    TASK_RETRY_DELAY = 60  # Seconds


class GeneralConfig:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    CHAT_ID = None
    BASE_IIS_URL = "https://iis.bsuir.by/api/v1/schedule"
    TIMEZONE = 'Europe/Minsk'


redis_config = RedisConfig()
celery_config = CeleryConfig()
general_config = GeneralConfig()
