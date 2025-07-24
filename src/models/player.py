import pygame
import logging
import typing

from models.figure import Figure
import settings

logger = logging.getLogger(__name__)

class Player:
    """Represents a player in the game."""
    def __init__(self, name: str, index: int, color: str, isAI: bool = False, isHuman: bool = False) -> None:
        """
        Initialize a player.
        :param name: The name of the player.
        :param index: Player's index in the game.
        :param color: Color of player's figures.
        :param isAI: Whether the player is AI-controlled.
        :param isHuman: Whether the player is human-controlled.
        """
        self.name = name
        self.color = color
        self.score = 0
        self.index = index
        self.figures = [Figure(self) for _ in range(7)]
        self.isAI = isAI
        self.isHuman = isHuman

    def getIsAI(self) -> bool:
        """Return True if player is AI-controlled."""
        return self.isAI

    def getName(self) -> str:
        """Return the player's name."""
        return self.name

    def getScore(self) -> int:
        """Return the player's score."""
        return self.score

    def getFigures(self) -> list:
        """Return the list of figures held by the player."""
        return self.figures

    def getIndex(self) -> int:
        """Return the player's index."""
        return self.index

    def getColor(self) -> str:
        """Return the color of the player's figures."""
        return self.color

    def getColorWithAlpha(self, alpha: int = 150) -> pygame.Color:
        """Return the player's color as a pygame.Color with the given alpha."""
        color = pygame.Color(self.color)
        color.a = alpha
        return color

    def getFigure(self) -> typing.Union['Figure', bool]:
        """Pop and return a figure if available, else return False."""
        logger.debug("Retrieving figure...")
        if self.figures:
            logger.debug("Figure retrieved")
            return self.figures.pop()
        logger.debug("Unable to retrieve figure")
        return False

    def addFigure(self, figure: 'Figure') -> None:
        """Add a figure to the player's list."""
        self.figures.append(figure)

    def addScore(self, score: int) -> None:
        """Add points to the player's score."""
        self.score += score

    def setIsHuman(self, isHuman: bool) -> None:
        """Set whether the player is human-controlled."""
        self.isHuman = isHuman

    def serialize(self) -> dict:
        """Serialize the player to a dictionary."""
        return {
            "name": self.name,
            "score": self.score,
            "index": self.index,
            "color": self.color,
            "isAI": self.isAI,
            "figuresRemaining": len(self.figures),
            "isHuman": self.isHuman
        }

    @staticmethod
    def deserialize(data: dict) -> 'Player':
        """Deserialize a player from a dictionary."""
        try:
            name = str(data["name"])
            index = int(data["index"])
            color = str(data["color"])
            isAI = bool(data.get("isAI", False))
            score = int(data.get("score", 0))
            figuresRemaining = int(data.get("figuresRemaining", 7))
            isHuman = bool(data.get("isHuman", False))

            player = Player(name=name, index=index, color=color, isAI=isAI, isHuman=isHuman)
            player.score = score
            player.figures = [Figure(player) for _ in range(figuresRemaining)]
            return player
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to deserialize Player object: {e}\nData: {data}")
            return None
