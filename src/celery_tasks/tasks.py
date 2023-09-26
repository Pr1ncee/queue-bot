from celery import Task

from celery_app import app
from settings.config import celery_config
from services.iis_service import IISService


class FetchTodayScheduleTask(Task):
    name = celery_config.TASK_NAME

    def run(self):
        group_id = 121701
        schedule = IISService.get_today_schedule(group_id)
        return schedule


app.tasks.register(FetchTodayScheduleTask())
