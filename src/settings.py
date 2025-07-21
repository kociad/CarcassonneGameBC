#Fixed variables
FPS = 60

ASSETS_PATH = "src/assets/"
TILE_IMAGES_PATH = ASSETS_PATH + "tiles/"
MEEPLE_IMAGES_PATH = ASSETS_PATH + "meeples/"
BACKGROUND_IMAGE_PATH = ASSETS_PATH + "backgrounds/"
SOUND_PATH = ASSETS_PATH + "sounds/"

#Session defaults
#Player settings (valid for host only)
PLAYERS = ["Adam", "Benedict", "Cecil", "David", "Ernest", "Francis"]

# Network Mode: "host" or "client" or "local"
NETWORK_MODE = "local"

# If client, where to connect, if host, where to listen
HOST_IP = "0.0.0.0"
HOST_PORT = 222  # TCP port to use

# Player index to detect player turn correctly
PLAYER_INDEX = 0

# General Game Settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FULLSCREEN = False

# Apply dynamic fullscreen resolution override if needed
if FULLSCREEN:
    try:
        import pygame
        pygame.display.init()
        info = pygame.display.Info()
        WINDOW_WIDTH = info.current_w
        WINDOW_HEIGHT = info.current_h
        pygame.display.quit()
    except Exception as e:
        print(f"Failed to detect fullscreen resolution: {e}")

# Tile Settings
TILE_SIZE = 96
FIGURE_SIZE = 25
GRID_SIZE = 20
SIDEBAR_WIDTH = 200

# Debug
DEBUG = False


