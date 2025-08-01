import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any
from network.message import encodeMessage, decodeMessage

logger = logging.getLogger(__name__)


class GameCommand:
    """Base class for game commands that can be synchronized across the network."""

    def __init__(self,
                 commandType: str,
                 playerIndex: int,
                 timestamp: Optional[float] = None):
        self.commandId = str(uuid.uuid4())
        self.commandType = commandType
        self.playerIndex = playerIndex
        self.timestamp = timestamp or time.time()
        self.sequenceNumber = 0

    def serialize(self) -> dict:
        """Serialize the command to a dictionary."""
        return {
            "command_id": self.commandId,
            "command_type": self.commandType,
            "player_index": self.playerIndex,
            "timestamp": self.timestamp,
            "sequence_number": self.sequenceNumber
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'GameCommand':
        """Deserialize a command from a dictionary."""
        command = cls(data["command_type"], data["player_index"],
                      data["timestamp"])
        command.commandId = data["command_id"]
        command.sequenceNumber = data["sequence_number"]
        return command


class PlaceCardCommand(GameCommand):
    """Command for placing a card on the board."""

    def __init__(self,
                 playerIndex: int,
                 x: int,
                 y: int,
                 cardRotation: int,
                 timestamp: Optional[float] = None):
        super().__init__("place_card", playerIndex, timestamp)
        self.x = x
        self.y = y
        self.cardRotation = cardRotation

    def serialize(self) -> dict:
        data = super().serialize()
        data.update({
            "x": self.x,
            "y": self.y,
            "card_rotation": self.cardRotation
        })
        return data

    @classmethod
    def deserialize(cls, data: dict) -> 'PlaceCardCommand':
        command = cls(data["player_index"], data["x"], data["y"],
                      data["card_rotation"], data["timestamp"])
        command.commandId = data["command_id"]
        command.sequenceNumber = data["sequence_number"]
        return command


class PlaceFigureCommand(GameCommand):
    """Command for placing a figure on a card."""

    def __init__(self,
                 playerIndex: int,
                 x: int,
                 y: int,
                 position: str,
                 timestamp: Optional[float] = None):
        super().__init__("place_figure", playerIndex, timestamp)
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
        command.commandId = data["command_id"]
        command.sequenceNumber = data["sequence_number"]
        return command


class SkipActionCommand(GameCommand):
    """Command for skipping the current action (card placement or figure placement)."""

    def __init__(self,
                 playerIndex: int,
                 actionType: str,
                 timestamp: Optional[float] = None):
        super().__init__("skip_action", playerIndex, timestamp)
        self.actionType = actionType

    def serialize(self) -> dict:
        data = super().serialize()
        data.update({"action_type": self.actionType})
        return data

    @classmethod
    def deserialize(cls, data: dict) -> 'SkipActionCommand':
        command = cls(data["player_index"], data["action_type"],
                      data["timestamp"])
        command.commandId = data["command_id"]
        command.sequenceNumber = data["sequence_number"]
        return command


class RotateCardCommand(GameCommand):
    """Command for rotating the current card."""

    def __init__(self, playerIndex: int, timestamp: Optional[float] = None):
        super().__init__("rotate_card", playerIndex, timestamp)

    @classmethod
    def deserialize(cls, data: dict) -> 'RotateCardCommand':
        command = cls(data["player_index"], data["timestamp"])
        command.commandId = data["command_id"]
        command.sequenceNumber = data["sequence_number"]
        return command


class CommandManager:
    """Manages command execution and synchronization across the network."""

    def __init__(self):
        self.commands: List[GameCommand] = []
        self.nextSequenceNumber = 1
        self.pendingAcks: Dict[str, float] = {}
        self.ackTimeout = 5.0
        self.maxRetries = 3
        self.retryDelays = [1.0, 2.0, 4.0]

    def addCommand(self, command: GameCommand) -> None:
        """Add a command to the sequence and assign sequence number."""
        command.sequenceNumber = self.nextSequenceNumber
        self.nextSequenceNumber += 1
        self.commands.append(command)
        logger.debug(
            f"Added command {command.commandType} with sequence {command.sequenceNumber}"
        )

    def getCommandsSince(self, sequenceNumber: int) -> List[GameCommand]:
        """Get all commands with sequence number greater than the given one."""
        return [
            cmd for cmd in self.commands if cmd.sequenceNumber > sequenceNumber
        ]

    def getLatestSequenceNumber(self) -> int:
        """Get the latest sequence number."""
        return self.nextSequenceNumber - 1

    def markCommandPendingAck(self, commandId: str) -> None:
        """Mark a command as pending acknowledgment."""
        self.pendingAcks[commandId] = time.time()

    def ackCommand(self, commandId: str) -> None:
        """Acknowledge receipt of a command."""
        if commandId in self.pendingAcks:
            del self.pendingAcks[commandId]
            logger.debug(f"Acknowledged command {commandId}")

    def getExpiredCommands(self) -> List[str]:
        """Get list of command IDs that have exceeded their timeout."""
        currentTime = time.time()
        expired = []
        for commandId, timestamp in self.pendingAcks.items():
            if currentTime - timestamp > self.ackTimeout:
                expired.append(commandId)
        return expired

    def clearExpiredCommands(self) -> None:
        """Remove expired commands from pending acks."""
        expired = self.getExpiredCommands()
        for commandId in expired:
            del self.pendingAcks[commandId]
            logger.warning(
                f"Command {commandId} expired without acknowledgment")


def createCommandFromData(data: dict) -> Optional[GameCommand]:
    """Create a command object from serialized data."""
    commandType = data.get("command_type")

    if commandType == "place_card":
        return PlaceCardCommand.deserialize(data)
    elif commandType == "place_figure":
        return PlaceFigureCommand.deserialize(data)
    elif commandType == "skip_action":
        return SkipActionCommand.deserialize(data)
    elif commandType == "rotate_card":
        return RotateCardCommand.deserialize(data)
    else:
        logger.warning(f"Unknown command type: {commandType}")
        return None


def encodeCommandMessage(command: GameCommand,
                         messageType: str = "command") -> str:
    """Encode a command as a network message."""
    return encodeMessage(messageType, command.serialize())


def decodeCommandMessage(rawMessage: str) -> Optional[GameCommand]:
    """Decode a command from a network message."""
    data = decodeMessage(rawMessage)
    if not data:
        return None

    payload = data.get("payload", {})
    return createCommandFromData(payload)
