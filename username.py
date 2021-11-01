from db import db_reader


def get_user_name(call):
    """
    Returns the username from the call
    And subgroup if it's chosen
    """
    first_name = call.from_user.first_name
    last_name = call.from_user.last_name

    username = ' '.join([first_name, last_name])
    users_db = db_reader()

    try:
        user_subgroup = users_db[username]['subgroup']
    except ValueError:
        user_subgroup = None

    return username, user_subgroup
