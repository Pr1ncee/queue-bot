from dataclasses import dataclass, field
from typing import Optional

from bson import ObjectId

from src.entities.base_entity import BaseEntity


@dataclass
class ActiveChatEntity(BaseEntity):
    active_chats: list[int] = field(default_factory=list)
    name: str = "Active Chats"  # Mustn't be changed
    _id: Optional[ObjectId] = None
