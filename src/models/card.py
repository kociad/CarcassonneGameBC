import pygame
import logging
import settings
import typing

logger = logging.getLogger(__name__)


class Card:
    """Represents a tile (card) in the game with an image and terrain properties."""

    def __init__(self, imagePath: str, terrains: dict, connections: typing.Optional[dict], features: typing.Any) -> None:
        """
        Initialize a tile with an image and terrain data.
        
        Args:
            imagePath: Path to the tile image
            terrains: Dictionary defining terrain types for each side
            connections: Dictionary defining connections within the card
            features: List of features on the card
        """
        self.imagePath = imagePath
        originalImage = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(originalImage, (settings.TILE_SIZE, settings.TILE_SIZE))
        self.terrains = terrains
        self.connections = connections
        self.occupied = {}
        self.features = features
        self.neighbors = {"N": None, "E": None, "S": None, "W": None}
        self.position = {"X": None, "Y": None}
        self.rotation = 0

    def getPosition(self) -> dict:
        """Get the card's position on the board."""
        return self.position

    def setPosition(self, x: int, y: int) -> None:
        """
        Set the card's position on the board.
        
        Args:
            x: X coordinate of the card
            y: Y coordinate of the card
        """
        self.position = {"X": x, "Y": y}

    def getImage(self) -> pygame.Surface:
        """Get the card's image."""
        return self.image

    def getTerrains(self) -> dict:
        """Get the card's terrain information."""
        return self.terrains

    def getNeighbors(self) -> dict:
        """Get the card's neighboring cards."""
        return self.neighbors

    def getNeighbor(self, direction: str) -> typing.Any:
        """
        Get a specific neighbor card.
        
        Args:
            direction: Direction to get neighbor from
            
        Returns:
            Neighbor card or None
        """
        return self.neighbors[direction]

    def setNeighbor(self, direction: str, neighbor: typing.Any) -> None:
        """
        Set a neighbor card.
        
        Args:
            direction: Direction to set neighbor for
            neighbor: Neighbor card to set
        """
        self.neighbors[direction] = neighbor

    def getConnections(self) -> typing.Optional[dict]:
        """Get the card's internal connections."""
        return self.connections

    def getFeatures(self) -> typing.Any:
        """Get the card's features."""
        return self.features

    def rotate(self) -> None:
        """Rotate the card 90 degrees clockwise."""
        self.rotation = (self.rotation + 90) % 360

        logger.debug(f"Card rotation - {self.rotation}")

        directionMap = {
            "N": "E",
            "E": "S",
            "S": "W",
            "W": "N",
            "C": "C",
        }
        self.terrains = {
            directionMap[dir]: self.terrains[dir]
            for dir in self.terrains
        }

        if self.connections:
            newConnections = {}
            for dir, connectedList in self.connections.items():
                newDir = directionMap[dir]
                newConnections[newDir] = [directionMap[conn] for conn in connectedList]

            self.connections = newConnections

    def serialize(self) -> dict:
        """Serialize the card to a dictionary."""
        return {
            "imagePath": self.imagePath,
            "terrains": self.terrains,
            "connections": self.connections,
            "features": self.features,
            "occupied": self.occupied,
            "neighbors": {
                dir: None if neighbor is None else neighbor.imagePath
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
            imagePath = str(data["imagePath"])
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
            card = Card(
                imagePath=imagePath,
                terrains=terrains,
                connections=connections,
                features=features
            )
        except Exception as e:
            logger.error(f"Failed to initialize Card from data: {data} - {e}")
            raise

        try:
            card.occupied = data.get("occupied", {})
            if not isinstance(card.occupied, dict):
                logger.warning(f"Invalid 'occupied' field type, resetting to empty dict: {card.occupied}")
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
                logger.warning(f"Invalid 'position' format: {pos}, defaulting to None")
                card.position = {"X": None, "Y": None}

            rawRotation = data.get("rotation", 0)
            try:
                card.rotation = int(rawRotation)
            except Exception as e:
                logger.warning(f"Invalid rotation value: {rawRotation}, defaulting to 0 - {e}")
                card.rotation = 0

        except Exception as e:
            logger.error(f"Failed to parse optional card fields: {data} - {e}")
            raise

        return card