from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from enums.callback_enum import CallbackEnum


def inline_keyboard():
    btn_join_queue = InlineKeyboardButton("Встать в очередь", callback_data=CallbackEnum.JOIN_QUEUE.value)
    btn_leave_queue = InlineKeyboardButton("Выйти из очереди", callback_data=CallbackEnum.LEAVE_QUEUE.value)

    inline_kb = InlineKeyboardMarkup()
    inline_kb.row_width = 2
    inline_kb.add(btn_join_queue, btn_leave_queue)
    return inline_kb
