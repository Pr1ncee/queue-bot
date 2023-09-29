from httpx import ConnectError

from celery_app import app
from exceptions.exceptions import ClientError, ServerError, FatalError
from services.iis_service import IISService
from settings.config import celery_config


@app.task(bind=True, max_retries=celery_config.TASK_MAX_RETRY)
def get_today_schedule(self, group: int) -> list:
    try:
        today_schedule = IISService.get_today_schedule(group=group)
        return today_schedule
    except (ClientError, ServerError) as exc:
        self.retry(exc=exc, countdown=celery_config.TASK_RETRY_DELAY)
    except ConnectError:
        raise FatalError(status_code=500, content={"message": "Fatal error! Exiting..."})

