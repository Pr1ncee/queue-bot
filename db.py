import pickle


def db_users_writer(username, subgroup_num=None,
                    db_filename='users.pickle'):
    """
    Saves the information about a user
    Or updates the database with a new subgroup
    """
    data = db_reader(db_filename)
    with open(db_filename, 'wb') as db_:
        if username not in data:
            data.update({username: {'subgroup': subgroup_num}})
        elif subgroup_num:
            data[username].update({'subgroup': subgroup_num})

        pickle.dump(data, db_)


def db_queue_writer(user, db_filename='queueBot_db.pickle'):
    """
    Creates a specific queue if it isn't
    And pushes a user into the queue
    """
    user_data = db_reader()
    queue_data = db_reader(db_filename)
    user_subgroup = user_data[user]['subgroup']

    with open(db_filename, 'wb') as db:
        if user not in queue_data:
            data_for_recording = {user_subgroup: {user: user_data[user]}}
            queue_data.update(data_for_recording)

            pickle.dump(queue_data, db)
        else:
            pass


def db_queue_deleter(subgroup):
    """
    Deletes the created queue
    """
    db_filename = 'queueBot_db.pickle'

    data = db_reader(db_filename)
    data.pop(subgroup)

    with open(db_filename, 'wb') as db:
        pickle.dump(data, db)


def db_queue_out(username, subgroup):
    """
    Pulls a user out of the queue
    """
    db_filename = 'queueBot_db.pickle'

    data = db_reader(db_filename)
    data[subgroup].pop(username)

    with open(db_filename, 'wb') as db:
        pickle.dump(data, db)


def db_reader(db_filename='users.pickle'):
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
    db_filename = 'queueBot_db.pickle'

    data = db_reader(db_filename)
    try:
        data[subgroup]
    except KeyError:
        return 0
    else:
        return 1


def db_del():
    data = db_reader('queueBot_db.pickle')
    with open('queueBot_db.pickle', 'wb') as db:
        data.clear()
        pickle.dump(data, db)
