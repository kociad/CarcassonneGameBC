import pygame
import logging
import typing
from models.gameBoard import GameBoard
import settings

logger = logging.getLogger(__name__)


class Figure:
    """Represents a figure (meeple) belonging to a player."""

    def __init__(self,
                 owner: 'Player',
                 imagePath: str = settings.FIGURE_IMAGES_PATH) -> None:
        """
        Initialize a figure for a specific player.
        
        Args:
            owner: Player who owns the figure
            imagePath: Path to the meeple image
        """
        self.owner = owner
        originalImage = pygame.image.load(imagePath +
                                          f"{owner.getColor()}.png")
        self.image = pygame.transform.scale(
            originalImage, (settings.FIGURE_SIZE, settings.FIGURE_SIZE))
        self.card = None
        self.positionOnCard = None

    def getOwner(self) -> 'Player':
        """Get the player who owns the figure."""
        return self.owner

    def place(self, card: typing.Any, position: typing.Any) -> bool:
        """
        Attempt to place the figure on a given card at a given position.
        
        Args:
            card: Card to place the figure on
            position: Position on the card to place the figure
            
        Returns:
            True if placement was successful, False otherwise
        """
        logger.debug(f"Placing figure on card {card} position {position}...")
        if card is not None:
            self.card = card
            self.positionOnCard = position
            logger.debug("Figure placed")
            return True
        logger.debug("Unable to place figure, placement invalid")
        return False

    def remove(self) -> None:
        """Remove the figure from the board."""
        self.card = None
        self.positionOnCard = None

    def serialize(self) -> dict:
        """Serialize the figure to a dictionary."""
        position = None
        if self.card:
            position = self.card.getPosition() if self.card else None
        return {
            "ownerIndex": self.owner.getIndex(),
            "positionOnCard": self.positionOnCard,
            "cardPosition": position
        }

    @staticmethod
    def deserialize(data: dict, playerMap: dict,
                    gameBoard: typing.Any) -> typing.Optional['Figure']:
        """
        Create a Figure instance from serialized data.
        
        Args:
            data: Serialized figure data
            playerMap: Mapping of player indices to player objects
            gameBoard: The game board
            
        Returns:
            Figure instance with restored state or None if deserialization failed
        """
        try:
            ownerIndex = int(data["ownerIndex"])
            owner = playerMap[ownerIndex]
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to resolve owner for figure: {data} - {e}")
            return None
        try:
            figure = Figure(owner)
        except Exception as e:
            logger.error(
                f"Failed to initialize Figure for owner {owner.getName()} - {e}"
            )
            return None
        try:
            posData = data.get("cardPosition")
            if posData is not None:
                if isinstance(posData, (list, tuple)):
                    x, y = int(posData[0]), int(posData[1])
                elif isinstance(posData, dict):
                    x, y = int(posData["X"]), int(posData["Y"])
                else:
                    raise TypeError("cardPosition must be dict or list/tuple")
                card = gameBoard.getCard(x, y)
                figure.card = card
        except Exception as e:
            logger.warning(
                f"Failed to set card position for figure: {data} - {e}")
            figure.card = None
        try:
            position = data.get("positionOnCard")
            if position is not None:
                figure.positionOnCard = str(position)
            else:
                figure.positionOnCard = None
        except Exception as e:
            logger.warning(
                f"Failed to set figure positionOnCard: {data} - {e}")
            figure.positionOnCard = None
        return figure
