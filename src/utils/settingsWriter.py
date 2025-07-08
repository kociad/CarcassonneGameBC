import logging
import settings
from utils.loggingConfig import configureLogging

logger = logging.getLogger(__name__)

def updateResolution(width, height):
    _updateSetting("WINDOW_WIDTH", width)
    _updateSetting("WINDOW_HEIGHT", height)
    logger.debug(f"Updated resolution to {width}x{height}")

def updateFullscreen(enabled):
    _updateSetting("FULLSCREEN", enabled)
    logger.debug(f"Updated FULLSCREEN to {enabled}")

def updateDebug(enabled):
    _updateSetting("DEBUG", enabled)
    settings.DEBUG = enabled  # Update runtime config
    configureLogging()
    logging.getLogger(__name__).debug(f"DEBUG={settings.DEBUG}")
    logger.debug(f"Updated settings.DEBUG to {settings.DEBUG}")

def updateTileSize(value):
    _updateSetting("TILE_SIZE", value)
    settings.TILE_SIZE = value

def updateFigureSize(value):
    _updateSetting("FIGURE_SIZE", value)
    settings.FIGURE_SIZE = value

def updateGridSize(value):
    _updateSetting("GRID_SIZE", value)
    settings.GRID_SIZE = value

def _updateSetting(key, value):
    try:
        with open("src/settings.py", "r") as f:
            lines = f.readlines()

        with open("src/settings.py", "w") as f:
            for line in lines:
                if line.startswith(key):
                    f.write(f"{key} = {value}\n")
                else:
                    f.write(line)
        logger.debug(f"{key} updated to {value}")
    except Exception as e:
        logger.error(f"Failed to update {key}: {e}")
