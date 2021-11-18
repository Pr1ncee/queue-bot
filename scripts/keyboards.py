"""
This module includes two functions that add different keyboards to the bot.
All keyboards are built-in in pyTelegramBotAPI.
"""

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup,\
                          ReplyKeyboardMarkup, KeyboardButton


def reply_keyboard():
    btn_make_queue = KeyboardButton('Create a queue')
    btn_subgroup_1 = KeyboardButton('Subgroup 1')
    btn_subgroup_2 = KeyboardButton('Subgroup 2')

    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    reply_kb.row(btn_subgroup_1, btn_subgroup_2).add(btn_make_queue)
    return reply_kb


def inline_keyboard():
    btn_in_queue = InlineKeyboardButton("In the queue", callback_data="cb_in")
    btn_out_queue = InlineKeyboardButton("Out of the queue", callback_data="cb_out")
    btn_close_queue = InlineKeyboardButton("Close the queue", callback_data="cb_close")

    inline_kb = InlineKeyboardMarkup()
    inline_kb.row_width = 2
    inline_kb.add(btn_in_queue, btn_out_queue, btn_close_queue)
    return inline_kb
