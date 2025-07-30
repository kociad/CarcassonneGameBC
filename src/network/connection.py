import socket
import threading
import logging
import typing
from network.message import decodeMessage
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
        self.onClientConnected = None
        self.onClientSubmittedTurn = None
        self.onInitialGameStateReceived = None
        self.onSyncGameState = None
        self.onJoinFailed = None
        self.onJoinRejected = None
        self.onPlayerClaimed = None
        self.onStartGame = None
        if self.networkMode == "local":
            logger.debug("Running in local mode. Networking is disabled.")
            return
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.networkMode == "host":
            try:
                host_ip = settingsManager.get("HOST_IP", "0.0.0.0")
                host_port = settingsManager.get("HOST_PORT", 222)
                self.socket.bind((host_ip, host_port))
                self.socket.listen()
                logger.debug(f"Host listening on {host_ip}:{host_port}...")
                threading.Thread(target=self.acceptConnections, daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to bind socket: {e}")
        elif self.networkMode == "client":
            try:
                host_ip = settingsManager.get("HOST_IP", "0.0.0.0")
                host_port = settingsManager.get("HOST_PORT", 222)
                self.socket.connect((host_ip, host_port))
                logger.debug(f"Connected to host at {host_ip}:{host_port}")
                threading.Thread(target=self.receiveLoop, args=(self.socket,), daemon=True).start()
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
                break

    def onMessageReceived(self, message, conn=None):
        """Handle a received message and dispatch to the appropriate handler."""
        parsed = decodeMessage(message)
        if not parsed:
            return
        action = parsed.get("action")
        payload = parsed.get("payload")
        if action == "init_game_state":
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
            self.socket = None