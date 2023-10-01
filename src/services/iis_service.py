import httpx
import json

from enums.day_of_week_enum import DayOfWeekEnum
from exceptions.exceptions import ServerError, ClientError
from settings.config import general_config


class IISService:
    @classmethod
    def get_current_week(cls) -> int:
        with httpx.Client() as client:
            response = client.get(general_config.BASE_IIS_URL + "/current-week")
            cls.raise_for_status(status_code=response.status_code, response_text=response.text)

            content = response.content
            return int(content)

    @classmethod
    def get_schedule(cls, group: int) -> dict:
        with httpx.Client() as client:
            response = client.get(general_config.BASE_IIS_URL + f"?studentGroup={group}")
            cls.raise_for_status(status_code=response.status_code, response_text=response.text)

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
        if today_day.__str__() == "Воскресенье":
            return []

        lessons = [lesson for lesson in schedules[f"{today_day}"] if week in lesson['weekNumber']]
        return lessons

    @staticmethod
    def raise_for_status(status_code: int, response_text: str) -> None:
        if 400 <= status_code < 500:
            raise ClientError(status_code=status_code, content={"message": response_text})
        elif 500 <= status_code < 600:
            raise ServerError(status_code=status_code, content={"message": response_text})
