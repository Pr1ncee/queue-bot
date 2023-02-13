import sqlalchemy as sqla
from sqlalchemy import table, column
from sqlalchemy.engine.cursor import LegacyCursorResult
from sqlalchemy.sql.dml import DMLState

from app.scripts.postgres_db.base_client import ClientMeta
from app.scripts import settings


class PostgresDBClient(metaclass=ClientMeta):
    _client = None
    _connection = None
    _queue_name = settings.QUEUE_NAME
    _table_schema = table(
                _queue_name,
                column('username'),
                column('is_creator')
    )

    @classmethod
    def init_table(cls) -> None:
        """
        Create the table if it doesn't exist.
        """
        root_creds = {'username': 'root', 'is_creator': True}
        cls.client.execute(f"CREATE TABLE IF NOT EXISTS {cls._queue_name} "
                           "(id SERIAL PRIMARY KEY, username INTEGER UNIQUE, is_creator BOOLEAN NOT NULL)")
        cls.insert_user_into_db(root_creds)

    @classmethod
    def insert_user_into_db(cls, user: dict) -> None:
        """
        Insert the user in the queue table
        :param user: dictionary with information about the user
        :return: None
        """
        query = sqla.insert(cls._table_schema).values(username=user['username'], is_creator=user['is_creator'])
        cls.execute_query(query)

    @classmethod
    def remove_user_from_db(cls, username: str) -> None:
        """
        Remove the user from the queue table
        :param username: unique user
        :return: None.
        """
        query = sqla.delete(cls._table_schema).where(cls._table_schema.c.username == username)
        cls.execute_query(query)

    @classmethod
    def scan_table(cls):
        query = sqla.text(f"SELECT * FROM {cls._queue_name}")
        return cls.client.execute(query).fetchall()

    @classmethod
    def get_user(cls, username: str):
        """
        Take telegram user id and returns corresponding record from the database.
        Return the tuple in form of (username: str, is_creator: bool,)
        :param username: telegram username to be fetched by
        :return: record from the database.
        """
        query = sqla.select([cls._table_schema]).where(cls._table_schema.c.username == username)
        return cls.execute_query(query).fetchall()[0]

    @classmethod
    def truncate_table(cls) -> None:
        query = sqla.text(f"TRUNCATE TABLE {cls._queue_name}")
        cls.execute_query(query)

    @classmethod
    def execute_query(cls, query: DMLState) -> LegacyCursorResult:
        """
        Execute the given query
        :param query: query to be executed
        :return: None.
        """
        return cls.connection.execute(query)

    @staticmethod
    def get_users() -> list[tuple[id, str]]:
        users = []
        users_in_queue = PostgresDBClient.scan_table()
        for index, user_data in enumerate(users_in_queue):
            users.append((index, user_data[1]))
        users.pop(0)
        return users
