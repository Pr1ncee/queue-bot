from enums.base_enum import BaseEnum


class CallbackEnum(BaseEnum):
    JOIN_QUEUE = "join_queue"
    LEAVE_QUEUE = "leave_queue"
    CLOSE_QUEUE = "close_queue"
