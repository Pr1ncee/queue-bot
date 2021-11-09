"""This module combines several functions that make operations with queues."""

from pathlib import Path

from db import db_reader, db_queue_writer, db_queue_deleter, db_queue_out
from keyboards import inline_keyboard


def queue_create(bot_obj, user_name, sb, id_chat, queue_caption,):
    """
    Creates a queue if it isn't yet, or send the appropriate message.

    :param bot_obj: Telebot object
    :param user_name: username
    :param sb: a subgroup of an user
    :param id_chat: chat id where bot is connected to
    :param queue_caption: the caption of queue message
    :return: if an queue is not created yet, it returns the dictionary with id of queue message
    """

    db_queue_writer(user_name, sb)

    msg_id = {}
    sent_msg = bot_obj.send_message(id_chat, queue_caption, reply_markup=inline_keyboard())
    msg_id[sb] = sent_msg.message_id

    return msg_id


def queue_in(bot_obj, user_name, sb, id_chat, queue_caption, call_id, queue_data, msg_id):
    """
    Queues a user up.

    :param bot_obj: Telebot object
    :param user_name: username
    :param sb: a subgroup of a user
    :param id_chat: chat id where bot is connected to
    :param queue_caption: the caption of queue message
    :param call_id: id of callback query
    :param queue_data: information about existing queues
    :param msg_id: id of queue message
    """

    if user_name not in queue_data[sb]:
        db_queue_writer(user_name, sb)
        join_queue(bot_obj, sb, id_chat, msg_id, queue_caption)
    else:
        bot_obj.answer_callback_query(call_id, "You are already in the queue!")


def queue_out(bot_obj, user_name, sb, id_chat, queue_caption, msg_id):
    """
    Pulls a user out of a queue.

    :param bot_obj: Telebot object
    :param user_name: username
    :param sb: a subgroup of a user
    :param id_chat: chat id where bot is connected to
    :param queue_caption: the caption of queue message
    :param msg_id: id of queue message
    """

    try:
        db_queue_out(user_name, sb)
    except KeyError:
        pass
    else:
        join_queue(bot_obj, sb, id_chat, msg_id, queue_caption)


def queue_close(bot_obj, sb, id_chat, call_id, msg_id):
    """
    Queue closing is only available for a user with the same subgroup of a queue.
    If subgroups don't match the function send the appropriate message.

    :param bot_obj: Telebot object
    :param sb: a subgroup of a user
    :param id_chat: chat id where bot is connected to
    :param call_id: id of callback query
    :param msg_id: id of queue message
    :return: returns the dictionary with nullified id of subgroup's queue message
    """

    msg__id = {}
    db_queue_deleter(sb)
    bot_obj.answer_callback_query(call_id, "The queue has been closed")
    bot_obj.delete_message(id_chat, msg_id)
    msg__id[sb] = None

    return msg__id


def join_queue(bot_obj, sb, id_chat, msg_id, queue_caption):
    """
    Edits queue message

    :param bot_obj: Telebot object
    :param sb: a subgroup of a user
    :param id_chat: chat id where bot is connected to
    :param msg_id: id of queue message
    :param queue_caption: the caption of queue message
    """

    db_filename = Path("..") / "databases" / "queueBot_db.pickle"
    queue_data = db_reader(db_filename)
    queue_list = queue_list_creator(queue_data[sb])  # The list with users in queue
    output = queue_caption
    for user_data in queue_list:
        output += f"\n{user_data[0]}. {user_data[1]}"

    bot_obj.edit_message_text(output, id_chat, msg_id, reply_markup=inline_keyboard())


def queue_list_creator(queue_data_sb):
    """
    :param queue_data_sb: information about existing queues in specific subgroup
    :return: returns users in a queue
    """

    queue_list = []
    try:
        for index, user in enumerate(queue_data_sb):
            queue_list.append((index + 1, user))
    except KeyError:
        pass

    return queue_list
