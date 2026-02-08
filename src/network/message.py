import json
import logging
from typing import Union

logger = logging.getLogger(__name__)
HEADER_SIZE = 4


def encode_message(action_type: str, data: dict) -> bytes:
    """Encode a message to a framed JSON payload with a length prefix."""
    try:
        payload = json.dumps({"action": action_type, "payload": data}).encode(
            "utf-8")
        length = len(payload).to_bytes(HEADER_SIZE, byteorder="big")
        return length + payload
    except (TypeError, ValueError) as e:
        logger.debug(f"Failed to serialize message: {e}")
        return b""


def decode_message(raw: Union[str, bytes]) -> dict | None:
    """Decode a JSON message payload into a Python dictionary."""
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as e:
        logger.debug(f"Failed to parse message: {e}")
        return None


def extract_framed_messages(buffer: bytearray,
                            max_message_size: int) -> list[bytes]:
    """Extract length-prefixed message payloads from a buffer."""
    messages: list[bytes] = []
    offset = 0
    buffer_len = len(buffer)
    while buffer_len - offset >= HEADER_SIZE:
        length = int.from_bytes(buffer[offset:offset + HEADER_SIZE],
                                byteorder="big")
        if length <= 0:
            raise ValueError("Invalid message length.")
        if length > max_message_size:
            raise ValueError("Message length exceeds maximum size.")
        frame_end = offset + HEADER_SIZE + length
        if buffer_len < frame_end:
            break
        messages.append(bytes(buffer[offset + HEADER_SIZE:frame_end]))
        offset = frame_end
    if offset:
        del buffer[:offset]
    return messages
