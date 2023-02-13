import logging

import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, CallbackQuery

from app.scripts.postgres_db.postgres_db_client import PostgresDBClient
from app.scripts.services.queue_bot_service import QueueBotService
import settings


logger = logging.getLogger(__name__)
token = settings.TELEGRAM_BOT_TOKEN
bot = telebot.TeleBot(token)
db = PostgresDBClient
qbs = QueueBotService
qbs.bot = bot


# TODO Implement the queue message output
@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """
    Bots entrypoint.
    If there is no active queue, start a queue with cleaning the database.
    """
    chat_id = message.chat.id
    # Must be compared exactly to bool, because uninitialized property returns <property object>
    if qbs.is_queue_started != True:
        PostgresDBClient.truncate_table()
        qbs._chat_id = chat_id
        qbs.is_queue_started = False
        qbs.start_queue(chat_id, message.from_user.username)
        logger.info('The queue has been started')
        return

    logger.info('The queue has been already started')
    bot.send_message(chat_id, "The queue has been already started!")


@bot.message_handler(commands=['sudo'])
def root_actions(message: Message) -> None:
    """
    A router for handling root commands.
    """
    chat_id = message.chat.id
    raw = message.text.split(' ')
    raw.remove('/sudo')
    try:
        password, command = raw
    except ValueError:
        logger.error('The user entered incorrect message format')
        bot.send_message(chat_id, 'Enter valid format!')
        return

    if password != settings.ROOT_PASS:
        logger.info('The password is incorrect')
        bot.send_message(chat_id, 'The password is incorrect!')
        return
    if command not in settings.COMMANDS:
        logger.info('The entered command not found')
        bot.send_message(chat_id, 'Enter valid command!')
        return

    qbs.close_queue(settings.ROOT_USERNAME)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery) -> None:
    """
    Handling info from inline keyboard.
    """
    username, chat_id = call.from_user.username, call.message.chat.id
    try:
        match call.data:
            case 'in':
                qbs.put_in_queue(username)
            case 'out':
                qbs.remove_from_queue(username)
            case 'close':
                qbs.close_queue(username)
    except ApiTelegramException as e:
        logger.error(e)


bot.polling(timeout=60)
