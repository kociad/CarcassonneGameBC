import pygame
import logging

from models.gameBoard import GameBoard

import settings

logger = logging.getLogger(__name__)

class Figure:
    
    def __init__(self, owner, image_path = settings.MEEPLE_IMAGES_PATH):
        """
        Init a figure belonging to a specific player
        :param owner: Player owner of the figure
        """
        self.owner = owner
        original_image = pygame.image.load(image_path + f"{owner.getColor()}.png")
        self.image = pygame.transform.scale(original_image, (settings.FIGURE_SIZE, settings.FIGURE_SIZE))  # Resize to match TILE_SIZE
        self.card = None # Card on which the figure has been placed
        self.positionOnCard = None # Position on the card (e.g., road, city, monastery)
        
    def getOwner(self):
        """
        Figure owner getter method
        :return: Player owning the figure
        """
        return self.owner
        
    def place(self, card, position):
        """
        Attempts to place the figure on a given card at a given position
        :param card: Card on which the figure is to be placed
        :param positiojn: The specific position on the card
        :return: True if placement is successful, False otherwise
        """
        logger.debug(f"Placing figure on card {card} position {position}...")
        if card.canPlaceFigure(position):
            self.card = card
            self.positionOnCard = position
            logger.debug("Figure placed")
            return True
        logger.debug("Unable to place figure, placement invalid")
        return False
        
    def remove(self):
        """
        Remove the figure from the board
        """
        self.card = None
        self.positionOnCard = None
        
    def serialize(self):
        position = None
        if self.card:
            position = self.card.getPosition() if self.card else None
        return {
            "owner_index": self.owner.getIndex(),
            "position_on_card": self.positionOnCard,
            "card_position": position  # needed to re-link during deserialization
        }
        
    @staticmethod
    def deserialize(data, playerMap, gameBoard):
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

        # Set card if card_position is valid
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

        # Set position on card
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