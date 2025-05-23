import pygame
import logging

from settings import MEEPLE_IMAGES_PATH, FIGURE_SIZE, DEBUG

logger = logging.getLogger(__name__)

class Figure:
    
    def __init__(self, owner, image_path = MEEPLE_IMAGES_PATH):
        """
        Init a figure belonging to a specific player
        :param owner: Player owner of the figure
        """
        self.owner = owner
        original_image = pygame.image.load(image_path + f"{owner.getColor()}.png")
        self.image = pygame.transform.scale(original_image, (FIGURE_SIZE, FIGURE_SIZE))  # Resize to match TILE_SIZE
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
        return {
            "owner_index": self.owner.getIndex(),
            "position_on_card": self.positionOnCard,
            # card position must be filled manually by the GameSession serializer
        }
        
    @staticmethod
    def deserialize(data, playerMap, gameBoard):
        from models.figure import Figure

        owner = playerMap[data["owner_index"]]
        figure = Figure(owner)

        if data["card_position"]:
            x, y = data["card_position"]
            card = gameBoard.getCard(x, y)
            figure.card = card
            figure.positionOnCard = data["position_on_card"]

        return figure
