from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

from enums.command_enum import CommandEnum


def reply_keyboard():
    btn_make_general_queue = KeyboardButton(CommandEnum.CREATE_QUEUE_FOR_ENTIRE_GROUP.value)

    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    reply_kb.row(btn_make_general_queue)
    return reply_kb
