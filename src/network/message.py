import json
import logging
from settings import DEBUG

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

def encodeMessage(actionType, data):
    """
    Encodes a message to JSON format with a defined structure.
    :param actionType: String identifier of the message purpose.
    :param data: Dictionary or primitive data to be sent.
    :return: JSON-formatted string
    """
    try:
        return json.dumps({
            "action": actionType,
            "payload": data
        })
    except (TypeError, ValueError) as e:
        logger.error(f"[ENCODE] Failed to serialize message: {e}")
        return ""

def decodeMessage(raw):
    """
    Decodes a JSON message string into a Python dictionary.
    :param raw: JSON-formatted string
    :return: dict with 'action' and 'payload', or None if invalid
    """
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"[DECODE] Failed to parse message: {e}")
        return None
