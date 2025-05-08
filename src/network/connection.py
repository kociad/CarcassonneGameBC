import socket
import threading
import logging
from settings import DEBUG, NETWORK_MODE, HOST_IP, HOST_PORT
from network.message import decodeMessage
from models.gameSession import GameSession

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

BUFFER_SIZE = 4096

class NetworkConnection:
    def __init__(self):
        self.networkMode = NETWORK_MODE  # 'host', 'client', or 'local'
        self.running = False
        self.connections = []  # only for host mode
        self.onClientConnected = None  # externally assigned

        if self.networkMode == "local":
            logger.info("[LOCAL] Running in local mode. Networking is disabled.")
            return

        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.networkMode == "host":
            try:
                self.socket.bind((HOST_IP, HOST_PORT))
                self.socket.listen()
                logger.info(f"[HOST] Listening on {HOST_IP}:{HOST_PORT}")
                threading.Thread(target=self.acceptConnections, daemon=True).start()
            except Exception as e:
                logger.error(f"[HOST] Failed to bind socket: {e}")
        elif self.networkMode == "client":
            try:
                self.socket.connect((HOST_IP, HOST_PORT))
                logger.info(f"[CLIENT] Connected to host at {HOST_IP}:{HOST_PORT}")
                threading.Thread(target=self.receiveLoop, args=(self.socket,), daemon=True).start()
            except Exception as e:
                logger.error(f"[CLIENT] Failed to connect to host: {e}")

    def acceptConnections(self):
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.connections.append(conn)
                logger.info(f"[HOST] Connection established with {addr}")
                if self.onClientConnected:
                    self.onClientConnected(conn)
                threading.Thread(target=self.receiveLoop, args=(conn,), daemon=True).start()
            except Exception as e:
                logger.error(f"[HOST] Accept connection failed: {e}")

    def receiveLoop(self, conn):
        while self.running:
            try:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    message = data.decode()
                    logger.debug(f"[RECEIVE] Message: {message}")
                    self.onMessageReceived(message)
            except Exception as e:
                logger.warning(f"[RECEIVE] Socket error: {e}")
                break

    def onMessageReceived(self, message):
        parsed = decodeMessage(message)
        if not parsed:
            return

        action = parsed.get("action")
        payload = parsed.get("payload")

        if action == "init_game_state":
            logger.info("[NETWORK] Received initial game state from host")
            self.onInitialGameStateReceived(payload)
            
        elif action == "ack_game_state":
            logger.info("[NETWORK] Client confirmed receipt of game state: %s", payload)
            
    def sendToAll(self, message):
        logger.info("Sending game state to all clients")
        if self.networkMode != "host":
            return
        logger.debug(f"[SEND-ALL] {message}")
        for conn in self.connections:
            try:
                conn.sendall(message.encode())
            except Exception as e:
                logger.error(f"[SEND-ALL] Failed: {e}")

    def sendToHost(self, message):
        if self.networkMode != "client":
            return
        try:
            logger.debug(f"[SEND-HOST] {message}")
            self.socket.sendall(message.encode())
        except Exception as e:
            logger.error(f"[SEND-HOST] Failed: {e}")

    def close(self):
        if self.networkMode == "local":
            logger.info("[LOCAL] No network to close.")
            return
        self.running = False
        try:
            self.socket.close()
            logger.info("[CLOSE] Socket closed")
        except Exception as e:
            logger.error(f"[CLOSE] Error while closing socket: {e}")
