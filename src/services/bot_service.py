from datetime import datetime, timedelta

from telebot.types import CallbackQuery

from celery_tasks.tasks import get_today_schedule
from db.redis_client import RedisClient
from enums.response_enum import ResponseEnum
from utils.get_username_from_callback import get_username
from utils.get_queue_name_from_callback import get_queue_name


class BotService:
    queue_caption = "Queue {0}"

    @classmethod
    def join_queue(cls, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        if not (username in RedisClient.list_queue(queue_name=queue_name)):
            RedisClient.join_queue(queue_name=queue_name, username=username)

            msg = cls.update_queue(queue_name=queue_name)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "You are already in the queue!"}

    @classmethod
    def leave_queue(cls, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        if username in RedisClient.list_queue(queue_name=queue_name):
            RedisClient.remove_from_queue(queue_name=queue_name, username=username)

            msg = cls.update_queue(queue_name=queue_name)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "You are not in the queue!"}

    @classmethod
    def close_queue(cls, call: CallbackQuery) -> None:
        queue_name = get_queue_name(call=call)
        RedisClient.clear_queue(queue_name=queue_name)

    @classmethod
    def update_queue(cls, queue_name: str) -> str:
        waiting_people = RedisClient.list_queue(queue_name=queue_name)

        msg = queue_name
        for index, user in enumerate(waiting_people):
            msg += f"\n{index + 1}. {user}"
        return msg

    @classmethod
    def clear_db(cls) -> None:
        RedisClient.clear_db()

    @classmethod
    def get_today_schedule_and_create_queues(cls):
        schedule = get_today_schedule.apply_async(args=(121701,), eta=datetime.now() + timedelta(hours=24))

        classes = BotService.create_queues(schedule=schedule.get())
        return classes

    @classmethod
    def create_queues(cls, schedule) -> list[str]:
        pairs = filter(lambda it: it['lessonTypeAbbrev'] == 'ЛР', schedule)

        queues = []
        for pair in pairs:
            msg = (f'{pair["subject"]}\n'
                   f'{"Подгруппа " + str(pair["numSubgroup"]) if pair["numSubgroup"] != 0 else ""}')
            queues.append(msg)
        return queues
