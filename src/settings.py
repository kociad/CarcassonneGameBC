# settings.py

# General Game Settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60

# Tile Settings
TILE_SIZE = 96  # Each tile is X pixels
FIGURE_SIZE = 25 # Each figure is Y pixels
GRID_SIZE = 20   # A x A grid for the board

# Asset Paths
ASSETS_PATH = "src/assets/"
TILE_IMAGES_PATH = ASSETS_PATH + "tiles/"
MEEPLE_IMAGES_PATH = ASSETS_PATH + "meeples/"
BACKGROUND_IMAGE_PATH = ASSETS_PATH + "backgrounds/"
SOUND_PATH = ASSETS_PATH + "sounds/"

# Debug
DEBUG = True

# Player settings
PLAYERS = ["Player1","Player2"]

# Network Mode: "host" or "client" or "local"
NETWORK_MODE = "host"  # or "client" or "local"

# If client, where to connect
HOST_IP = "192.168.88.251"
HOST_PORT = 222  # TCP port to use

# Player index to detect player turn correctly
PLAYER_INDEX = 0