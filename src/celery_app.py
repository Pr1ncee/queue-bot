from celery import Celery

from settings.config import celery_config, general_config


app = Celery(
    'src',
    broker=celery_config.CELERY_BROKER_URL,
    backend=celery_config.CELERY_RESULT_BACKEND,
    include=["celery_tasks.tasks"]
)

app.conf.timezone = general_config.TIMEZONE

app.autodiscover_tasks()
