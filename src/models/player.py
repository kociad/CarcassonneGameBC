import pygame
import logging
import typing
from models.figure import Figure
import settings

logger = logging.getLogger(__name__)


class Player:
    """Represents a player in the game."""

    def __init__(self,
                 name: str,
                 color: str,
                 index: int,
                 is_ai: bool = False,
                 is_human: bool = False) -> None:
        """
        Initialize a player.
        
        Args:
            name: The name of the player
            color: Color of player's figures (string like "blue", "red", etc.)
            index: Player's index in the game
            is_ai: Whether the player is AI-controlled
            is_human: Whether the player is human-controlled
        """
        self.name = name
        self.color = color
        self.score = 0
        self.index = index
        self.figures = [Figure(self) for _ in range(7)]
        self.is_ai = is_ai
        self.is_human = is_human

    def get_is_ai(self) -> bool:
        """Check if player is AI-controlled."""
        return self.is_ai

    def get_name(self) -> str:
        """Get the player's name."""
        return self.name

    def get_score(self) -> int:
        """Get the player's score."""
        return self.score

    def get_figures(self) -> list:
        """Get the list of figures held by the player."""
        return self.figures

    def get_index(self) -> int:
        """Get the player's index."""
        return self.index

    def get_color(self) -> str:
        """Get the color of the player's figures."""
        return self.color

    def get_color_with_alpha(self, alpha: int = 150) -> pygame.Color:
        """
        Get the player's color as a pygame.Color with the given alpha.
        
        Args:
            alpha: Alpha value for the color
            
        Returns:
            pygame.Color with specified alpha
        """
        color = pygame.Color(self.color)
        color.a = alpha
        return color

    def get_figure(self) -> typing.Union['Figure', bool]:
        """
        Pop and return a figure if available.
        
        Returns:
            Figure if available, False otherwise
        """
        logger.debug("Retrieving figure...")
        if self.figures:
            logger.debug("Figure retrieved")
            return self.figures.pop()
        logger.debug("Unable to retrieve figure")
        return False

    def add_figure(self, figure: 'Figure') -> None:
        """
        Add a figure to the player's list.
        
        Args:
            figure: Figure to add
        """
        self.figures.append(figure)

    def add_score(self, score: int) -> None:
        """
        Add points to the player's score.
        
        Args:
            score: Points to add
        """
        self.score += score

    def set_is_human(self, is_human: bool) -> None:
        """
        Set whether the player is human-controlled.
        
        Args:
            is_human: Whether the player is human
        """
        self.is_human = is_human

    def serialize(self) -> dict:
        """Serialize the player to a dictionary."""
        return {
            "name": self.name,
            "score": self.score,
            "index": self.index,
            "color": self.color,
            "is_ai": self.is_ai,
            "figures_remaining": len(self.figures),
            "is_human": self.is_human
        }

    @staticmethod
    def deserialize(data: dict) -> 'Player':
        """
        Create a Player instance from serialized data.
        
        Args:
            data: Serialized player data
            
        Returns:
            Player instance with restored state or None if deserialization failed
        """
        try:
            name = str(data["name"])
            index = int(data["index"])
            color = str(data["color"])
            is_ai = bool(data.get("is_ai", False))
            score = int(data.get("score", 0))
            figures_remaining = int(data.get("figures_remaining", 7))
            is_human = bool(data.get("is_human", False))

            player = Player(name=name,
                            color=color,
                            index=index,
                            is_ai=is_ai,
                            is_human=is_human)
            player.score = score
            player.figures = [Figure(player) for _ in range(figures_remaining)]
            return player
        except (KeyError, ValueError, TypeError) as e:
            logger.error(
                f"Failed to deserialize Player object: {e}\nData: {data}")
            return None
