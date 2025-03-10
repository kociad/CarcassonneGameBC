import pygame

from settings import TILE_SIZE

class Card:
    """
    Represents a tile (card) in the game with an image and terrain properties.
    """
    
    def __init__(self, image_path, terrain):
        """
        Initializes a tile with an image and terrain data.
        :param image_path: Path to the tile image.
        :param terrain: Dictionary defining terrain types for each side.
        """
        original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))  # Resize to match TILE_SIZE
        self.terrains = terrain  # Dictionary with terrain info (e.g., {"N": "city", "S": "road"})
        self.connections = [] # Currently unused
        self.occupied = {} # Currently unused
        self.features = set() # Currently unused
    
    def rotate(self):
        """
        Rotates the tile 90 degrees clockwise.
        """
        self.image = pygame.transform.rotate(self.image, -90)
        
        # Rotate terrain mapping
        new_terrain = {
            "N": self.terrains["W"],
            "E": self.terrains["N"],
            "S": self.terrains["E"],
            "W": self.terrains["S"],
        }
        self.terrains = new_terrain
