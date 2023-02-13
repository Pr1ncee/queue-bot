from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine, Connection

from app.scripts import settings


db_link = settings.DB_LINK


class ClientMeta(type):
    @property
    def client(cls) -> Engine:
        if not getattr(cls, '_client', None):
            client = create_engine(db_link)
            setattr(cls, '_client', client)
        return getattr(cls, '_client')

    @property
    def connection(cls) -> Connection:
        if not getattr(cls, '_connection', None):
            connection = cls.client.connect()
            setattr(cls, '_connection', connection)
        return getattr(cls, '_connection')
