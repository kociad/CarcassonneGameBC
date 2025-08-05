import json
import logging
import settings

logger = logging.getLogger(__name__)


def encode_message(action_type: str, data: dict) -> str:
    """Encode a message to JSON format with a defined structure."""
    try:
        return json.dumps({"action": action_type, "payload": data})
    except (TypeError, ValueError) as e:
        logger.debug(f"Failed to serialize message: {e}")
        return ""


def decode_message(raw: str) -> dict | None:
    """Decode a JSON message string into a Python dictionary."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as e:
        logger.debug(f"Failed to parse message: {e}")
        return None
