import socket
import threading
import logging
from network.message import decodeMessage
from models.gameSession import GameSession

import settings

logger = logging.getLogger(__name__)

BUFFER_SIZE = 4096

class NetworkConnection:
    def __init__(self):
        self.networkMode = settings.NETWORK_MODE  # 'host', 'client', or 'local'
        self.running = False
        self.connections = []  # only for host mode

        # Handlers assigned externally
        self.onClientConnected = None
        self.onClientSubmittedTurn = None
        self.onInitialGameStateReceived = None
        self.onSyncGameState = None
        self.onJoinFailed = None           # new for host
        self.onJoinRejected = None         # new for client

        if self.networkMode == "local":
            logger.debug("Running in local mode. Networking is disabled.")
            return

        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.networkMode == "host":
            try:
                self.socket.bind((settings.HOST_IP, settings.HOST_PORT))
                self.socket.listen()
                logger.debug(f"Host listening on {settings.HOST_IP}:{settings.HOST_PORT}...")
                threading.Thread(target=self.acceptConnections, daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to bind socket: {e}")
        elif self.networkMode == "client":
            try:
                self.socket.connect((settings.HOST_IP, settings.HOST_PORT))
                logger.debug(f"Connected to host at {settings.HOST_IP}:{settings.HOST_PORT}")
                threading.Thread(target=self.receiveLoop, args=(self.socket,), daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to connect to host: {e}")

    def acceptConnections(self):
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.connections.append(conn)
                logger.debug(f"Connection received and established with {addr}")
                if self.onClientConnected:
                    self.onClientConnected(conn)
                threading.Thread(target=self.receiveLoop, args=(conn,), daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to accept connection: {e}")

    def receiveLoop(self, conn):
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
                logger.exception(f"Socket error: {e}")
                break

    def onMessageReceived(self, message, conn=None):
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

        elif action == "join_rejected" and self.networkMode == "client":
            logger.debug("Received join_rejected from host")
            if self.onJoinRejected:
                self.onJoinRejected(payload)

    def sendToAll(self, message):
        if self.networkMode != "host":
            return
        logger.debug(f"Sending message to all: {message}")
        for conn in self.connections:
            try:
                conn.sendall((message + "\n").encode())
            except Exception as e:
                logger.exception(f"Failed to send message to all: {e}")

    def sendToHost(self, message):
        if self.networkMode != "client":
            return
        try:
            logger.debug(f"Sending message to host: {message}")
            self.socket.sendall((message + "\n").encode())
        except Exception as e:
            logger.exception(f"Failed to send to host: {e}")

    def close(self):
        if self.networkMode == "local":
            logger.debug("No network to close.")
            return
        self.running = False
        try:
            self.socket.close()
            logger.debug("Socket closed")
        except Exception as e:
            logger.exception(f"Error while closing socket: {e}")