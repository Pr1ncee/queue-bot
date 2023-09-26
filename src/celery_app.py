from celery import Celery
from celery.schedules import crontab

from settings.config import celery_config


app = Celery(
    'src',
    broker=celery_config.CELERY_BROKER_URL,
    backend=celery_config.CELERY_RESULT_BACKEND,
    include=["celery_tasks.tasks"]
)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch_today_schedule_every_midnight': {
        'task': 'celery_tasks.tasks.fetch_today_schedule',
        'schedule': 10,
    },
}
