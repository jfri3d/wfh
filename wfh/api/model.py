from enum import Enum, auto


class Actions(Enum):
    login = auto()
    coffee = auto()
    move = auto()
    pushups = auto()
    lunch = auto()
    logoff = auto()

    @staticmethod
    def contains(name: str):
        return name in Actions.__members__
