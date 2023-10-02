from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

from enums.command_enum import CommandEnum


def reply_keyboard():
    btn_make_queue_for_subgroup = KeyboardButton(CommandEnum.CREATE_QUEUE_FOR_SUBGROUP.value)
    btn_make_general_queue = KeyboardButton(CommandEnum.CREATE_QUEUE_FOR_ENTIRE_GROUP.value)
    btn_subgroup_1 = KeyboardButton(CommandEnum.SUBGROUP_1.value)
    btn_subgroup_2 = KeyboardButton(CommandEnum.SUBGROUP_2.value)

    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    # reply_kb.row(btn_subgroup_1, btn_subgroup_2).add(btn_make_queue_for_subgroup).add(btn_make_general_queue)
    reply_kb.row(btn_make_general_queue)
    return reply_kb
