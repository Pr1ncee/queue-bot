# TODO: The message with a queue must be sent to every user in a subgroup!
# TODO: To make queue counter work properly!
import telebot
from telebot.types import CallbackQuery

from config import token
from db import db_reader, is_queue_created
from keyboards import reply_keyboard
from subgroup import subgroup, is_subgroup_chosen
from username import get_user_name
from queue_methods import queue_in, queue_out, queue_close, queue_create


bot = telebot.TeleBot(token[0])

queues = 1  # Counts queues
# Saves the id of the queue message with a specific subgroup
msgs_id = {}


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
    queue_data = db_reader('queueBot_db.pickle')
    user_data = get_user_name(call)

    user_name, sb = user_data
    queue_caption = f"Queue {queues} \nSubgroup {sb}"

    if flag == 'cr':
        if queues < 3:
            id_ = queue_create(bot, user_name, sb, id_chat, queue_caption)
            if id_[sb]:
                queues += 1
                msgs_id[sb] = id_[sb]
        else:
            bot.send_message(id_chat, "There are no more queues to be created!")
    elif flag == 'in':
        queue_in(bot, user_name, sb, id_chat, queue_caption, call_id, queue_data, msgs_id[sb])
    elif flag == 'out':
        queue_out(bot, user_name, sb, id_chat, queue_caption, msgs_id[sb])
    elif flag == 'cl':
        id_ = queue_close(bot, sb, id_chat, call_id, msgs_id[sb], call.message.text)
        if id_:
            queues -= 1
            msgs_id[sb] = id_[sb]


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Choose your subgroup at first: ", reply_markup=reply_keyboard())


@bot.message_handler(content_types=['text'])
def main(message):
    global queues

    user_name, sb = get_user_name(message)  # Gets an username
    queue_data = db_reader('queueBot_db.pickle')
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
        bot.answer_callback_query(call.id, "You have been put in the queue")
    elif call.data == "cb_out":
        queue_redirect(call, flag='out')
        bot.answer_callback_query(call.id, "You have been put out of the queue")
    elif call.data == "cb_close":
        queue_redirect(call, flag='cl')


bot.polling(timeout=60)
