"""The module includes two functions that operate with subgroups."""

from paths import db_users

from db import db_users_writer, db_reader
from username import get_user_name


def subgroup(message, subgroup_num):
    """
    Updates the user's subgroup
    """

    username = get_user_name(message)[0]
    db_users_writer(username, subgroup_num)


def is_subgroup_chosen(username):
    """
    The function checks out whether a subgroup is chosen
    And returns the appropriate value
    """

    user_data = db_reader(db_users)

    try:
        sb = user_data[username]['subgroup']
    except KeyError:
        return 0
    else:
        return sb
