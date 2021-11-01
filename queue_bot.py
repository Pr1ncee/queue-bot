import telebot
from telebot.types import CallbackQuery

from config import token
from db import db_reader, db_queue_writer, db_queue_deleter, db_queue_out, is_queue_created
from keyboards import reply_keyboard, inline_keyboard
from subgroup import subgroup, is_subgroup_chosen
from username import get_user_name


bot = telebot.TeleBot(token[0])

queues = 1  # Counts queues
# Saves the id of the queue message with a specific subgroup
msg_id_1 = None
msg_id_2 = None


def queue_in(call):
    global queues, msg_id_1, msg_id_2

    queue_data = db_reader('queueBot_db.pickle')
    user_data = get_user_name(call)
    user_name, sb = user_data

    queue_caption = f"Queue {queues} \nSubgroup {sb}"

    id_chat = call.message.chat.id if type(call) == CallbackQuery else call.chat.id
    msg_id = msg_id_1 if sb == 1 else msg_id_2

    if not is_queue_created(1) or not (user_name in queue_data[1]) or \
       not is_queue_created(2) or not (user_name in queue_data[2]):
        db_queue_writer(user_name)

        if msg_id:
            put_in_queue(sb, id_chat, msg_id, queue_caption)
        else:
            sent_msg = bot.send_message(id_chat, queue_caption, reply_markup=inline_keyboard())
            if sb == 1:
                msg_id_1 = sent_msg.message_id
            elif sb == 2:
                msg_id_2 = sent_msg.message_id
            queue_in(call)
    else:
        bot.send_message(id_chat, "You are already in the queue!")


def queue_out(call):
    global msg_id_1, msg_id_2, queues

    username, sb = get_user_name(call)
    db_queue_out(username, sb)

    msg_id = msg_id_1 if sb == 1 else msg_id_2
    queue_caption = f"Queue {queues} \nSubgroup {sb}"
    id_chat = call.message.chat.id

    put_in_queue(sb, id_chat, msg_id, queue_caption)


def queue_close(call):
    global msg_id_2, msg_id_1, queues

    queue_sb = int(call.message.text[18])  # Gets a queue subgroup from the sent message
    sb = get_user_name(call)[1]

    if queue_sb == sb:
        db_queue_deleter(sb)
        bot.answer_callback_query(call.id, "The queue has been closed")
        bot.delete_message(call.message.chat.id, call.message.id)
        queues -= 1
        if sb == 1:
            msg_id_1 = 0
        else:
            msg_id_2 = 0
    else:
        bot.send_message(call.message.chat.id, "You can only close queues of your subgroup!")


def queue_list_creater(queue, sb):
    queue_list = []
    try:
        for index, user in enumerate(queue[sb]):
            queue_list.append((index + 1, user))
    except KeyError:
        pass

    return queue_list


def put_in_queue(sb, id_chat, msg_id, string_sample):
    queue_data = db_reader('queueBot_db.pickle')

    queue_list = queue_list_creater(queue_data, sb)  # The list with users in queue
    output = string_sample
    for user_data in queue_list:
        output += f"\n{user_data[0]}. {user_data[1]}"

    bot.edit_message_text(output, id_chat, msg_id, reply_markup=inline_keyboard())


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Choose your subgroup at first: ", reply_markup=reply_keyboard())


@bot.message_handler(content_types=['text'])
def main(message):
    global queues

    user = get_user_name(message)[0]  # Gets an username
    queue = db_reader('queueBot_db.pickle')
    # Checks out whether there are queues of both subgroups
    queue_subgroup_1 = queue_subgroup_2 = {}
    if 1 in queue:
        queue_subgroup_1 = queue[1]
    if 2 in queue:
        queue_subgroup_2 = queue[2]

    if message.text == "Create a queue":
        user, sb = get_user_name(message)
        is_sb = is_subgroup_chosen(user)

        # Can't create a queue with the same subgroup twice
        if is_queue_created(sb):
            bot.send_message(message.chat.id, "The queue with such subgroup already exists!")
        else:
            if not is_sb:
                bot.send_message(message.chat.id, "Choose your subgroup at first!")
            else:
                if queues < 3:
                    queue_in(message)
                    queues += 1
                else:
                    bot.send_message(message.chat.id, "There are no more queues to be created!")

    # If there is no queue created or user isn't in any of the subgroups
    # Then he can change the user's Subgroup
    elif not queue or user not in queue_subgroup_2 and user not in queue_subgroup_1:
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
        queue_in(call)
        bot.answer_callback_query(call.id, "You have been put in the queue")
    elif call.data == "cb_out":
        queue_out(call)
        bot.answer_callback_query(call.id, "You have been put out of the queue")
    elif call.data == "cb_close":
        queue_close(call)


bot.polling(timeout=60)
