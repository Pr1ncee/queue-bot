import pytz
from datetime import datetime

from enums.base_enum import BaseEnum
from settings.config import general_config


class DayOfWeekEnum(BaseEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    DAY_OFF = "Воскресенье"

    def __str__(self):
        return ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][self.value]

    @staticmethod
    def get_today_day():
        current_day = datetime.now(pytz.timezone(general_config.TIMEZONE)).weekday()
        return DayOfWeekEnum(current_day)
