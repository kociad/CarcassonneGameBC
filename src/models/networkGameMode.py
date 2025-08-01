import socket
import threading
import pickle
import logging
import typing
import settings

logger = logging.getLogger(__name__)


class NetworkGameMode:
    """Handles networked game mode for host and client."""

    def __init__(self, gameSession: typing.Any) -> None:
        self.gameSession = gameSession
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if settings.NETWORK_MODE == "host":
            self.initHost()
        elif settings.NETWORK_MODE == "client":
            self.initClient()
        else:
            raise ValueError(
                "Invalid settings.NETWORK_MODE in settings.py (must be 'host' or 'client')"
            )

    def initHost(self) -> None:
        """Initialize as host and wait for a client connection."""
        self.sock.bind((settings.HOST_IP, settings.HOST_PORT))
        self.sock.listen(1)
        logger.debug(
            f"[HOST] Waiting for connection on {settings.HOST_IP}:{settings.HOST_PORT}..."
        )
        self.conn, addr = self.sock.accept()
        logger.debug(f"[HOST] Connected by {addr}")
        threading.Thread(target=self.listenThread, daemon=True).start()

    def initClient(self) -> None:
        """Initialize as client and connect to host."""
        self.sock.connect((settings.HOST_IP, settings.HOST_PORT))
        logger.debug(
            f"[CLIENT] Connected to host at {settings.HOST_IP}:{settings.HOST_PORT}"
        )
        self.conn = self.sock
        threading.Thread(target=self.listenThread, daemon=True).start()

    def listenThread(self) -> None:
        """Listen for incoming network actions."""
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    continue
                action = pickle.loads(data)
                self.handleNetworkAction(action)
            except Exception as e:
                logger.exception(f"Network thread exception: {e}")
                self.running = False

    def handleNetworkAction(self, action: dict) -> None:
        """Execute actions sent from the remote peer."""
        actionType = action.get("type")
        if actionType == "playCard":
            self.gameSession.playCard(action["x"], action["y"])
        elif actionType == "playFigure":
            self.gameSession.playFigure(self.gameSession.getCurrentPlayer(),
                                        action["x"], action["y"],
                                        action["position"])
        elif actionType == "skip":
            self.gameSession.skipCurrentAction()
        else:
            logger.warning(f"Unknown network action type: {actionType}")

    def sendAction(self, actionDict: dict) -> None:
        """Send an action to the remote peer."""
        try:
            data = pickle.dumps(actionDict)
            self.conn.sendall(data)
        except Exception as e:
            logger.exception(f"Failed to send network action: {e}")

    def stop(self) -> None:
        """Stop the network game mode and close the connection."""
        self.running = False
        self.conn.close()
