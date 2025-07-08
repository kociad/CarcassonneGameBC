import logging
import settings

from utils.loggingConfig import configureLogging

logger = logging.getLogger(__name__)

def updateResolution(width, height):
    try:
        with open("src/settings.py", "r") as f:
            lines = f.readlines()

        with open("src/settings.py", "w") as f:
            for line in lines:
                if line.startswith("WINDOW_WIDTH"):
                    f.write(f"WINDOW_WIDTH = {width}\n")
                elif line.startswith("WINDOW_HEIGHT"):
                    f.write(f"WINDOW_HEIGHT = {height}\n")
                else:
                    f.write(line)

        logger.debug(f"Updated resolution to {width}x{height}")
    except Exception as e:
        logger.error(f"Failed to update resolution: {e}")

def updateFullscreen(enabled):
    try:
        with open("src/settings.py", "r") as f:
            lines = f.readlines()

        with open("src/settings.py", "w") as f:
            for line in lines:
                if line.startswith("FULLSCREEN"):
                    f.write(f"FULLSCREEN = {enabled}\n")
                else:
                    f.write(line)

        logger.debug(f"Updated FULLSCREEN to {enabled}")
    except Exception as e:
        logger.error(f"Failed to update FULLSCREEN: {e}")
        
def updateDebug(enabled):
    try:
        with open("src/settings.py", "r") as f:
            lines = f.readlines()
        with open("src/settings.py", "w") as f:
            for line in lines:
                if line.startswith("DEBUG"):
                    f.write(f"DEBUG = {enabled}\n")
                else:
                    f.write(line)
                    
        settings.DEBUG = enabled
        
        configureLogging()
        logging.getLogger(__name__).debug(f"DEBUG={settings.DEBUG}")

        logger.debug(f"Updated settings.DEBUG to {settings.DEBUG}")
    except Exception as e:
        logger.error(f"Failed to update DEBUG: {e}")