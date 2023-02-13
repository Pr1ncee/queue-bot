import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import IntegrityError

from app.scripts.exceptions.base_exceptions import PermissionDenied
from app.scripts.postgres_db.postgres_db_client import PostgresDBClient


logger = logging.getLogger(__name__)


class QueueBotService:
    """
    A layer between a bot and a database. Make sure the communication is safe & efficient.
    """
    __is_queue = False
    _chat_id = None
    _msg_id = None
    bot = None  # Connection object, think about better class-based solution

    @property
    def is_queue_started(self):
        return self.__is_queue

    @is_queue_started.setter
    def is_queue_started(self, value: bool):
        self.__is_queue = value

    @classmethod
    def send_queue(cls):
        """
        Send the current state of the queue.
        Firstly fetching the users then send the message with the state.
        """
        try:
            users = PostgresDBClient.get_users()
        except IndexError:
            logger.error("The table is clean, can't get the users")
            return

        queue_order = ''
        if not users:
            queue_order = 'The queue is emtpy!'
        else:
            for user in users:
                queue_order += f'\n{user[0]}. {user[1]}'

        if not cls._msg_id:
            msg = cls.bot.send_message(cls._chat_id, queue_order, reply_markup=cls.inline_keyboard())
            cls._msg_id = msg.id
            return

        cls.bot.edit_message_text(queue_order, cls._chat_id, cls._msg_id, reply_markup=cls.inline_keyboard())

    @classmethod
    def start_queue(cls, chat_id: int, user: str) -> None:
        """
        Start the queue with appropriate checks;
        :param chat_id: working chat id;
        :param user: username of creator, creator is able to close the queue without the root command;
        :return: None.
        """
        if not cls.is_queue_started:
            try:
                PostgresDBClient.init_table()
                cls.put_in_queue(user, True)
                cls.is_queue_started = True
                cls.bot.send_message(chat_id, "The queue has been successfully started")
            except IntegrityError:
                logger.error("The queue is already started!")
                cls.bot.send_message(chat_id, "You have already been started the queue!")
            return

        cls.bot.send_message(chat_id, "The queue has been already started")

    @classmethod
    def close_queue(cls, username: str) -> None:
        """
        Close the active queue with appropriate checks.
        """
        if cls.is_queue_started:
            try:
                is_creator = PostgresDBClient.get_user(username)[-1]
                if not is_creator:
                    raise PermissionDenied()
            except (Exception, PermissionDenied):
                logger.error('Permission denied to close the queue')
                cls.bot.send_message(cls._chat_id, 'You have no permission to do this action')
            else:
                PostgresDBClient.truncate_table()  # Clean the database
                logger.info('The queue has been closed')

                cls.bot.delete_message(cls._chat_id, cls._msg_id)
                cls.is_queue_started = False
                cls._msg_id = None
                cls.bot.send_message(cls._chat_id, 'The queue has been closed')
            return

        logger.error('There is no currently opened queue')
        cls.bot.send_message(cls._chat_id, 'There is no currently opened queue!')

    @classmethod
    def put_in_queue(cls, username: str, is_creator: bool = False):
        try:
            user = {'username': username, 'is_creator': is_creator}
            PostgresDBClient.insert_user_into_db(user)
            cls.send_queue()
        except IntegrityError:
            logger.error('The user has been already in queue')

    @classmethod
    def remove_from_queue(cls, username: str):
        PostgresDBClient.remove_user_from_db(username)
        cls.send_queue()

    @staticmethod
    def get_initials(request):
        username = request.from_user.username
        if not username:
            first_name = request.from_user.first_name
            last_name = request.from_user.last_name
            user = f'{first_name} {last_name}' if last_name else first_name
            return user
        return username

    @staticmethod
    def inline_keyboard():
        keyboard = [
            [InlineKeyboardButton('In', callback_data='in')],
            [InlineKeyboardButton('Out', callback_data='out')],
            [InlineKeyboardButton('Close', callback_data='close')]
        ]
        return InlineKeyboardMarkup(keyboard)
