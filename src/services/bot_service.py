from datetime import timedelta, datetime

from celery.utils.serialization import UnpickleableExceptionWrapper
from telebot import TeleBot
from telebot.types import CallbackQuery

from celery_tasks.tasks import get_today_schedule
from db.redis_client import RedisClient
from enums.response_enum import ResponseEnum
from exceptions.exceptions import FatalError
from keyboards.inline_keyboard import inline_keyboard
from utils.get_username_from_callback import get_username
from utils.get_queue_name_from_callback import get_queue_name


class BotService:
    @classmethod
    def join_queue(cls, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        if not (username in RedisClient.list_queue(queue_name=queue_name, msg_id=call.message.id)):
            queue_exists = RedisClient.queue_exists_in_chat_supervisor(
                queue_name=queue_name,
                msg_id=call.message.id
            )
            username, full_queue_name = RedisClient.join_queue(
                queue_name=queue_name,
                username=username,
                msg_id=call.message.id
            )

            if not queue_exists:
                RedisClient.add_queue_to_chat_supervisor(
                    chat_id=call.message.chat.id,
                    queue_name=full_queue_name
                )

            msg = cls.update_queue(queue_name=queue_name, msg_id=call.message.id)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "You are already in the queue!"}

    @classmethod
    def leave_queue(cls, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        if username in RedisClient.list_queue(queue_name=queue_name, msg_id=call.message.id):
            RedisClient.remove_from_queue(queue_name=queue_name, username=username, msg_id=call.message.id)

            msg = cls.update_queue(queue_name=queue_name, msg_id=call.message.id)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "You are not in the queue!"}

    @classmethod
    def close_queue(cls, call: CallbackQuery) -> None:
        queue_name = get_queue_name(call=call)
        RedisClient.clear_queue(queue_name=queue_name, msg_id=call.message.id)

    @classmethod
    def update_queue(cls, msg_id: int, queue_name: str) -> str:
        waiting_people = RedisClient.list_queue(queue_name=queue_name, msg_id=msg_id)

        msg = queue_name
        for index, user in enumerate(waiting_people):
            msg += f"\n{index + 1}. {user}"
        return msg

    @classmethod
    def clear_db(cls) -> None:
        RedisClient.clear_db()

    @classmethod
    def get_today_schedule_and_create_queues(
            cls,
            bot: TeleBot,
            chat_id: int,
            group: int,
            delay: timedelta
    ) -> None | bool:
        try:
            schedule = get_today_schedule.apply_async(args=(group,), eta=datetime.now() + delay)
        except (FatalError, UnpickleableExceptionWrapper):
            bot.send_message(chat_id=chat_id, text="Fatal error occurred! Exiting...")
            return False

        classes = BotService.create_text_queues(schedule=schedule.get())
        for cl in classes:
            bot.send_message(chat_id=chat_id, text=cl, reply_markup=inline_keyboard())

    @classmethod
    def create_text_queues(cls, schedule) -> list[str]:
        pairs = filter(lambda it: it['lessonTypeAbbrev'] == 'ЛР', schedule)

        queues = []
        for pair in pairs:
            subgroup = f'(Подгруппа {pair["numSubgroup"]})' if pair["numSubgroup"] else ''
            msg = f'{pair["subject"]} {subgroup}'
            queues.append(msg)
        return queues

    @classmethod
    def delete_outdated_resources(cls, bot: TeleBot, chat_id: int) -> None:
        queue_ids = RedisClient.delete_outdated_queues_in_chat(chat_id=chat_id)

        for msg_id in queue_ids:
            bot.delete_message(chat_id=chat_id, message_id=msg_id)
