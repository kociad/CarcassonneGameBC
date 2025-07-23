import logging

from models.card import Card

import settings

logger = logging.getLogger(__name__)

class GameBoard:
    """
    Represents the game board where cards are placed.
    """
    
    def __init__(self, gridSize=int(settings.GRID_SIZE)):
        """
        Initializes the game board with an empty grid.
        :param gridSize: The size of the board grid (default: 20x20).
        """
        self.gridSize = gridSize
        self.grid = [[None for _ in range(gridSize)] for _ in range(gridSize)]
        self.center = gridSize // 2
        
    def getGridSize(self):
        """
        gridSize getter method
        :return: A number representing the size of the square grid
        """
        return self.gridSize
    
    def getCenterPosition(self):
        """
        Returns the center position of the board.
        :return: Tuple (x, y) representing the center coordinates.
        """
        return self.center, self.center
        
    def getCenter(self):
        """
        Returns the center value
        :return: Integer representing the exact halfpoint of the board
        """
        return self.center
    
    def placeCard(self, card, x, y):
        """
        Places a card on the board at the given coordinates without validation.
        :param card: The card (Card) to be placed.
        :param x: X-coordinate on the board.
        :param y: Y-coordinate on the board.
        """
        if not (0 <= x < self.gridSize):
            raise ValueError(f"x must be between 1 and {self.gridSize - 1}, got {x}")
        
        if not (0 <= y < self.gridSize):
            raise ValueError(f"y must be between 1 and {self.gridSize - 1}, got {y}")
            
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            card.setPosition(x,y)
            self.grid[y][x] = card
            self.updateNeighbors(x,y)
    
    def getCard(self, x, y):
        """
        Retrieves a card from the board at the given coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :return: The card (Card) at the specified position, or None if empty.
        """
        if not (0 <= x < self.gridSize):
            logger.debug(f"Error getting card: x must be between 1 and {self.gridSize - 1}, got {x}")
            return None
        
        if not (0 <= y < self.gridSize):
            logger.debug(f"Error getting card: y must be between 1 and {self.gridSize - 1}, got {y}")
            return None
            
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            return self.grid[y][x]
            
        return None
        
    def getCardPosition(self, card):
        """
        Retrieves the (x, y) position of a card based on its internal position attribute.
        :param card: The card object.
        :return: Tuple (x, y) if set, otherwise (None, None)
        """
        pos = card.getPosition()
        try:
            x = int(pos["X"]) if pos["X"] is not None else None
            y = int(pos["Y"]) if pos["Y"] is not None else None
        except (KeyError, ValueError, TypeError):
            x, y = None, None
        return x, y

    def validateCardPlacement(self, card, x, y):
        """
        Validates if a card can be placed on given space
        """
        logger.debug("Validating card placement...")
        
        if not (0 <= x < self.gridSize) or not (0 <= y < self.gridSize):
            logger.debug(f"Cannot place card at ({x}, {y}) - position out of bounds")
            return False
        
        if self.getCard(x, y) is not None:
            logger.debug(f"Cannot place card at ({x}, {y}) - position already occupied")
            return False
            
        if not self.hasNeighbor(x, y):
            logger.debug(f"Cannot place card at ({x}, {y}) - no adjacent cards found")
            return False
            
        neighbors = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        
        for direction, (nx, ny) in neighbors.items():
            if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize:
                neighbor = self.getCard(nx, ny)
                if neighbor:
                    cardTerrain = card.getTerrains()[direction]
                    neighborTerrain = neighbor.getTerrains()[self.getOppositeDirection(direction)]
                    if cardTerrain != neighborTerrain:
                        logger.debug(f"Cannot place card at ({x}, {y}) - {cardTerrain} doesn't match neighbor's {neighborTerrain}")
                        return False
        
        return True
            
    def getOppositeDirection(self, direction):
        """
        Returns the opposite direction
        :param direction: Direction to which opposite will be returned
        :return: Opposite direction
        """
        opposites = {"N": "S", "E": "W", "S": "N", "W": "E"}
        return opposites[direction]
        
    def hasNeighbor(self, x, y):
        """
        Checks if selected space has an occupied neighbor
        :param x: X-coordinate of selected space
        :param y: Y-coordinate of selected space
        :return: True if space has a neighbor, false otherwise
        """
        logger.debug("Checking for neighbors...")
        
        neighbors = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        
        existsNeighbor = False # By default no neighbor is expected
        
        for direction, (nx, ny) in neighbors.items():
            if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize: # Validate only neighbors within the grid
                neighbor = self.getCard(nx, ny)
                logger.debug(f"Testing existence of neighbor {direction}...")
                if neighbor:
                    logger.debug(f"Neighbor found!")
                    existsNeighbor = True
                    break

        return existsNeighbor
        
    def updateNeighbors(self, x, y):
        """
        Updates the neighbors dictionary for the card at (x, y)
        and also ensures reciprocal neighbor links are updated
        """
        card = self.getCard(x, y)
        if card is None:
            return

        directions = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }

        for direction, (nx, ny) in directions.items():
            neighbor = self.getCard(nx, ny)
            card.neighbors[direction] = neighbor
            if neighbor:
                opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
                neighbor.neighbors[opposite] = card
                
    def serialize(self):
        placed = []
        for y in range(self.gridSize):
            for x in range(self.gridSize):
                card = self.grid[y][x]
                if card:
                    placed.append({
                        "x": x,
                        "y": y,
                        "card": card.serialize()
                    })
        return {
            "grid_size": self.gridSize,
            "center": self.center,
            "placed_cards": placed
        }
    
    @staticmethod
    def deserialize(data):
        try:
            grid_size = int(data.get("grid_size", settings.GRID_SIZE))
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid grid_size in GameBoard data: {data.get('grid_size')} - {e}")
            grid_size = int(settings.GRID_SIZE)

        board = GameBoard(gridSize=grid_size)

        try:
            board.center = int(data.get("center", board.gridSize // 2))
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid center value, defaulting to center of grid - {e}")
            board.center = board.gridSize // 2

        for item in data.get("placed_cards", []):
            try:
                x = int(item["x"])
                y = int(item["y"])
                card_data = item["card"]
                if not isinstance(card_data, dict):
                    raise TypeError("card field must be a dictionary")

                card = Card.deserialize(card_data)
                board.placeCard(card, x, y)

            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Failed to place card at {item}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error while placing card at {item}: {e}")

        return board