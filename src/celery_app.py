from celery import Celery

from settings.config import celery_config


app = Celery(
    'src',
    broker=celery_config.CELERY_BROKER_URL,
    backend=celery_config.CELERY_RESULT_BACKEND,
    include=["celery_tasks.tasks"]
)

app.autodiscover_tasks()
