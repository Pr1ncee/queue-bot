from random import choices

from httpx import ConnectError
from retry import retry
from telebot import TeleBot
from telebot.types import CallbackQuery

from db.redis_client import RedisClient
from enums.day_of_week_enum import DayOfWeekEnum
from enums.day_off_phrases import DayOffPhrases
from enums.response_enum import ResponseEnum
from exceptions.exceptions import FatalError, ClientError, ServerError
from keyboards.inline_keyboard import inline_keyboard
from services.iis_service import IISService
from settings.config import task_config
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
        return {"status": ResponseEnum.FAILED.value, "msg": "Вы уже встали в эту очередь!"}

    @classmethod
    def leave_queue(cls, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        if username in RedisClient.list_queue(queue_name=queue_name, msg_id=call.message.id):
            RedisClient.remove_from_queue(queue_name=queue_name, username=username, msg_id=call.message.id)

            msg = cls.update_queue(queue_name=queue_name, msg_id=call.message.id)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "Вы не находитесь в этой очереди!"}

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
    def make_queues(
            cls,
            bot: TeleBot,
            chat_id: int,
            group: int,
    ) -> None | bool:
        cls.delete_outdated_resources(bot=bot, chat_id=chat_id)

        try:
            res_schedule = cls.get_today_schedule(group=group)
        except (FatalError, ClientError, ServerError) as exc:
            bot.send_message(chat_id=chat_id, text="Фатальная ошибка! Завершаем работу...")
            raise FatalError(exc)

        if res_schedule[0] == DayOfWeekEnum.DAY_OFF.value:
            random_phrase = choices(DayOffPhrases.values(), weights=DayOffPhrases.get_weights(), k=1)[0]
            if random_phrase is None:
                return
            bot.send_message(chat_id=chat_id, text=random_phrase)
        else:
            classes = BotService.create_text_queues(schedule=res_schedule)
            classes = ["ОМИС"]
            for cl in classes:
                bot.send_message(chat_id=chat_id, text=cl, reply_markup=inline_keyboard())

    @classmethod
    @retry(exceptions=(ClientError, ServerError), tries=task_config.TASK_MAX_RETRY, delay=task_config.TASK_RETRY_DELAY)
    def get_today_schedule(cls, group: int) -> list:
        try:
            today_schedule = IISService.get_today_schedule(group=group)
            return today_schedule
        except ConnectError:
            raise FatalError(status_code=500, content={"message": "Fatal error! Exiting..."})

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

    @classmethod
    def add_active_chat(cls, chat_id: int) -> None:
        RedisClient.add_active_chat(chat_id=chat_id)

    @classmethod
    def list_active_chats(cls) -> list[str]:
        return RedisClient.list_active_chats()
