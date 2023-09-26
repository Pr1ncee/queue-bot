from telebot.types import CallbackQuery


def get_queue_name(call: CallbackQuery) -> str:
    queue_name = call.message.json.get("text", "").split("\n")[0]
    return queue_name
