class AppError(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidConnection(AppError):
    def __init__(self, msg: str):
        super().__init__(f"InvalidConnection: {msg}")
