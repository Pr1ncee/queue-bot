import pickle

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup,\
                          ReplyKeyboardMarkup, KeyboardButton

from config import token


bot = telebot.TeleBot(token[0])

data_base = {}
queue_num = 0


def db_writer(username, subgroup_num=None,
              queue_id=None, queue_is_created=False,
              flag=None, db_filename='queueBot_db.pickle'):
    with open(db_filename, 'rb') as db:
        try:
            data = pickle.load(db)
        except EOFError:
            data = {}

    with open(db_filename, 'wb') as db_:
        if username not in data:
            data.update({username: {'subgroup': subgroup_num, 'queue_id': queue_id,
                                    'queue_is_created': queue_is_created}})
            pickle.dump(data, db_)
        elif subgroup_num:
            data[username].update({'subgroup': subgroup_num})
        elif queue_id:
            data[username].update({'queue_id': queue_id, 'queue_is_created': queue_is_created})
        elif flag == 'close':
            data[username].update({'queue_is_created': queue_is_created})

        pickle.dump(data, db_)


def db_reader(db_filename='queueBot_db.pickle'):
    with open(db_filename, 'rb') as db:
        user_data = pickle.load(db)

    return user_data


def subgroup(message, subgroup_num):
    global data_base

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = ' '.join([first_name, last_name])

    db_writer(username, subgroup_num)
    with open('queueBot_db.pickle', 'rb') as db:
        data = pickle.load(db)
        print(data[username])
    bot.send_message(message.chat.id, f"Your subgroup is changed to {subgroup_num}")


def queue_create(message):
    global queue_num

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = ' '.join([first_name, last_name])

    user_data = db_reader()

    try:
        user_data[username]['subgroup']
    except KeyError:
        bot.send_message(message.chat.id, "Choose your subgroup at first!")
    else:
        queue_num += 1

        if not user_data[username]['queue_is_created']:
            db_writer(username, queue_id=queue_num, queue_is_created=True)
            bot.send_message(message.chat.id, f"Queue №{queue_num}", reply_markup=inline_keyboard())
        else:
            bot.send_message(message.chat.id, "You have already created the queue!")


def queue_close(call):
    first_name = call.from_user.first_name
    last_name = call.from_user.last_name
    username = ' '.join([first_name, last_name])

    db_writer(username, flag='close')

    bot.edit_message_text("The queue was deleted", call.message.chat.id, call.message.id)


def reply_keyboard():
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    btn_make_queue = KeyboardButton('Create a queue')
    btn_subgroup_1 = KeyboardButton('Subgroup 1')
    btn_subgroup_2 = KeyboardButton('Subgroup 2')

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


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Choose the subgroup at first: ", reply_markup=reply_keyboard())


@bot.message_handler(content_types=['text'])
def main(message):
    if message.text == "Subgroup 1":
        subgroup(message, 1)
    elif message.text == "Subgroup 2":
        subgroup(message, 2)
    elif message.text == "Create a queue":
        queue_create(message)


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
