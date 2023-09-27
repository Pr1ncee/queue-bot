from celery import shared_task

from services.iis_service import IISService


@shared_task
def get_today_schedule(group: int) -> list:
    today_schedule = IISService.get_today_schedule(group=group)
    return today_schedule
