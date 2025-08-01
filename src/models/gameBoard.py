import logging
import typing
from models.card import Card
import settings

logger = logging.getLogger(__name__)


class GameBoard:
    """Represents the game board where cards are placed."""

    def __init__(self, gridSize: int = int(settings.GRID_SIZE)) -> None:
        """
        Initialize the game board with an empty grid.
        
        Args:
            gridSize: The size of the board grid
        """
        self.gridSize = gridSize
        self.grid = [[None for _ in range(gridSize)] for _ in range(gridSize)]
        self.center = gridSize // 2

    def getGridSize(self) -> int:
        """Get the size of the square grid."""
        return self.gridSize

    def getCenterPosition(self) -> tuple[int, int]:
        """Get the center position of the board as (x, y)."""
        return self.center, self.center

    def getCenter(self) -> int:
        """Get the center value of the board."""
        return self.center

    def placeCard(self, card: 'Card', x: int, y: int) -> None:
        """
        Place a card on the board at the given coordinates without validation.
        
        Args:
            card: Card to place
            x: X coordinate
            y: Y coordinate
        """
        if not (0 <= x < self.gridSize):
            raise ValueError(
                f"x must be between 1 and {self.gridSize - 1}, got {x}")
        if not (0 <= y < self.gridSize):
            raise ValueError(
                f"y must be between 1 and {self.gridSize - 1}, got {y}")
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            card.setPosition(x, y)
            self.grid[y][x] = card
            self.updateNeighbors(x, y)

    def getCard(self, x: int, y: int) -> typing.Optional['Card']:
        """
        Retrieve a card from the board at the given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Card at the position or None if not found
        """
        if not (0 <= x < self.gridSize):
            logger.debug(
                f"Error getting card: x must be between 1 and {self.gridSize - 1}, got {x}"
            )
            return None
        if not (0 <= y < self.gridSize):
            logger.debug(
                f"Error getting card: y must be between 1 and {self.gridSize - 1}, got {y}"
            )
            return None
        if 0 <= x < self.gridSize and 0 <= y < self.gridSize:
            return self.grid[y][x]
        return None

    def getCardPosition(
            self,
            card: 'Card') -> tuple[typing.Optional[int], typing.Optional[int]]:
        """
        Get the (x, y) position of a card based on its internal position attribute.
        
        Args:
            card: Card to get position for
            
        Returns:
            Tuple of (x, y) coordinates or (None, None) if not found
        """
        pos = card.getPosition()
        try:
            x = int(pos["X"]) if pos["X"] is not None else None
            y = int(pos["Y"]) if pos["Y"] is not None else None
        except (KeyError, ValueError, TypeError):
            x, y = None, None
        return x, y

    def validateCardPlacement(self, card: 'Card', x: int, y: int) -> bool:
        """
        Validate if a card can be placed on the given space.
        
        Args:
            card: Card to validate placement for
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if placement is valid, False otherwise
        """
        logger.debug("Validating card placement...")
        if not (0 <= x < self.gridSize) or not (0 <= y < self.gridSize):
            logger.debug(
                f"Cannot place card at ({x}, {y}) - position out of bounds")
            return False
        if self.getCard(x, y) is not None:
            logger.debug(
                f"Cannot place card at ({x}, {y}) - position already occupied")
            return False
        if not self.hasNeighbor(x, y):
            logger.debug(
                f"Cannot place card at ({x}, {y}) - no adjacent cards found")
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
                    neighborTerrain = neighbor.getTerrains()[
                        self.getOppositeDirection(direction)]
                    if cardTerrain != neighborTerrain:
                        logger.debug(
                            f"Cannot place card at ({x}, {y}) - {cardTerrain} doesn't match neighbor's {neighborTerrain}"
                        )
                        return False
        return True

    def getOppositeDirection(self, direction: str) -> str:
        """
        Get the opposite direction for a given direction.
        
        Args:
            direction: Direction to get opposite for
            
        Returns:
            Opposite direction
        """
        opposites = {"N": "S", "E": "W", "S": "N", "W": "E"}
        return opposites[direction]

    def hasNeighbor(self, x: int, y: int) -> bool:
        """
        Check if the selected space has an occupied neighbor.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if there is a neighbor, False otherwise
        """
        logger.debug("Checking for neighbors...")
        neighbors = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        existsNeighbor = False
        for direction, (nx, ny) in neighbors.items():
            if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize:
                neighbor = self.getCard(nx, ny)
                logger.debug(f"Testing existence of neighbor {direction}...")
                if neighbor:
                    logger.debug(f"Neighbor found!")
                    existsNeighbor = True
                    break
        return existsNeighbor

    def updateNeighbors(self, x: int, y: int) -> None:
        """
        Update the neighbors dictionary for the card at (x, y).
        
        Args:
            x: X coordinate
            y: Y coordinate
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

    def serialize(self) -> dict:
        """Serialize the game board to a dictionary."""
        placed = []
        for y in range(self.gridSize):
            for x in range(self.gridSize):
                card = self.grid[y][x]
                if card:
                    placed.append({"x": x, "y": y, "card": card.serialize()})
        return {
            "gridSize": self.gridSize,
            "center": self.center,
            "placedCards": placed
        }

    @staticmethod
    def deserialize(data: dict) -> 'GameBoard':
        """
        Create a GameBoard instance from serialized data.
        
        Args:
            data: Serialized board data
            
        Returns:
            GameBoard instance with restored state
        """
        try:
            gridSize = int(data.get("gridSize", settings.GRID_SIZE))
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid gridSize in GameBoard data: {data.get('gridSize')} - {e}"
            )
            gridSize = int(settings.GRID_SIZE)
        board = GameBoard(gridSize=gridSize)
        try:
            board.center = int(data.get("center", board.gridSize // 2))
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Invalid center value, defaulting to center of grid - {e}")
            board.center = board.gridSize // 2
        for item in data.get("placedCards", []):
            try:
                x = int(item["x"])
                y = int(item["y"])
                cardData = item["card"]
                if not isinstance(cardData, dict):
                    raise TypeError("card field must be a dictionary")
                card = Card.deserialize(cardData)
                board.placeCard(card, x, y)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Failed to place card at {item}: {e}")
            except Exception as e:
                logger.error(
                    f"Unexpected error while placing card at {item}: {e}")
        return board
