from db import db_users_writer, db_reader


def subgroup(message, subgroup_num):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = ' '.join([first_name, last_name])

    db_users_writer(username, subgroup_num)


def is_subgroup_chosen(username):
    db_filename = 'users.pickle'
    user_data = db_reader(db_filename)
    try:
        sb = user_data[username]['subgroup']
    except KeyError:
        return 0  # Returns 0 if subgroup is not chosen
    else:
        return sb  # Returns 1 if db calling was successful
