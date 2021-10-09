import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup,\
                          ReplyKeyboardMarkup, KeyboardButton

from config import token


bot = telebot.TeleBot(token[0])

data_base = {}
queue_num = 0


def subgroup(message, subgroup_num, first_name, last_name):
    global data_base
    data_base[' '.join([first_name, last_name])] = {'subgroup': subgroup_num, 'queue_id': None}
    bot.send_message(message.chat.id, f"Your subgroup is changed to {subgroup_num}")


def queue_create(message):
    global queue_num
    queue_num += 1
    bot.send_message(message.chat.id, f"Queue №{queue_num}", reply_markup=inline_keyboard())


def queue_close(call):
    bot.edit_message_text("The queue was deleted", call.message.chat.id, call.message.id)


def reply_keyboard():
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_make_queue = KeyboardButton('Create a queue')
    btn_subgroup_1 = KeyboardButton('Subgroup 1')
    btn_subgroup_2 = KeyboardButton('Subgroup 2')

    reply_kb.add(btn_make_queue).row(btn_subgroup_1, btn_subgroup_2)
    return reply_kb


def inline_keyboard():
    btn_in_queue = InlineKeyboardButton("In the queue", callback_data="cb_in")
    btn_out_queue = InlineKeyboardButton("Out of the queue", callback_data="cb_out")
    btn_close_queue = InlineKeyboardButton("Close the queue", callback_data="cb_close")
    inline_kb = InlineKeyboardMarkup()
    inline_kb.row_width = 2

    inline_kb.add(btn_in_queue, btn_out_queue, btn_close_queue)
    return inline_kb


@bot.message_handler(content_types=['text'])
def main(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    if message.text == "Subgroup 1":
        subgroup(message, 1, first_name, last_name)
    elif message.text == "Subgroup 2":
        subgroup(message, 2, first_name, last_name)
    elif message.text == "Create a queue":
        queue_create(message)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Choose the option you want", reply_markup=reply_keyboard())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_in":
        bot.answer_callback_query(call.id, "You have been put in the queue")
    elif call.data == "cb_out":
        bot.answer_callback_query(call.id, "You have been put out of the queue")
    elif call.data == "cb_close":
        queue_close(call)
        bot.answer_callback_query(call.id, "You have closed the queue")


bot.polling(timeout=60)
