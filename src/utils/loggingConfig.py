import importlib
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
import typing

SCORING_LEVEL = 26
logging.addLevelName(SCORING_LEVEL, "SCORING")


def scoring(self, message, *args, **kwargs):
    """Log 'message % args' with severity 'SCORING'."""
    if self.isEnabledFor(SCORING_LEVEL):
        self._log(SCORING_LEVEL, message, args, **kwargs)


logging.Logger.scoring = scoring


def configureLogging() -> None:
    """Configure logging for the application with file and console output and global exception handling."""
    from utils.settingsManager import settingsManager
    debugEnabled = settingsManager.get("DEBUG", False)
    logToConsole = settingsManager.get("LOG_TO_CONSOLE", True)
    handlers = []
    logFilename = None
    if debugEnabled and logToConsole:
        handlers.append(logging.StreamHandler(sys.stdout))
    if debugEnabled:
        logsDir = Path("logs")
        logsDir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logFilename = logsDir / f"carcassonne_{timestamp}.log"
        handlers.append(logging.FileHandler(logFilename, encoding='utf-8'))
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers)
    updateLoggingLevel()
    setupExceptionLogging()
    logger = logging.getLogger(__name__)
    if debugEnabled:
        msg = f"Logging configured with file output: {logFilename}"
        if logToConsole:
            msg += " and console output"
        logger.debug(msg)
    """
    else:
        logger.info("Logging configured (no console output - DEBUG disabled)")
    """


def updateLoggingLevel() -> None:
    """Update logging level based on current DEBUG setting."""
    from utils.settingsManager import settingsManager
    debugEnabled = settingsManager.get("DEBUG", True)
    if debugEnabled:
        logging.disable(logging.NOTSET)
        for handler in logging.getLogger().handlers:
            if isinstance(
                    handler,
                    logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug("Debug logging enabled - all messages visible")
    else:
        logging.disable(logging.NOTSET)
        for handler in logging.getLogger().handlers:
            if isinstance(
                    handler,
                    logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Debug logging disabled - INFO and above messages visible")


def setupExceptionLogging():
    """Set up global exception handling to log all unhandled exceptions."""

    def handleException(excType, excValue, excTraceback):
        if issubclass(excType, KeyboardInterrupt):
            sys.__excepthook__(excType, excValue, excTraceback)
            return
        logger = logging.getLogger("UNHANDLED_EXCEPTION")
        tbLines = traceback.format_exception(excType, excValue, excTraceback)
        tbText = ''.join(tbLines)
        logger.critical("Unhandled exception occurred!")
        logger.critical(f"Exception Type: {excType.__name__}")
        logger.critical(f"Exception Message: {str(excValue)}")
        logger.critical("Full Traceback:")
        logger.critical(tbText)
        sys.__excepthook__(excType, excValue, excTraceback)

    sys.excepthook = handleException


def logError(message: str, exception: Exception) -> None:
    """Log an error with optional exception details."""
    logger = logging.getLogger("ERROR_HANDLER")
    logger.error(message)
    if exception:
        logger.error(f"Exception type: {type(exception).__name__}")
        logger.error(f"Exception message: {str(exception)}")
        logger.error("Full traceback:", exc_info=True)


gameLogInstance = None
gameLogHandler = None


def setGameLogInstance(gameLog: typing.Any) -> None:
    """Set the game log instance for UI logging."""
    global gameLogInstance, gameLogHandler
    gameLogInstance = gameLog
    if gameLogHandler is None:
        gameLogHandler = GameLogHandler()
        gameLogHandler.setLevel(logging.DEBUG)
        rootLogger = logging.getLogger()
        rootLogger.addHandler(gameLogHandler)
        logger = logging.getLogger(__name__)
        logger.debug("Game log handler added to root logger")


class GameLogHandler(logging.Handler):
    """Custom logging handler that sends messages to the game log UI."""

    def emit(self, record):
        global gameLogInstance
        if gameLogInstance is None:
            return
        try:
            levelMapping = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                SCORING_LEVEL: "SCORING",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "ERROR"
            }
            level = levelMapping.get(record.levelno, "INFO")
            if level not in ("INFO", "SCORING"):
                return
            cleanMessage = record.getMessage()
            if level == "DEBUG":
                loggerName = record.name.split('.')[-1]
                cleanMessage = f"[{loggerName}] {cleanMessage}"
            gameLogInstance.addEntry(cleanMessage, level)
        except Exception:
            pass
