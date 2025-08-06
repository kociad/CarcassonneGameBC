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


def configure_logging() -> None:
    """Configure logging for the application with file and console output and global exception handling."""
    from utils.settingsManager import settings_manager
    debug_enabled = settings_manager.get("DEBUG", False)
    log_to_console = settings_manager.get("LOG_TO_CONSOLE", True)
    handlers = []
    log_filename = None
    if debug_enabled and log_to_console:
        handlers.append(logging.StreamHandler(sys.stdout))
    if debug_enabled:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = logs_dir / f"carcassonne_{timestamp}.log"
        handlers.append(logging.FileHandler(log_filename, encoding='utf-8'))
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers)
    update_logging_level()
    setup_exception_logging()
    logger = logging.getLogger(__name__)
    if debug_enabled:
        msg = f"Logging configured with file output: {log_filename}"
        if log_to_console:
            msg += " and console output"
        logger.debug(msg)
    """
    else:
        logger.info("Logging configured (no console output - DEBUG disabled)")
    """


def update_logging_level() -> None:
    """Update logging level based on current DEBUG setting."""
    from utils.settingsManager import settings_manager
    debug_enabled = settings_manager.get("DEBUG", True)
    if debug_enabled:
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


def setup_exception_logging():
    """Set up global exception handling to log all unhandled exceptions."""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger = logging.getLogger("UNHANDLED_EXCEPTION")
        tb_lines = traceback.format_exception(exc_type, exc_value,
                                              exc_traceback)
        tb_text = ''.join(tb_lines)
        logger.critical("Unhandled exception occurred!")
        logger.critical(f"Exception Type: {exc_type.__name__}")
        logger.critical(f"Exception Message: {str(exc_value)}")
        logger.critical("Full Traceback:")
        logger.critical(tb_text)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def log_error(message: str, exception: Exception) -> None:
    """Log an error with optional exception details."""
    logger = logging.getLogger("ERROR_HANDLER")
    logger.error(message)
    if exception:
        logger.error(f"Exception type: {type(exception).__name__}")
        logger.error(f"Exception message: {str(exception)}")
        logger.error("Full traceback:", exc_info=True)


game_log_instance = None
game_log_handler = None


def set_game_log_instance(game_log: typing.Any) -> None:
    """Set the game log instance for UI logging."""
    global game_log_instance, game_log_handler
    game_log_instance = game_log
    if game_log_handler is None:
        game_log_handler = GameLogHandler()
        game_log_handler.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.addHandler(game_log_handler)
        logger = logging.getLogger(__name__)
        logger.debug("Game log handler added to root logger")


class GameLogHandler(logging.Handler):
    """Custom logging handler that sends messages to the game log UI."""

    def emit(self, record):
        global game_log_instance
        if game_log_instance is None:
            return
        try:
            level_mapping = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                SCORING_LEVEL: "SCORING",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "ERROR"
            }
            level = level_mapping.get(record.levelno, "INFO")
            if level not in ("INFO", "SCORING"):
                return
            clean_message = record.getMessage()
            if level == "DEBUG":
                logger_name = record.name.split('.')[-1]
                clean_message = f"[{logger_name}] {clean_message}"
            game_log_instance.add_entry(clean_message, level)
        except Exception:
            pass
