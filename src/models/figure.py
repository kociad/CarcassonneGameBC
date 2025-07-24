import pygame
import logging
import typing
from models.gameBoard import GameBoard
import settings

logger = logging.getLogger(__name__)

class Figure:
    """Represents a figure (meeple) belonging to a player."""
    def __init__(self, owner: 'Player', image_path: str = settings.MEEPLE_IMAGES_PATH) -> None:
        """
        Initialize a figure for a specific player.
        :param owner: Player who owns the figure.
        :param image_path: Path to the meeple image.
        """
        self.owner = owner
        original_image = pygame.image.load(image_path + f"{owner.getColor()}.png")
        self.image = pygame.transform.scale(original_image, (settings.FIGURE_SIZE, settings.FIGURE_SIZE))
        self.card = None
        self.positionOnCard = None

    def getOwner(self) -> 'Player':
        """Return the player who owns the figure."""
        return self.owner

    def place(self, card: typing.Any, position: typing.Any) -> bool:
        """Attempt to place the figure on a given card at a given position."""
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
            "owner_index": self.owner.getIndex(),
            "position_on_card": self.positionOnCard,
            "card_position": position
        }

    @staticmethod
    def deserialize(data: dict, playerMap: dict, gameBoard: typing.Any) -> typing.Optional['Figure']:
        """Deserialize a figure from a dictionary."""
        try:
            owner_index = int(data["owner_index"])
            owner = playerMap[owner_index]
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to resolve owner for figure: {data} - {e}")
            return None
        try:
            figure = Figure(owner)
        except Exception as e:
            logger.error(f"Failed to initialize Figure for owner {owner.getName()} - {e}")
            return None
        try:
            pos_data = data.get("card_position")
            if pos_data is not None:
                if isinstance(pos_data, (list, tuple)):
                    x, y = int(pos_data[0]), int(pos_data[1])
                elif isinstance(pos_data, dict):
                    x, y = int(pos_data["X"]), int(pos_data["Y"])
                else:
                    raise TypeError("card_position must be dict or list/tuple")
                card = gameBoard.getCard(x, y)
                figure.card = card
        except Exception as e:
            logger.warning(f"Failed to set card position for figure: {data} - {e}")
            figure.card = None
        try:
            position = data.get("position_on_card")
            if position is not None:
                figure.positionOnCard = str(position)
            else:
                figure.positionOnCard = None
        except Exception as e:
            logger.warning(f"Failed to set figure position_on_card: {data} - {e}")
            figure.positionOnCard = None
        return figure