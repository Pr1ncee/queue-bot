from datetime import timedelta

import telebot

from src.enums.response_enum import ResponseEnum
from src.keyboards.inline_keyboard import inline_keyboard
from src.services.bot_service import BotService
from src.enums.callback_enum import CallbackEnum
from src.settings.config import general_config, celery_config

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

    try:
        group = int(message.text.split(" ")[-1])
    except ValueError:
        bot.send_message(chat_id=general_config.CHAT_ID, text="Введите действительную группу!")
    else:
        bot.send_message(chat_id=message.chat.id, text="Запускаем бота... ")
        bot.send_message(chat_id=message.chat.id, text="Скачиваем расписание... ")

        response = BotService.get_today_schedule_and_create_queues(
            bot=bot,
            chat_id=chat_id,
            group=group,
            delay=timedelta(seconds=0)
        )
        if response is False:
            return
        while True:
            BotService.delete_outdated_resources(bot=bot, chat_id=chat_id)
            response = BotService.get_today_schedule_and_create_queues(
                bot=bot,
                chat_id=chat_id,
                group=group,
                delay=timedelta(hours=celery_config.TASK_RETRY_EVERY_HOURS)
            )
            if response is False:
                return


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
