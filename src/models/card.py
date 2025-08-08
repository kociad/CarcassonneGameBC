import pygame
import logging
import settings
import typing

logger = logging.getLogger(__name__)


class Card:
    """Represents a tile (card) in the game with an image and terrain properties."""

    def __init__(self, image_path: str, terrains: dict,
                 connections: typing.Optional[dict],
                 features: typing.Any) -> None:
        """
        Initialize a tile with an image and terrain data.
        
        Args:
            image_path: Path to the tile image
            terrains: Dictionary defining terrain types for each side
            connections: Dictionary defining connections within the card
            features: List of features on the card
        """
        self.image_path = image_path
        original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(
            original_image, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.terrains = terrains
        self.connections = connections
        self.occupied = {}
        self.features = features
        self.neighbors = {"N": None, "E": None, "S": None, "W": None}
        self.position = {"X": None, "Y": None}
        self.rotation = 0

        self._rotation_cache = {}

    def get_position(self) -> dict:
        """Get the card's position on the board."""
        return self.position

    def set_position(self, x: int, y: int) -> None:
        """
        Set the card's position on the board.
        
        Args:
            x: X coordinate of the card
            y: Y coordinate of the card
        """
        self.position = {"X": x, "Y": y}

    def get_image(self) -> pygame.Surface:
        """Get the card's image."""
        return self.image

    def get_rotated_image(self) -> pygame.Surface:
        """Get the card's image rotated to current rotation with caching."""
        if self.rotation == 0:
            return self.image

        if self.rotation in self._rotation_cache:
            return self._rotation_cache[self.rotation]

        rotated_image = pygame.transform.rotate(self.image, -self.rotation)
        self._rotation_cache[self.rotation] = rotated_image
        return rotated_image

    def get_terrains(self) -> dict:
        """Get the card's terrain information."""
        return self.terrains

    def get_neighbors(self) -> dict:
        """Get the card's neighboring cards."""
        return self.neighbors

    def get_neighbor(self, direction: str) -> typing.Any:
        """
        Get a specific neighbor card.
        
        Args:
            direction: Direction to get neighbor from
            
        Returns:
            Neighbor card or None
        """
        return self.neighbors[direction]

    def set_neighbor(self, direction: str, neighbor: typing.Any) -> None:
        """
        Set a neighbor card.
        
        Args:
            direction: Direction to set neighbor for
            neighbor: Neighbor card to set
        """
        self.neighbors[direction] = neighbor

    def get_connections(self) -> typing.Optional[dict]:
        """Get the card's internal connections."""
        return self.connections

    def get_features(self) -> typing.Any:
        """Get the card's features."""
        return self.features

    def rotate(self) -> None:
        """Rotate the card 90 degrees clockwise."""
        self.rotation = (self.rotation + 90) % 360

        logger.debug(f"Card rotation - {self.rotation}")

        direction_map = {
            "N": "E",
            "E": "S",
            "S": "W",
            "W": "N",
            "NW": "NE",
            "NE": "SE",
            "SE": "SW",
            "SW": "NW",
            "C": "C",
        }
        new_terrains = {}
        for dir, terrain in self.terrains.items():
            new_dir = direction_map.get(dir, dir)
            new_terrains[new_dir] = terrain
        self.terrains = new_terrains

        if self.connections:
            new_connections = {}
            for dir, connectedList in self.connections.items():
                new_dir = direction_map.get(dir, dir)
                new_connections[new_dir] = [
                    direction_map.get(conn, conn) for conn in connectedList
                ]

            self.connections = new_connections

    def serialize(self) -> dict:
        """Serialize the card to a dictionary."""
        return {
            "image_path": self.image_path,
            "terrains": self.terrains,
            "connections": self.connections,
            "features": self.features,
            "occupied": self.occupied,
            "neighbors": {
                dir: None if neighbor is None else neighbor.image_path
                for dir, neighbor in self.neighbors.items()
            },
            "position": self.position,
            "rotation": self.rotation
        }

    @staticmethod
    def deserialize(data: dict) -> 'Card':
        """
        Create a Card instance from serialized data.
        
        Args:
            data: Serialized card data
            
        Returns:
            Card instance with restored state
        """
        try:
            image_path = str(data["image_path"])
            terrains = dict(data["terrains"])
            connections = data.get("connections", None)
            if connections is not None and not isinstance(connections, dict):
                raise TypeError("connections must be a dict or None")
            features = data.get("features", None)
            if features is not None and not isinstance(features, list):
                raise TypeError("features must be a list or None")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to parse required card fields: {data} - {e}")
            raise

        try:
            card = Card(image_path=image_path,
                        terrains=terrains,
                        connections=connections,
                        features=features)
        except Exception as e:
            logger.error(f"Failed to initialize Card from data: {data} - {e}")
            raise

        try:
            card.occupied = data.get("occupied", {})
            if not isinstance(card.occupied, dict):
                logger.warning(
                    f"Invalid 'occupied' field type, resetting to empty dict: {card.occupied}"
                )
                card.occupied = {}

            card.neighbors = {dir: None for dir in ["N", "E", "S", "W"]}

            pos = data.get("position", {"X": None, "Y": None})
            if isinstance(pos, dict):
                x = pos.get("X", None)
                y = pos.get("Y", None)
                card.position = {
                    "X": int(x) if x is not None else None,
                    "Y": int(y) if y is not None else None
                }
            else:
                logger.warning(
                    f"Invalid 'position' format: {pos}, defaulting to None")
                card.position = {"X": None, "Y": None}

            raw_rotation = data.get("rotation", 0)
            try:
                card.rotation = int(raw_rotation)
            except Exception as e:
                logger.warning(
                    f"Invalid rotation value: {raw_rotation}, defaulting to 0 - {e}"
                )
                card.rotation = 0

        except Exception as e:
            logger.error(f"Failed to parse optional card fields: {data} - {e}")
            raise

        return card
