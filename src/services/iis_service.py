import httpx
import json

from enums.day_of_week_enum import DayOfWeekEnum
from settings.config import general_config


class IISService:
    @classmethod
    def get_current_week(cls) -> int:
        with httpx.Client() as client:
            response = client.get(general_config.BASE_IIS_URL + "/current-week")
            if response.status_code != 200:
                return 0
            content = response.content
            return int(content)

    @classmethod
    def get_schedule(cls, group: int) -> dict:
        with httpx.Client() as client:
            response = client.get(general_config.BASE_IIS_URL + f"?studentGroup={group}")
            if response.status_code != 200:
                return {}
            content = response.content
            return json.loads(content)

    @classmethod
    def get_today_schedule(cls, group: int) -> list:
        full = IISService.get_schedule(group=group)
        week = IISService.get_current_week()

        schedules = full.get("schedules", {})
        if not schedules:
            return []

        today_day = DayOfWeekEnum.get_today_day()

        lessons = [lesson for lesson in schedules[f"{today_day}"] if week in lesson['weekNumber']]
        return lessons
