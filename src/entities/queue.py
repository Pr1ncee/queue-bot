from dataclasses import dataclass
from typing import Optional

from bson import ObjectId

from src.entities.base_entity import BaseEntity


@dataclass
class QueueEntity(BaseEntity):
    chat_id: int
    msg_id: int
    name: str
    people: list[str]
    _id: Optional[ObjectId] = None

    def get_dict(self) -> dict:
        entity_dict = super().get_dict()
        entity_dict.pop("_id")
        return entity_dict
