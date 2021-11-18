"""This module combines several functions that make operations with queues."""

from db import db_reader, db_queue_writer, db_queue_deleter, db_queue_out, db_users_writer
from keyboards import inline_keyboard
from paths import db_queue, db_users


def queue_create(bot_obj, sb, queue_caption):
    """
    Creates a queue if it isn't yet, or send the appropriate message.+

    :param bot_obj: Telebot object
    :param sb: a subgroup of an user
    :param queue_caption: the caption of queue message
    :return: if an queue is not created yet, it returns the dictionary with id of queue message
    """

    db_queue_writer(sb)

    users_data = db_reader()
    for user, data in users_data.items():
        if data['subgroup'] == sb:
            sent_msg = bot_obj.send_message(data['chat_id'],
                                            queue_caption,
                                            reply_markup=inline_keyboard())
            db_users_writer(username=user, msg_id=sent_msg.message_id)


def queue_in(bot_obj, user_name, sb, queue_caption, call_id):
    """
    Queues a user up.

    :param bot_obj: Telebot object
    :param user_name: username
    :param sb: a subgroup of a user
    :param queue_caption: the caption of queue message
    :param call_id: id of callback query
    """

    queue_data = db_reader(db_queue)

    if user_name not in queue_data[sb]:
        db_queue_writer(sb, user_name=user_name)
        join_queue(bot_obj, sb, queue_caption)
    else:
        bot_obj.answer_callback_query(call_id, "You are already in the queue!")


def queue_out(bot_obj, user_name, sb, queue_caption):
    """
    Pulls a user out of a queue.

    :param bot_obj: Telebot object
    :param user_name: username
    :param sb: a subgroup of a user
    :param queue_caption: the caption of queue message
    """

    try:
        db_queue_out(user_name, sb)
    except KeyError:
        pass
    else:
        join_queue(bot_obj, sb, queue_caption)


def queue_close(bot_obj, sb):
    """
    Queue closing is only available for a user with the same subgroup of a queue.
    If subgroups don't match the function send the appropriate message.

    :param bot_obj: Telebot object
    :param sb: a subgroup of a user
    :return: returns the dictionary with nullified id of subgroup's queue message
    """

    users_data = db_reader()
    for user, data in users_data.items():
        bot_obj.delete_message(data['chat_id'], data['msg_id'])
        bot_obj.send_message(data['chat_id'], "The queue has been closed")

        db_users_writer(user, msg_id=None)  # Message to edit set to None
    db_queue_deleter(sb)


def join_queue(bot_obj, sb, queue_caption):
    """
    Edits queue message

    :param bot_obj: Telebot object
    :param sb: a subgroup of a user
    :param queue_caption: the caption of queue message
    """
    queue_data = db_reader(db_queue)[sb]  # Gets info about certain queue in subgroup
    users_data = db_reader(db_users)
    queue_list = queue_list_creator(queue_data)  # The list with users in queue

    output = queue_caption
    for user_data in queue_list:
        output += f"\n{user_data[0]}. {user_data[1]}"
    for user, data in users_data.items():
        if data['msg_id']:
            bot_obj.edit_message_text(output, data['chat_id'], data['msg_id'], reply_markup=inline_keyboard())


def queue_list_creator(queue_data_sb):
    """
    :param queue_data_sb: information about existing queues in specific subgroup
    :return: returns users in a queue
    """

    queue_list = []
    try:
        for index, user in enumerate(queue_data_sb):
            queue_list.append((index+1, user))
    except KeyError:
        pass

    return queue_list
