import importlib
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Definovat nový SCORING level
SCORING_LEVEL = 25  # Mezi INFO (20) a WARNING (30)
logging.addLevelName(SCORING_LEVEL, "SCORING")

def scoring(self, message, *args, **kwargs):
    """Log 'message % args' with severity 'SCORING'."""
    if self.isEnabledFor(SCORING_LEVEL):
        self._log(SCORING_LEVEL, message, args, **kwargs)

# Přidat SCORING metodu do Logger třídy
logging.Logger.scoring = scoring

def configureLogging():
    """
    Configure logging for the application with file and console output.
    Also sets up global exception handling.
    """
    
    # Import settings_manager to check DEBUG setting
    from utils.settingsManager import settings_manager
    
    # Check if DEBUG is enabled
    debugEnabled = settings_manager.get("DEBUG", False)
    
    # Prepare handlers list
    handlers = [logging.StreamHandler(sys.stdout)]  # Always have console output
    
    # Only add file handler if DEBUG is enabled
    if debugEnabled:
        # Create logs directory only when needed
        logsDir = Path("logs")
        logsDir.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logFilename = logsDir / f"carcassonne_{timestamp}.log"
        
        # Add file handler
        handlers.append(logging.FileHandler(logFilename, encoding='utf-8'))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Set initial logging state based on DEBUG setting
    updateLoggingLevel()
    
    # Set up global exception handling
    setupExceptionLogging()
    
    logger = logging.getLogger(__name__)
    if debugEnabled:
        logger.debug(f"Logging configured with file output: {logFilename}")
    else:
        logger.info("Logging configured (console only - DEBUG disabled)")

def updateLoggingLevel():
    """
    Update logging level based on current DEBUG setting.
    INFO and above are always visible, DEBUG only when DEBUG=True
    """
    from utils.settingsManager import settings_manager
    
    debugEnabled = settings_manager.get("DEBUG", True)
    
    if debugEnabled:
        # Enable all logging (including DEBUG)
        logging.disable(logging.NOTSET)
        # Set console handler to DEBUG level
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug("Debug logging enabled - all messages visible")
    else:
        # Disable only DEBUG level, keep INFO and above
        logging.disable(logging.NOTSET)  # First enable all
        # Set console handler to INFO level (hide DEBUG messages)
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Debug logging disabled - INFO and above messages visible")

def setupExceptionLogging():
    """
    Set up global exception handling to log all unhandled exceptions.
    """
    def handleException(excType, excValue, excTraceback):
        # Don't log KeyboardInterrupt (Ctrl+C)
        if issubclass(excType, KeyboardInterrupt):
            sys.__excepthook__(excType, excValue, excTraceback)
            return
        
        logger = logging.getLogger("UNHANDLED_EXCEPTION")
        
        # Format the exception with full traceback
        tbLines = traceback.format_exception(excType, excValue, excTraceback)
        tbText = ''.join(tbLines)
        
        # Log with CRITICAL level
        logger.critical("Unhandled exception occurred!")
        logger.critical(f"Exception Type: {excType.__name__}")
        logger.critical(f"Exception Message: {str(excValue)}")
        logger.critical("Full Traceback:")
        logger.critical(tbText)
        
        # Call the default handler to maintain normal behavior
        sys.__excepthook__(excType, excValue, excTraceback)
    
    # Set our custom exception handler
    sys.excepthook = handleException

def logError(message, exception=None):
    """
    Quick function to log an error with optional exception details.
    """
    logger = logging.getLogger("ERROR_HANDLER")
    logger.error(message)
    
    if exception:
        logger.error(f"Exception type: {type(exception).__name__}")
        logger.error(f"Exception message: {str(exception)}")
        logger.error("Full traceback:", exc_info=True)
        
gameLogInstance = None
gameLogHandler = None

def setGameLogInstance(gameLog):
    """Set the game log instance for UI logging"""
    global gameLogInstance, gameLogHandler
    gameLogInstance = gameLog
    
    # Now add the handler since we have the instance
    if gameLogHandler is None:
        gameLogHandler = GameLogHandler()
        gameLogHandler.setLevel(logging.DEBUG)  # Capture all levels
        
        # Add to root logger
        rootLogger = logging.getLogger()
        rootLogger.addHandler(gameLogHandler)
        
        logger = logging.getLogger(__name__)
        logger.debug("Game log handler added to root logger")

class GameLogHandler(logging.Handler):
    """Custom logging handler that sends messages to the game log UI"""
    
    def emit(self, record):
        global gameLogInstance
        if gameLogInstance is None:
            return
            
        try:
            # Map logging levels to our log levels
            levelMapping = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                SCORING_LEVEL: "SCORING",  # ⭐ Přidáno SCORING level
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "ERROR"
            }
            
            level = levelMapping.get(record.levelno, "INFO")
            
            # Get clean message without logger name prefix
            cleanMessage = record.getMessage()
            
            # Add logger name for DEBUG messages to help with debugging
            if level == "DEBUG":
                loggerName = record.name.split('.')[-1]  # Get last part of logger name
                cleanMessage = f"[{loggerName}] {cleanMessage}"
            
            # Add to game log
            gameLogInstance.addEntry(cleanMessage, level)
            
        except Exception as e:
            # Don't let logging errors crash the game
            pass