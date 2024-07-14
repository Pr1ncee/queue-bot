import logging

import pymongo

from src.entities.active_chat import ActiveChatEntity
from src.entities.queue import QueueEntity
from src.settings.config import mongo_config

logger = logging.getLogger(__name__)


class MongoDBClient:
    def __init__(self):
        self.client = pymongo.MongoClient(host=mongo_config.HOST, port=mongo_config.PORT)
        self.db = self.client[mongo_config.DB_NAME]
        self.queue_collection = self.db[mongo_config.QUEUE_COLLECTION_NAME]
        self.internal_collection = self.db[mongo_config.INTERNAL_COLLECTION_NAME]

    def create_queue(self, queue_entity: QueueEntity) -> None:
        try:
            self.queue_collection.insert_one(document=queue_entity.get_dict())
        except pymongo.errors.DuplicateKeyError:
            logger.exception(f"Document: {queue_entity} already exist!")

    def add_people_to_queue(self, msg_id: int, people: list[str]):
        self.queue_collection.update_one(
            {"msg_id": msg_id},
            {"$addToSet": {"people": {"$each": people}}}
        )

    def remove_from_queue(self, msg_id: int, username: str) -> None:
        self.queue_collection.update_one(
            filter={"msg_id": msg_id},
            update={"$pull": {"people": username}}
        )

    def is_already_in_queue(self, username: str, **kwargs) -> bool:
        queue = self.get_queue(**kwargs)
        return bool(queue) and username in queue.people

    def get_queue(self, **kwargs) -> QueueEntity | None:
        """
        **kwargs must be either chat_id, msg_id or name
        """
        doc = self.queue_collection.find_one(kwargs)
        return QueueEntity(**doc) if doc else None

    def delete_queue(self, **kwargs) -> None:
        """
        **kwargs must be either chat_id, msg_id or name
        """
        self.queue_collection.delete_one(kwargs)

    def delete_outdated_queues(self, chat_id: int) -> list[int]:
        documents = self.queue_collection.find({"chat_id": chat_id}, {"msg_id": 1})
        msg_ids = [doc["msg_id"] for doc in documents]

        self.queue_collection.delete_many(filter={"chat_id": chat_id})
        return msg_ids

    def get_active_chats(self) -> ActiveChatEntity | None:
        active_chats = self.internal_collection.find_one({"name": ActiveChatEntity.name})
        default_doc = ActiveChatEntity()
        if not active_chats:
            self.internal_collection.insert_one(default_doc.get_dict())
        return ActiveChatEntity(**active_chats) if active_chats else default_doc

    def add_active_chat(self, active_chat: ActiveChatEntity) -> None:
        self.internal_collection.update_one(
            {"name": active_chat.name},
            {"$addToSet": {"active_chats": {"$each": active_chat.active_chats}}}
        )

    def is_chat_active(self, chat_id: int) -> bool:
        active_chats_doc = self.get_active_chats()
        return True if chat_id in active_chats_doc.active_chats else False

    def delete_all_queues(self) -> None:
        self.queue_collection.delete_many({})
        self.internal_collection.delete_many({})

    def ping(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except pymongo.errors.ConnectionFailure:
            return False
