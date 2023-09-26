from telebot.types import CallbackQuery


def get_username(call: CallbackQuery) -> str:
    first_name = call.from_user.first_name
    last_name = call.from_user.last_name
    username = first_name if not last_name else f"{first_name} {last_name}"
    return username
