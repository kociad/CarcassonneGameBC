# settings.py

# General Game Settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)

# Tile Settings
TILE_SIZE = 110  # Each tile is X pixels
FIGURE_SIZE = 25 # Each figure is Y pixels
GRID_SIZE = 15   # A x A grid for the board

# Meeple Settings
MEEPLE_COLOR_RED = (200, 0, 0)
MEEPLE_COLOR_BLUE = (0, 0, 200)
MEEPLE_COLOR_YELLOW = (200, 200, 0)
MEEPLE_COLOR_GREEN = (0, 200, 0)

# Asset Paths
ASSETS_PATH = "assets/"
TILE_IMAGES_PATH = ASSETS_PATH + "tiles/"
MEEPLE_IMAGES_PATH = ASSETS_PATH + "meeples/"
BACKGROUND_IMAGE_PATH = ASSETS_PATH + "backgrounds/"
SOUND_PATH = ASSETS_PATH + "sounds/"

# Game Rules
MAX_PLAYERS = 4
INITIAL_TILES = 72  # Number of tiles in the game
