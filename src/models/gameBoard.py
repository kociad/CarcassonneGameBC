import logging
import typing
from models.card import Card
import settings

logger = logging.getLogger(__name__)


class GameBoard:
    """Represents the game board where cards are placed."""

    def __init__(self, grid_size: int = int(settings.GRID_SIZE)) -> None:
        """
        Initialize the game board with an empty grid.
        
        Args:
            grid_size: The size of the board grid
        """
        self.grid_size = grid_size
        self.grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.center = grid_size // 2

    def get_grid_size(self) -> int:
        """Get the size of the square grid."""
        return self.grid_size

    def get_center_position(self) -> tuple[int, int]:
        """Get the center position of the board as (x, y)."""
        return self.center, self.center

    def get_center(self) -> int:
        """Get the center value of the board."""
        return self.center

    def place_card(self, card: 'Card', x: int, y: int) -> None:
        """
        Place a card on the board at the given coordinates without validation.
        
        Args:
            card: Card to place
            x: X coordinate
            y: Y coordinate
        """
        if not (0 <= x < self.grid_size):
            raise ValueError(
                f"x must be between 1 and {self.grid_size - 1}, got {x}")
        if not (0 <= y < self.grid_size):
            raise ValueError(
                f"y must be between 1 and {self.grid_size - 1}, got {y}")
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            card.set_position(x, y)
            self.grid[y][x] = card
            self._update_neighbors(x, y)

    def get_card(self, x: int, y: int) -> typing.Optional['Card']:
        """
        Retrieve a card from the board at the given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Card at the position or None if not found
        """
        if not (0 <= x < self.grid_size):
            logger.debug(
                f"Error getting card: x must be between 1 and {self.grid_size - 1}, got {x}"
            )
            return None
        if not (0 <= y < self.grid_size):
            logger.debug(
                f"Error getting card: y must be between 1 and {self.grid_size - 1}, got {y}"
            )
            return None
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[y][x]
        return None

    def get_card_position(
            self,
            card: 'Card') -> tuple[typing.Optional[int], typing.Optional[int]]:
        """
        Get the (x, y) position of a card based on its internal position attribute.
        
        Args:
            card: Card to get position for
            
        Returns:
            Tuple of (x, y) coordinates or (None, None) if not found
        """
        pos = card.get_position()
        try:
            x = int(pos["X"]) if pos["X"] is not None else None
            y = int(pos["Y"]) if pos["Y"] is not None else None
        except (KeyError, ValueError, TypeError):
            x, y = None, None
        return x, y

    def validate_card_placement(self, card: 'Card', x: int, y: int) -> bool:
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
        if not (0 <= x < self.grid_size) or not (0 <= y < self.grid_size):
            logger.debug(
                f"Cannot place card at ({x}, {y}) - position out of bounds")
            return False
        if self.get_card(x, y) is not None:
            logger.debug(
                f"Cannot place card at ({x}, {y}) - position already occupied")
            return False
        if not self.has_neighbor(x, y):
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
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbor = self.get_card(nx, ny)
                if neighbor:
                    card_terrain = card.get_terrains()[direction]
                    neighbor_terrain = neighbor.get_terrains()[
                        self.get_opposite_direction(direction)]
                    if card_terrain != neighbor_terrain:
                        logger.debug(
                            f"Cannot place card at ({x}, {y}) - {card_terrain} doesn't match neighbor's {neighbor_terrain}"
                        )
                        return False
        return True

    def get_opposite_direction(self, direction: str) -> str:
        """
        Get the opposite direction for a given direction.
        
        Args:
            direction: Direction to get opposite for
            
        Returns:
            Opposite direction
        """
        opposites = {"N": "S", "E": "W", "S": "N", "W": "E"}
        return opposites[direction]

    def has_neighbor(self, x: int, y: int) -> bool:
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
        exists_neighbor = False
        for direction, (nx, ny) in neighbors.items():
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbor = self.get_card(nx, ny)
                logger.debug(f"Testing existence of neighbor {direction}...")
                if neighbor:
                    logger.debug(f"Neighbor found!")
                    exists_neighbor = True
                    break
        return exists_neighbor

    def _update_neighbors(self, x: int, y: int) -> None:
        """
        Update the neighbors dictionary for the card at (x, y).
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        card = self.get_card(x, y)
        if card is None:
            return
        directions = {
            "N": (x, y - 1),
            "E": (x + 1, y),
            "S": (x, y + 1),
            "W": (x - 1, y)
        }
        for direction, (nx, ny) in directions.items():
            neighbor = self.get_card(nx, ny)
            card.neighbors[direction] = neighbor
            if neighbor:
                opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
                neighbor.neighbors[opposite] = card

    def serialize(self) -> dict:
        """Serialize the game board to a dictionary."""
        placed = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                card = self.grid[y][x]
                if card:
                    placed.append({"x": x, "y": y, "card": card.serialize()})
        return {
            "gridSize": self.grid_size,
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
            grid_size = int(data.get("grid_size", settings.GRID_SIZE))
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid grid_size in GameBoard data: {data.get('grid_size')} - {e}"
            )
            grid_size = int(settings.GRID_SIZE)
        board = GameBoard(grid_size=grid_size)
        try:
            board.center = int(data.get("center", board.grid_size // 2))
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Invalid center value, defaulting to center of grid - {e}")
            board.center = board.grid_size // 2
        for item in data.get("placedCards", []):
            try:
                x = int(item["x"])
                y = int(item["y"])
                card_data = item["card"]
                if not isinstance(card_data, dict):
                    raise TypeError("card field must be a dictionary")
                card = Card.deserialize(card_data)
                board.place_card(card, x, y)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Failed to place card at {item}: {e}")
            except Exception as e:
                logger.error(
                    f"Unexpected error while placing card at {item}: {e}")
        return board
