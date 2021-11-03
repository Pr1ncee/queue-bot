from db import db_reader


def get_user_name(call):
    """
    Returns the username from the call
    And subgroup if it's chosen
    """
    users_db = db_reader()

    first_name = call.from_user.first_name
    last_name = call.from_user.last_name
    if not last_name:
        username = first_name
    else:
        username = ' '.join([first_name, last_name])

    try:
        user_subgroup = users_db[username]['subgroup']
    except KeyError:
        user_subgroup = None

    return username, user_subgroup
