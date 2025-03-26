import pygame

from settings import TILE_SIZE

class Card:
    """
    Represents a tile (card) in the game with an image and terrain properties.
    """
    
    def __init__(self, image_path, terrains, connections):
        """
        Initializes a tile with an image and terrain data.
        :param image_path: Path to the tile image.
        :param terrain: Dictionary defining terrain types for each side.
        """
        original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))  # Resize to match TILE_SIZE
        self.terrains = terrains  # Dictionary with terrain info (e.g., {"N": "city", "S": "road"})
        self.connections = connections
        self.occupied = {} # Currently unused
        self.features = set() # Currently unused
        self.neighbors = {"N": None, "E": None, "S": None, "W": None}
    
    def getImage(self):
        """
        Card image getter method
        :return: Card image
        """
        return self.image
        
    def getTerrains(self):
        """
        Card terrains getter method
        :return: Dictionary with terrain info (e.g., {"N": "city", "S": "road"})
        """
        return self.terrains
        
    def getNeighbors(self):
        """
        Card neighbors getter method
        :return: Neighbors dictationary
        """
        return self.neighbors
        
    def getNeighbor(self, direction):
        """
        Card neighbor getter method for specific direction
        :return: Neighbor card or None
        """
        return self.neighbors[direction]
        
    def setNeighbor(self, direction, neighbor):
        """
        Card neighbor setter method
        :param direction: Direction which neighbor is to be added
        :param neighbor: Neighbor card to be added
        """
        self.neighbors[direction] = neighbor
        
    def getConnections(self):
        """
        Card connections getter method
        :return: Dict with connections within the card
        """
        return self.connections
    
    def rotate(self):
        """
        Rotates the card 90 degrees clockwise.
        """
        self.image = pygame.transform.rotate(self.image, -90)

        # Rotate terrain mapping
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

        # Rotate connections
        if self.connections:
            newConnections = {}
            for dir, connectedList in self.connections.items():
                newDir = directionMap[dir]
                newConnections[newDir] = [directionMap[conn] for conn in connectedList]

            self.connections = newConnections

    def canPlaceFigure(self, figure):
        return True # To be implemented