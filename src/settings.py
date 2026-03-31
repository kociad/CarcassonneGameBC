import os

# Fixed variables
FPS = 60

ASSETS_PATH = "src/assets/"
TILE_IMAGES_PATH = ASSETS_PATH + "tiles/"
FIGURE_IMAGES_PATH = ASSETS_PATH + "meeples/"
BACKGROUND_IMAGE_PATH = ASSETS_PATH + "backgrounds/"
SOUND_PATH = ASSETS_PATH + "sounds/"
ICONS_PATH = ASSETS_PATH + "icons/"
LOGOS_PATH = ASSETS_PATH + "logos/"

# Tile Settings
TILE_SIZE = 110
FIGURE_SIZE = 25
GRID_SIZE = 20
SIDEBAR_WIDTH = 300

# Session defaults
# Player settings (valid for host only)
PLAYERS = [
    "Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"
]

SELECTED_CARD_SETS = ["1_base_game"]

# Network Mode: "host" or "client" or "local"
NETWORK_MODE = "local"

# If client, where to connect, if host, where to listen
HOST_IP = "192.168.88.251"
HOST_PORT = 2222  # TCP port to use

# Player index to detect player turn correctly
PLAYER_INDEX = 0

# General Game Settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FULLSCREEN = False
SHOW_VALID_PLACEMENTS = True

# Debug
DEBUG = False
LOG_TO_CONSOLE = False
GAME_LOG_MAX_ENTRIES = 10000
MAX_RETRY_ATTEMPTS = 3

# AI Settings
AI_USE_SIMULATION = True
AI_STRATEGIC_CANDIDATES = 3
AI_THINKING_SPEED = -1


# ---------------------------------------------------------------------------
# Debug/testing-only environment overrides
#
# These are intentionally lightweight so local loopback multiplayer tests can
# override networking settings without editing this file manually.
# ---------------------------------------------------------------------------
NETWORK_MODE = os.getenv("NETWORK_MODE", NETWORK_MODE)
HOST_IP = os.getenv("HOST_IP", HOST_IP)
HOST_PORT = int(os.getenv("HOST_PORT", str(HOST_PORT)))
PLAYER_INDEX = int(os.getenv("PLAYER_INDEX", str(PLAYER_INDEX)))
DEBUG = os.getenv("DEBUG", str(DEBUG)).strip().lower() in {"1", "true", "yes", "on"}


# Apply dynamic fullscreen resolution override if needed
if FULLSCREEN:
    try:
        import pygame
        pygame.display.init()
        info = pygame.display.Info()
        WINDOW_WIDTH = info.current_w
        WINDOW_HEIGHT = info.current_h
    except Exception as e:
        print(f"Failed to detect fullscreen resolution: {e}")
