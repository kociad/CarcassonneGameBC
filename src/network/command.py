import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any
from network.message import encode_message, decode_message

logger = logging.getLogger(__name__)


class GameCommand:
    """Base class for game commands that can be synchronized across the network."""

    def __init__(self,
                 command_type: str,
                 player_index: int,
                 timestamp: Optional[float] = None):
        self.command_id = str(uuid.uuid4())
        self.command_type = command_type
        self.player_index = player_index
        self.timestamp = timestamp or time.time()
        self.sequence_number = 0

    def serialize(self) -> dict:
        """Serialize the command to a dictionary."""
        return {
            "command_id": self.command_id,
            "command_type": self.command_type,
            "player_index": self.player_index,
            "timestamp": self.timestamp,
            "sequence_number": self.sequence_number
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'GameCommand':
        """Deserialize a command from a dictionary."""
        command = cls(data["command_type"], data["player_index"],
                      data["timestamp"])
        command.command_id = data["command_id"]
        command.sequence_number = data["sequence_number"]
        return command


class PlaceCardCommand(GameCommand):
    """Command for placing a card on the board."""

    def __init__(self,
                 player_index: int,
                 x: int,
                 y: int,
                 card_rotation: int,
                 timestamp: Optional[float] = None):
        super().__init__("place_card", player_index, timestamp)
        self.x = x
        self.y = y
        self.card_rotation = card_rotation

    def serialize(self) -> dict:
        data = super().serialize()
        data.update({
            "x": self.x,
            "y": self.y,
            "card_rotation": self.card_rotation
        })
        return data

    @classmethod
    def deserialize(cls, data: dict) -> 'PlaceCardCommand':
        command = cls(data["player_index"], data["x"], data["y"],
                      data["card_rotation"], data["timestamp"])
        command.command_id = data["command_id"]
        command.sequence_number = data["sequence_number"]
        return command


class PlaceFigureCommand(GameCommand):
    """Command for placing a figure on a card."""

    def __init__(self,
                 player_index: int,
                 x: int,
                 y: int,
                 position: str,
                 timestamp: Optional[float] = None):
        super().__init__("place_figure", player_index, timestamp)
        self.x = x
        self.y = y
        self.position = position

    def serialize(self) -> dict:
        data = super().serialize()
        data.update({"x": self.x, "y": self.y, "position": self.position})
        return data

    @classmethod
    def deserialize(cls, data: dict) -> 'PlaceFigureCommand':
        command = cls(data["player_index"], data["x"], data["y"],
                      data["position"], data["timestamp"])
        command.command_id = data["command_id"]
        command.sequence_number = data["sequence_number"]
        return command


class SkipActionCommand(GameCommand):
    """Command for skipping the current action (card placement or figure placement)."""

    def __init__(self,
                 player_index: int,
                 action_type: str,
                 timestamp: Optional[float] = None):
        super().__init__("skip_action", player_index, timestamp)
        self.action_type = action_type

    def serialize(self) -> dict:
        data = super().serialize()
        data.update({"action_type": self.action_type})
        return data

    @classmethod
    def deserialize(cls, data: dict) -> 'SkipActionCommand':
        command = cls(data["player_index"], data["action_type"],
                      data["timestamp"])
        command.command_id = data["command_id"]
        command.sequence_number = data["sequence_number"]
        return command


class RotateCardCommand(GameCommand):
    """Command for rotating the current card."""

    def __init__(self, player_index: int, timestamp: Optional[float] = None):
        super().__init__("rotate_card", player_index, timestamp)

    @classmethod
    def deserialize(cls, data: dict) -> 'RotateCardCommand':
        command = cls(data["player_index"], data["timestamp"])
        command.command_id = data["command_id"]
        command.sequence_number = data["sequence_number"]
        return command


class CommandManager:
    """Manages command execution and synchronization across the network."""

    def __init__(self):
        self.commands: List[GameCommand] = []
        self.next_sequence_number = 1
        self.pendingAcks: Dict[str, float] = {}
        self.ack_timeout = 5.0
        self.max_retries = 3
        self.retry_delays = [1.0, 2.0, 4.0]

    def add_command(self, command: GameCommand) -> None:
        """Add a command to the sequence and assign sequence number."""
        command.sequence_number = self.next_sequence_number
        self.next_sequence_number += 1
        self.commands.append(command)
        logger.debug(
            f"Added command {command.command_type} with sequence {command.sequence_number}"
        )

    def get_commands_since(self, sequence_number: int) -> List[GameCommand]:
        """Get all commands with sequence number greater than the given one."""
        return [
            cmd for cmd in self.commands if cmd.sequence_number > sequence_number
        ]

    def get_latest_sequence_number(self) -> int:
        """Get the latest sequence number."""
        return self.next_sequence_number - 1

    def mark_command_pending_ack(self, command_id: str) -> None:
        """Mark a command as pending acknowledgment."""
        self.pendingAcks[command_id] = time.time()

    def ack_command(self, command_id: str) -> None:
        """Acknowledge receipt of a command."""
        if command_id in self.pendingAcks:
            del self.pendingAcks[command_id]
            logger.debug(f"Acknowledged command {command_id}")

    def get_expired_commands(self) -> List[str]:
        """Get list of command IDs that have exceeded their timeout."""
        current_time = time.time()
        expired = []
        for command_id, timestamp in self.pendingAcks.items():
            if current_time - timestamp > self.ack_timeout:
                expired.append(command_id)
        return expired

    def clear_expired_commands(self) -> None:
        """Remove expired commands from pending acks."""
        expired = self.get_expired_commands()
        for command_id in expired:
            del self.pendingAcks[command_id]
            logger.warning(
                f"Command {command_id} expired without acknowledgment")


def create_command_from_data(data: dict) -> Optional[GameCommand]:
    """Create a command object from serialized data."""
    command_type = data.get("command_type")

    if command_type == "place_card":
        return PlaceCardCommand.deserialize(data)
    elif command_type == "place_figure":
        return PlaceFigureCommand.deserialize(data)
    elif command_type == "skip_action":
        return SkipActionCommand.deserialize(data)
    elif command_type == "rotate_card":
        return RotateCardCommand.deserialize(data)
    else:
        logger.warning(f"Unknown command type: {command_type}")
        return None


def encode_command_message(command: GameCommand,
                         message_type: str = "command") -> str:
    """Encode a command as a network message."""
    return encode_message(message_type, command.serialize())


def decode_command_message(raw_message: str) -> Optional[GameCommand]:
    """Decode a command from a network message."""
    data = decode_message(raw_message)
    if not data:
        return None

    payload = data.get("payload", {})
    return create_command_from_data(payload)
