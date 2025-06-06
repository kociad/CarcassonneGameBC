import logging

from models.card import Card
from settings import GRID_SIZE, DEBUG

logger = logging.getLogger(__name__)

class GameBoard:
    """
    Represents the game board where cards are placed.
    """
    
    def __init__(self, gridSize=GRID_SIZE):
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
    
    def placeCard(self, card, x, y):
        """
        Places a card on the board at the given coordinates without validation.
        :param card: The card (Card) to be placed.
        :param x: X-coordinate on the board.
        :param y: Y-coordinate on the board.
        """
        if not (0 <= x < GRID_SIZE):
            raise ValueError(f"x must be between 1 and {GRID_SIZE - 1}, got {x}")
        
        if not (0 <= y < GRID_SIZE):
            raise ValueError(f"y must be between 1 and {GRID_SIZE - 1}, got {y}")
            
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            self.grid[y][x] = card
            self.updateNeighbors(x,y)
    
    def getCard(self, x, y):
        """
        Retrieves a card from the board at the given coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :return: The card (Card) at the specified position, or None if empty.
        """
        if not (0 <= x < GRID_SIZE):
            logger.debug(f"Error getting card: x must be between 1 and {GRID_SIZE - 1}, got {x}")
            return None
        
        if not (0 <= y < GRID_SIZE):
            logger.debug(f"Error getting card: y must be between 1 and {GRID_SIZE - 1}, got {y}")
            return None
            
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            return self.grid[y][x]
            
        return None
        
    def getCardPosition(self, card):
        for y in range(self.gridSize):
            for x in range(self.gridSize):
                if self.getCard(x, y) == card:
                    return x, y
        return None, None

    def validateCardPlacement(self, card, x, y):
        """
        Validates if a card can be placed on given space
        :param card: Card to be placed
        :param x: X-coordinate of selected space
        :param y: Y-coordinate of selected space
        :return: True if placement is valid, false otherwise
        """
        logger.debug("Validating card placement...")
        
        if not (0 <= x < GRID_SIZE) or not (0 <= y < GRID_SIZE):
            logger.debug(f"Placement invalid, coordinates out of bounds.")
            return False
        
        if self.getCard(x,y) is not None:
            logger.debug(f"Placement invalid, expected None in space, got {self.getCard(x,y)}")
            return False # Cannot place card where one already exists
            
        if not self.hasNeighbor(x,y):
            logger.debug(f"Placement invalid, no valid neighbor found")
            return False
            
        neighbors = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        
        for direction, (nx, ny) in neighbors.items():
            if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize: # Validate only neighbors within the grid
                neighbor = self.getCard(nx, ny)
                if neighbor:
                    logger.debug(f"Testing directions currentCard: {direction} - {card.getTerrains()[direction]} neighbor: {self.getOppositeDirection(direction)} - {neighbor.getTerrains()[self.getOppositeDirection(direction)]}")
                    if card.getTerrains()[direction] != neighbor.getTerrains()[self.getOppositeDirection(direction)]:
                        logger.debug(f"Terrain mismatch!")
                        return False  # Terrains do not match, placement is invalid
        
        logger.debug(f"Placement is valid!")
        return True  # Placement is valid
            
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
        from models.card import Card
        board = GameBoard(gridSize=data.get("grid_size", GRID_SIZE))
        board.center = data.get("center", board.gridSize // 2)  # fallback to default if missing

        for item in data["placed_cards"]:
            x = item["x"]
            y = item["y"]
            card_data = item["card"]
            card = Card.deserialize(card_data)
            board.placeCard(card, x, y)

        return board

