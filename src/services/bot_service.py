import logging
from random import choices

from httpx import ConnectError
from retry import retry
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery

from src.db.mongo_client import MongoDBClient
from src.entities.active_chat import ActiveChatEntity
from src.entities.queue import QueueEntity
from src.enums.day_of_week_enum import DayOfWeekEnum
from src.enums.day_off_phrases import DayOffPhrases
from src.enums.response_enum import ResponseEnum
from src.exceptions.exceptions import FatalError, ClientError, ServerError
from src.keyboards.inline_keyboard import inline_keyboard
from src.services.iis_service import IISService
from src.settings.config import task_config
from src.utils.get_username_from_callback import get_username
from src.utils.get_queue_name_from_callback import get_queue_name

logger = logging.getLogger(__name__)


class BotService:
    def __init__(self):
        self.mongo_client = MongoDBClient()

    def join_queue(self, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        msg_id = call.message.id
        if not self.mongo_client.is_already_in_queue(username=username, queue_name=queue_name, msg_id=msg_id):
            people_to_add = [username]
            if not self.mongo_client.get_queue(name=queue_name, msg_id=msg_id):
                queue_entity = QueueEntity(
                    chat_id=call.message.chat.id,
                    msg_id=msg_id,
                    name=queue_name,
                    people=people_to_add
                )
                self.mongo_client.create_queue(queue_entity=queue_entity)
            self.mongo_client.add_people_to_queue(msg_id=msg_id, people=people_to_add)

            msg = self.update_queue(queue_name=queue_name, msg_id=msg_id)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "Вы уже встали в эту очередь!"}

    def leave_queue(self, call: CallbackQuery) -> dict[str, str]:
        username = get_username(call=call)
        queue_name = get_queue_name(call=call)
        msg_id = call.message.id
        if self.mongo_client.is_already_in_queue(username=username, name=queue_name, msg_id=msg_id):
            self.mongo_client.remove_from_queue(username=username, msg_id=msg_id)

            msg = self.update_queue(queue_name=queue_name, msg_id=msg_id)
            return {"status": ResponseEnum.SUCCESS.value, "msg": msg}
        return {"status": ResponseEnum.FAILED.value, "msg": "Вы не находитесь в этой очереди!"}

    def close_queue(self, call: CallbackQuery) -> None:
        queue_name = get_queue_name(call=call)
        self.mongo_client.delete_queue(name=queue_name, msg_id=call.message.id, chat_id=call.message.chat.id)

    def update_queue(self, msg_id: int, queue_name: str) -> str:
        waiting_people = self.mongo_client.get_queue(name=queue_name, msg_id=msg_id)

        if waiting_people:
            msg = queue_name
            for index, user in enumerate(waiting_people.people):
                msg += f"\n{index + 1}. {user}"
            return msg

    def clear_db(self) -> None:
        self.mongo_client.delete_all_queues()

    def make_queues(
            self,
            bot: TeleBot,
            chat_id: int,
            group: int,
    ) -> None | bool:
        try:
            self.delete_outdated_resources(bot=bot, chat_id=chat_id)

            try:
                res_schedule = self.get_today_schedule(group=group)
            except (FatalError, ClientError, ServerError):
                return False

            if res_schedule[0] == DayOfWeekEnum.DAY_OFF.value:
                random_phrase = choices(DayOffPhrases.values(), weights=DayOffPhrases.get_weights(), k=1)[0]
                if random_phrase is None:
                    return
                bot.send_message(chat_id=chat_id, text=random_phrase)
            else:
                classes = self.create_text_queues(schedule=res_schedule)
                for cl in classes:
                    bot.send_message(chat_id=chat_id, text=cl, reply_markup=inline_keyboard())
        except ApiTelegramException:
            pass

    @retry(exceptions=(ClientError, ServerError), tries=task_config.TASK_MAX_RETRY, delay=task_config.TASK_RETRY_DELAY)
    def get_today_schedule(self, group: int) -> list:
        try:
            today_schedule = IISService.get_today_schedule(group=group)
            logger.info(f"Today schedule has been updated. Current schedule: {today_schedule}")
            return today_schedule
        except ConnectError:
            logger.error("Couldn't get a schedule. An error occurred. Exiting...")
            raise FatalError(status_code=500, content={"message": "Fatal error! Exiting..."})

    def create_text_queues(self, schedule) -> list[str]:
        pairs = filter(lambda it: it['lessonTypeAbbrev'] == 'ЛР', schedule)

        queues = []
        for pair in pairs:
            subgroup = f'(Подгруппа {pair["numSubgroup"]})' if pair["numSubgroup"] else ''
            msg = f'{pair["subject"]} {subgroup}'
            queues.append(msg)
        return queues

    def delete_outdated_resources(self, bot: TeleBot, chat_id: int) -> None:
        queue_ids = self.mongo_client.delete_outdated_queues(chat_id=chat_id)

        for msg_id in queue_ids:
            bot.delete_message(chat_id=chat_id, message_id=msg_id)

    def add_active_chat(self, chat_id: int) -> None:
        self.mongo_client.add_active_chat(active_chat=ActiveChatEntity(active_chats=[chat_id]))

    def is_chat_active(self, chat_id: int) -> bool:
        return self.mongo_client.is_chat_active(chat_id=chat_id)
