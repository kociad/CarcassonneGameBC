import socket
import threading
import logging
import typing
import time
from network.message import decodeMessage, encodeMessage
from network.command import CommandManager, decodeCommandMessage, encodeCommandMessage
from models.gameSession import GameSession
from utils.settingsManager import settingsManager

logger = logging.getLogger(__name__)

BUFFER_SIZE = 4096

class NetworkConnection:
    """Handles network connections for host and client modes."""
    def __init__(self) -> None:
        self.networkMode = settingsManager.get("NETWORK_MODE", "local")
        self.running = False
        self.connections = []
        self.socket = None
        self.commandManager = CommandManager()
        
        self.onClientConnected = None
        self.onClientSubmittedTurn = None
        self.onInitialGameStateReceived = None
        self.onSyncGameState = None
        self.onJoinFailed = None
        self.onJoinRejected = None
        self.onPlayerClaimed = None
        self.onStartGame = None
        self.onClientDisconnected = None
        self.onHostDisconnected = None
        
        self.onCommandReceived = None
        self.onCommandAck = None
        self.onSyncRequest = None
        
        if self.networkMode == "local":
            logger.debug("Running in local mode. Networking is disabled.")
            return
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.networkMode == "host":
            try:
                hostIp = settingsManager.get("HOST_IP", "0.0.0.0")
                hostPort = settingsManager.get("HOST_PORT", 222)
                self.socket.bind((hostIp, hostPort))
                self.socket.listen()
                logger.debug(f"Host listening on {hostIp}:{hostPort}...")
                threading.Thread(target=self.acceptConnections, daemon=True).start()
                threading.Thread(target=self._commandCleanupLoop, daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to bind socket: {e}")
        elif self.networkMode == "client":
            try:
                hostIp = settingsManager.get("HOST_IP", "0.0.0.0")
                hostPort = settingsManager.get("HOST_PORT", 222)
                self.socket.connect((hostIp, hostPort))
                logger.debug(f"Connected to host at {hostIp}:{hostPort}")
                threading.Thread(target=self.receiveLoop, args=(self.socket,), daemon=True).start()
                threading.Thread(target=self._commandCleanupLoop, daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to connect to host: {e}")

    def acceptConnections(self):
        """Accept incoming client connections (host mode)."""
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.connections.append(conn)
                logger.debug(f"Connection received and established with {addr}")
                if self.onClientConnected:
                    self.onClientConnected(conn)
                threading.Thread(target=self.receiveLoop, args=(conn,), daemon=True).start()
            except Exception as e:
                if self.running:
                    logger.exception(f"Failed to accept connection: {e}")
                break

    def receiveLoop(self, conn):
        """Receive and process messages from a connection."""
        buffer = ""
        while self.running:
            try:
                data = conn.recv(BUFFER_SIZE).decode()
                if not data:
                    logger.debug("Connection closed by peer")
                    self._handleConnectionDrop(conn)
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        logger.debug(f"Receiving message: {line}")
                        self.onMessageReceived(line, conn)
            except Exception as e:
                if self.running:
                    logger.exception(f"Socket error: {e}")
                self._handleConnectionDrop(conn)
                break

    def onMessageReceived(self, message, conn=None):
        """Handle a received message and dispatch to the appropriate handler."""
        parsed = decodeMessage(message)
        if not parsed:
            return
        action = parsed.get("action")
        payload = parsed.get("payload")
        
        if action == "command":
            logger.debug("Received command from network")
            command = decodeCommandMessage(message)
            if command and self.onCommandReceived:
                self.onCommandReceived(command, conn)
            ackMessage = encodeMessage("command_ack", {"command_id": command.commandId})
            if conn:
                try:
                    conn.sendall((ackMessage + "\n").encode())
                except Exception as e:
                    logger.exception(f"Failed to send command ack: {e}")
            elif self.networkMode == "client":
                self.sendToHost(ackMessage)
        elif action == "command_ack":
            logger.debug("Received command acknowledgment")
            commandId = payload.get("command_id")
            if commandId:
                self.commandManager.ackCommand(commandId)
                if self.onCommandAck:
                    self.onCommandAck(commandId)
        elif action == "sync_request":
            logger.debug("Received sync request")
            if self.onSyncRequest:
                self.onSyncRequest(payload, conn)
        elif action == "init_game_state":
            logger.debug("Received initial game state from host")
            if self.onInitialGameStateReceived:
                self.onInitialGameStateReceived(payload)
        elif action == "ack_game_state":
            logger.debug("Client confirmed receiving game state: %s", payload)
        elif action == "player_claimed" and self.networkMode == "host":
            logger.debug("Received player claimed from client")
            if self.onPlayerClaimed:
                self.onPlayerClaimed(payload, conn)
        elif action == "submit_turn" and self.networkMode == "host":
            logger.debug("Received submitted turn from client")
            if self.onClientSubmittedTurn:
                self.onClientSubmittedTurn(payload)
        elif action == "sync_game_state":
            logger.debug("Received updated game state from host")
            if self.onSyncGameState:
                self.onSyncGameState(payload)
        elif action == "join_failed" and self.networkMode == "host":
            logger.debug("Received join_failed from client")
            if self.onJoinFailed:
                self.onJoinFailed(payload, conn)
        elif action == "start_game" and self.networkMode == "client":
            logger.debug("Received start_game from host")
            if self.onStartGame:
                self.onStartGame(payload)
        elif action == "join_rejected" and self.networkMode == "client":
            logger.debug("Received join_rejected from host")
            if self.onJoinRejected:
                self.onJoinRejected(payload)

    def sendToAll(self, message):
        """Send a message to all connected clients (host mode)."""
        if self.networkMode != "host":
            return
        logger.debug(f"Sending message to all: {message}")
        for conn in self.connections[:]:
            try:
                conn.sendall((message + "\n").encode())
            except Exception as e:
                logger.exception(f"Failed to send message to client, removing connection: {e}")
                try:
                    conn.close()
                except:
                    pass
                if conn in self.connections:
                    self.connections.remove(conn)

    def sendToHost(self, message):
        """Send a message to the host (client mode)."""
        if self.networkMode != "client":
            return
        try:
            logger.debug(f"Sending message to host: {message}")
            self.socket.sendall((message + "\n").encode())
        except Exception as e:
            logger.exception(f"Failed to send to host: {e}")

    def sendCommand(self, command):
        """Send a command to the network with acknowledgment tracking."""
        if self.networkMode == "local":
            return
            
        message = encodeCommandMessage(command)
        self.commandManager.markCommandPendingAck(command.commandId)
        
        if self.networkMode == "host":
            for conn in self.connections[:]:
                try:
                    conn.sendall((message + "\n").encode())
                except Exception as e:
                    logger.exception(f"Failed to send command to client: {e}")
                    try:
                        conn.close()
                    except:
                        pass
                    if conn in self.connections:
                        self.connections.remove(conn)
        elif self.networkMode == "client":
            self.sendToHost(message)
            
        logger.debug(f"Sent command {command.commandType} with ID {command.commandId}")

    def _commandCleanupLoop(self):
        """Background thread to clean up expired commands."""
        while self.running:
            try:
                self.commandManager.clearExpiredCommands()
                time.sleep(1.0)
            except Exception as e:
                logger.exception(f"Error in command cleanup loop: {e}")
                time.sleep(1.0)

    def close(self) -> None:
        """Close the network connection and clean up resources."""
        if self.networkMode == "local":
            logger.debug("No network to close.")
            return
        logger.debug("Closing network connection...")
        self.running = False
        try:
            if hasattr(self, 'connections') and self.connections:
                for conn in self.connections[:]:
                    try:
                        conn.close()
                    except Exception as e:
                        logger.warning(f"Error closing client connection: {e}")
                self.connections.clear()
            if self.socket:
                try:
                    self.socket.close()
                except Exception as e:
                    logger.warning(f"Error closing main socket: {e}")
            logger.debug("Network connection closed successfully")
        except Exception as e:
            logger.exception(f"Error while closing network connection: {e}")
        finally:
            self.onClientConnected = None
            self.onClientSubmittedTurn = None
            self.onInitialGameStateReceived = None
            self.onSyncGameState = None
            self.onJoinFailed = None
            self.onJoinRejected = None
            self.onPlayerClaimed = None
            self.onStartGame = None
            self.onClientDisconnected = None
            self.onHostDisconnected = None
            self.socket = None

    def _handleConnectionDrop(self, conn):
        """Handle a dropped connection."""
        try:
            if conn in self.connections:
                self.connections.remove(conn)
                logger.debug("Client disconnected")
                if self.onClientDisconnected:
                    self.onClientDisconnected(conn)
            else:
                logger.debug("Lost connection to host")
                if self.onHostDisconnected:
                    self.onHostDisconnected()
        except Exception as e:
            logger.exception(f"Error handling connection drop: {e}")
        finally:
            try:
                conn.close()
            except:
                pass