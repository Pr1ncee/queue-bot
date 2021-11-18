# TODO When there are several same usernames in the users database, they should be automatically numerated
"""
The main module.
Initialization of Telegram Bot connection.
Two functions to interact with pyTelegramBotAPI.
And the function that redirects all calls directed at operations with queues.
"""

from paths import db_queue

import telebot
from telebot.types import CallbackQuery

from config import token
from db import db_reader, is_queue_created, db_users_writer
from keyboards import reply_keyboard
from subgroup import subgroup, is_subgroup_chosen
from username import get_user_name
from queue_methods import queue_in, queue_out, queue_close, queue_create


bot = telebot.TeleBot(token[0])
queues = 0  # Counts queues


def queue_redirect(call, flag='cr'):
    """
    Redirects to the appropriate specific function according to the flag.

    :param call: different information from telebot about the chat
    :param flag: char means where to redirect the function call
    """

    global queues

    # Checks out whether it is a pyTelegramBotAPI type CallbackQuery or just a dict
    # Handling to the information between those 2 types is not the same
    id_chat = call.message.chat.id if type(call) == CallbackQuery else call.chat.id
    call_id = call.id
    user_data = get_user_name(call)
    user_name, sb = user_data

    queue_caption = "Queue {0} \nSubgroup {1}"

    if flag == 'cr':
        if queues < 3:
            if not is_queue_created(sb):
                queues += 1
                queue_create(bot, sb, queue_caption.format(queues, sb))
            else:
                bot.send_message(id_chat, f"The queue with the subgroup {sb} already exists!")
        else:
            bot.send_message(id_chat, "There are no more queues to be created!")
    elif flag == 'in':
        queue_in(bot, user_name, sb, queue_caption.format(queues, sb), call_id)
        bot.answer_callback_query(call.id, "You have been put in the queue")
    elif flag == 'out':
        queue_out(bot, user_name, sb, queue_caption.format(queues, sb))
        bot.answer_callback_query(call.id, "You have been put out of the queue")
    elif flag == 'cl':
        queue_sb = int(call.message.text[18])  # Gets a queue subgroup from the sent message
        if queue_sb == sb:
            queues -= 1
            queue_close(bot, sb)
        else:
            bot.send_message(id_chat, "You can only close queues of your subgroup!")


@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = get_user_name(message)[0]
    db_users_writer(user_name, chat_id=message.chat.id)
    bot.send_message(message.chat.id, "Choose your subgroup at first: ", reply_markup=reply_keyboard())


@bot.message_handler(content_types=['text'])
def main(message):
    user_name, sb = get_user_name(message)  # Gets an username
    queue_data = db_reader(db_queue)
    # Checks out whether there are queues of both subgroups
    queue_subgroup_1 = queue_subgroup_2 = {}
    if 1 in queue_data:
        queue_subgroup_1 = queue_data[1]
    if 2 in queue_data:
        queue_subgroup_2 = queue_data[2]

    if message.text == "Create a queue":
        is_sb = is_subgroup_chosen(user_name)

        # Can't create a queue with the same subgroup twice
        if is_queue_created(sb):
            bot.send_message(message.chat.id, "The queue with such subgroup already exists!")
        else:
            if not is_sb:
                bot.send_message(message.chat.id, "Choose your subgroup at first!")
            else:
                queue_redirect(message, flag='cr')

    # If there is no queue created or user isn't in any of the subgroups
    # Then he can change the user's Subgroup
    elif not queue_data or user_name not in queue_subgroup_2 and user_name not in queue_subgroup_1:
        if message.text == "Subgroup 1":
            subgroup(message, 1)
            bot.send_message(message.chat.id, f"Your subgroup is changed to 1")
        elif message.text == "Subgroup 2":
            subgroup(message, 2)
            bot.send_message(message.chat.id, f"Your subgroup is changed to 2")
    else:
        bot.send_message(message.chat.id, "You can't change subgroup being in the queue!")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_in":
        queue_redirect(call, flag='in')
    elif call.data == "cb_out":
        queue_redirect(call, flag='out')
    elif call.data == "cb_close":
        queue_redirect(call, flag='cl')


bot.polling(timeout=60)
