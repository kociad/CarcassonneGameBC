# settings.py

# General Game Settings
WINDOW_WIDTH = 2560
WINDOW_HEIGHT = 1440
FULLSCREEN = False
FPS = 60

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
TILE_SIZE = 96  # Each tile is X pixels
FIGURE_SIZE = 25  # Each figure is Y pixels
GRID_SIZE = 20  # A x A grid for the board

# Asset Paths
ASSETS_PATH = "src/assets/"
TILE_IMAGES_PATH = ASSETS_PATH + "tiles/"
MEEPLE_IMAGES_PATH = ASSETS_PATH + "meeples/"
BACKGROUND_IMAGE_PATH = ASSETS_PATH + "backgrounds/"
SOUND_PATH = ASSETS_PATH + "sounds/"

# Debug
DEBUG = False

# Player settings (valid for host only)
PLAYERS = ["Pat", "AI_Mat"]

# Network Mode: "host" or "client" or "local"
NETWORK_MODE = "local"

# If client, where to connect, if host, where to listen
HOST_IP = "192.168.88.251"
HOST_PORT = 222  # TCP port to use

# Player index to detect player turn correctly
PLAYER_INDEX = 0


