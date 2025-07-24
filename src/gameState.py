from enum import Enum, auto

class GameState(Enum):
    """Enum representing the different states of the game"""
    MENU: int = auto()
    GAME: int = auto()
    SETTINGS: int = auto()
    PREPARE: int = auto()
    HELP: int = auto()
    LOBBY: int = auto()