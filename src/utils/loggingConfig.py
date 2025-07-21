import importlib
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

def configureLogging():
    """
    Configure logging for the application with file and console output.
    Also sets up global exception handling.
    """
    
    # Import settings_manager to check DEBUG setting
    from utils.settingsManager import settings_manager
    
    # Always configure logging infrastructure
    logsDir = Path("logs")
    logsDir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logFilename = logsDir / f"carcassonne_{timestamp}.log"
    
    # Configure root logger with both file and console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logFilename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set initial logging state based on DEBUG setting
    updateLoggingLevel()
    
    # Set up global exception handling
    setupExceptionLogging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured. Log file: {logFilename}")

def updateLoggingLevel():
    """
    Update logging level based on current DEBUG setting.
    Call this when DEBUG setting changes at runtime.
    """
    from utils.settingsManager import settings_manager
    
    debugEnabled = settings_manager.get("DEBUG", True)
    
    if debugEnabled:
        # Enable logging
        logging.disable(logging.NOTSET)
        logger = logging.getLogger(__name__)
        logger.info("Debug logging enabled")
    else:
        # Disable all logging
        logging.disable(logging.CRITICAL)

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