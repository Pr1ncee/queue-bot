import os

from dotenv import load_dotenv


load_dotenv()


class RedisConfig:
    PASS = os.getenv("REDIS_PASS", "redis")
    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = os.getenv("REDIS_PORT", "6379")
    QUEUE_PREFIX = os.getenv("REDIS_QUEUE_PREFIX", "queue:")
    ACTIVE_CHATS_LIST = os.getenv("REDIS_ACTIVE_CHATS_LIST", "active_chats")
    TEST_QUEUE_NAME = os.getenv("REDIS_TEST_QUEUE_NAME", "queue:test_queue_bot_db")
    REDIS_CHAT_SUPERVISOR_PREFIX = os.getenv("REDIS_CHAT_SUPERVISOR_PREFIX", "chat-supervisor?{0}")
    REDIS_TTL = int(os.getenv("REDIS_TTL", "86400"))  # Seconds
    ENCODING = "utf-8"


class TaskConfig:
    TASK_MAX_RETRY = int(os.getenv("TASK_MAX_RETRY", "100"))
    TASK_RETRY_DELAY = int(os.getenv("TASK_RETRY_DELAY", "60"))  # Seconds
    TASK_TIME_TO_REPEAT = os.getenv("TASK_TIME_TO_REPEAT", "00:00")


class GeneralConfig:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BASE_IIS_URL = "https://iis.bsuir.by/api/v1/schedule"
    TIMEZONE = "Europe/Minsk"


redis_config = RedisConfig()
task_config = TaskConfig()
general_config = GeneralConfig()
