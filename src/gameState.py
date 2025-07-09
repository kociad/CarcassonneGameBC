from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    GAME = auto()
    SETTINGS = auto()
    PREPARE = auto()