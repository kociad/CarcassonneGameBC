from enum import Enum, auto


class GameState(Enum):
    MENU: int = auto()
    GAME: int = auto()
    SETTINGS: int = auto()
    PREPARE: int = auto()
    HELP: int = auto()
    LOBBY: int = auto()
    THEME_DEBUG: int = auto()
