"""The module is all about modifying the databases."""

from paths import db_queue, db_users
import pickle


def db_users_writer(username, subgroup_num=None, msg_id=None, chat_id=None,
                    db_filename=db_users):
    """
    Saves the information about a user
    Or updates the database with a new subgroup
    """

    data = db_reader(db_filename)
    with open(db_filename, 'wb') as db_:
        if username not in data:
            data.update({username: {'subgroup': subgroup_num, 'chat_id': chat_id, 'msg_id': msg_id}})
        elif subgroup_num:
            data[username].update({'subgroup': subgroup_num})
        elif msg_id:
            data[username].update({'msg_id': msg_id})
        elif chat_id:
            data[username].update({'chat_id': chat_id})

        pickle.dump(data, db_)


def db_queue_writer(sb, user_name=None, db_filename=db_queue):
    """
    Creates a specific queue if it isn't
    And pushes a user into the queue
    """

    queue_data = db_reader(db_filename)

    with open(db_filename, 'wb') as db:
        if user_name:
            users_data = db_reader(db_users)[user_name]
            queue_data[sb].update({user_name: users_data})
        else:
            data_for_recording = {sb: {}}
            queue_data.update(data_for_recording)

        pickle.dump(queue_data, db)


def db_queue_deleter(subgroup):
    """
    Deletes a created queue
    """

    queue_data = db_reader(db_queue)
    users_data = db_reader(db_users)

    for user in queue_data[subgroup]:
        users_data[user].update({'msg_id': None})
    queue_data.pop(subgroup)

    with open(db_users, 'wb') as db_u:
        pickle.dump(users_data, db_u)
    with open(db_queue, 'wb') as db_q:
        pickle.dump(queue_data, db_q)


def db_queue_out(username, subgroup):
    """
    Pulls a user out of the queue
    """

    queue_data = db_reader(db_queue)

    queue_data[subgroup].pop(username)
    with open(db_queue, 'wb') as db_q:
        pickle.dump(queue_data, db_q)


def db_reader(db_filename=db_users):
    """
    Returns the user's dict or the queue's dict
    """

    try:
        with open(db_filename, 'rb') as db:
            data = pickle.load(db)
    except EOFError:
        data = {}

    return data


def is_queue_created(subgroup):
    """
    Checks out whether the queue is created and returns the appropriate value
    """

    data = db_reader(db_queue)

    try:
        data[subgroup]
    except KeyError:
        return 0
    else:
        return 1


def db_del():
    data = db_reader(db_queue)
    with open(db_queue, 'wb') as db:
        data.clear()
        pickle.dump(data, db)
    #d = db_reader(db_users)
    #with open(db_users, 'wb')as db:
        #d.clear()
        #pickle.dump(d, db)


if __name__ == '__main__':
    db_del()
