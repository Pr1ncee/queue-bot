class BaseError(Exception):
    status_code: int
    content: dict

    def __init__(self, status_code: int, content: dict = None):
        self.status_code = status_code
        self.content = content or self.content


class ClientError(BaseError):
    content = {"message": "The request failed!"}


class ServerError(BaseError):
    content = {"message": "Server error!"}


class FatalError(BaseError):
    content = {"message": "Fatal error!"}
