from db import db_reader


def get_user_name(call):
    first_name = call.from_user.first_name
    last_name = call.from_user.last_name

    username = ' '.join([first_name, last_name])
    users_db = db_reader()
    user_subgroup = users_db[username]['subgroup']

    return username, user_subgroup
