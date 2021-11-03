from pathlib import Path
import pickle


db_users = Path("..") / "databases"/ "users.pickle"
db_queue = Path("..") / "databases" / "queueBot_db.pickle"


def db_users_writer(username, subgroup_num=None,
                    db_filename=db_users):
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


def db_queue_writer(user, sb, db_filename=db_queue):
    """
    Creates a specific queue if it isn't
    And pushes a user into the queue
    """
    queue_data = db_reader(db_filename)

    with open(db_filename, 'wb') as db:
        if sb not in queue_data:
            data_for_recording = {sb: {}}
            queue_data.update(data_for_recording)
        else:
            if user not in queue_data:
                queue_data[sb] = {user: {'subgroup': sb}}

            else:
                pass

        pickle.dump(queue_data, db)


def db_queue_deleter(subgroup):
    """
    Deletes the created queue
    """
    db_filename = db_queue

    data = db_reader(db_filename)
    data.pop(subgroup)

    with open(db_filename, 'wb') as db:
        pickle.dump(data, db)


def db_queue_out(username, subgroup):
    """
    Pulls a user out of the queue
    """
    db_filename = db_queue

    data = db_reader(db_filename)
    data[subgroup].pop(username)

    with open(db_filename, 'wb') as db:
        pickle.dump(data, db)


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
    db_filename = db_queue

    data = db_reader(db_filename)
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


if __name__ == '__main__':
    db_del()