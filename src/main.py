from datetime import datetime

import pytz
import telebot
import schedule

from src.enums.response_enum import ResponseEnum
from src.keyboards.inline_keyboard import inline_keyboard
from src.services.bot_service import BotService
from src.enums.callback_enum import CallbackEnum
from src.settings.config import general_config, task_config

bot = telebot.TeleBot(general_config.TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    """
    Entrypoint for starting the bot.
    Example of valid /start command:
    '/start 121701'

    :param message: command to start the bot
    """
    chat_id = message.chat.id

    active_chats = BotService.list_active_chats()
    if str(chat_id) in active_chats:
        return
    BotService.add_active_chat(chat_id=chat_id)

    try:
        group = int(message.text.split(" ")[-1])
    except ValueError:
        bot.send_message(chat_id=general_config.CHAT_ID, text="Введите действительную группу!")
    else:
        bot.send_message(chat_id=message.chat.id, text="Запускаем бота... ")
        bot.send_message(chat_id=message.chat.id, text="Скачиваем расписание... ")

        BotService.make_queues(
            bot=bot,
            chat_id=chat_id,
            group=group,
        )

        schedule.every().day.at(task_config.TASK_TIME_TO_REPEAT).do(
            BotService.make_queues,
            bot=bot,
            group=group,
            chat_id=chat_id,
        )
        while True:
            schedule.run_pending()


@bot.message_handler(commands=['ping'])
def ping_command(message):
    current_time = datetime.now(pytz.timezone(general_config.TIMEZONE))
    msg = f"Текущая дата: {current_time}"
    bot.send_message(chat_id=message.chat.id, text=msg)


@bot.message_handler(commands=['clear'])
def clear_command(message):
    BotService.clear_db()


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == CallbackEnum.JOIN_QUEUE.value:
        msg = BotService.join_queue(call=call)
        if msg["status"] == ResponseEnum.SUCCESS.value:
            bot.edit_message_text(
                text=msg["msg"],
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=inline_keyboard(),
            )
            bot.answer_callback_query(call.id, "Вы добавлены в очередь!")
        elif msg["status"] == ResponseEnum.FAILED.value:
            bot.answer_callback_query(call.id, msg["msg"])
    elif call.data == CallbackEnum.LEAVE_QUEUE.value:
        msg = BotService.leave_queue(call=call)
        if msg["status"] == ResponseEnum.SUCCESS.value:
            bot.edit_message_text(
                text=msg["msg"],
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=inline_keyboard(),
            )
            bot.answer_callback_query(call.id, "Вы удалены из очереди!")
        elif msg["status"] == ResponseEnum.FAILED.value:
            bot.answer_callback_query(call.id, msg["msg"])
    elif call.data == CallbackEnum.CLOSE_QUEUE.value and call.from_user.username == "Andrey_Strongin":
        BotService.close_queue(call=call)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.answer_callback_query(call.id, "Очередь закрылась!")


bot.polling(timeout=60)
