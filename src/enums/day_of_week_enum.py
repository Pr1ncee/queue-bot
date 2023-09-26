from datetime import datetime

from enums.base_enum import BaseEnum


class DayOfWeekEnum(BaseEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __str__(self):
        return ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][self.value]

    @staticmethod
    def get_today_day():
        current_day = datetime.today().weekday()
        return DayOfWeekEnum(current_day)
