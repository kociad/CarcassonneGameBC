import socket
import threading
import pickle
import logging

from settings import NETWORK_MODE, HOST_IP, HOST_PORT, DEBUG

logger = logging.getLogger(__name__)

class NetworkGameMode:
    def __init__(self, gameSession):
        self.gameSession = gameSession
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if NETWORK_MODE == "host":
            self.initHost()
        elif NETWORK_MODE == "client":
            self.initClient()
        else:
            raise ValueError("Invalid NETWORK_MODE in settings.py (must be 'host' or 'client')")

    def initHost(self):
        self.sock.bind((HOST_IP, HOST_PORT))
        self.sock.listen(1)
        logger.debug(f"[HOST] Waiting for connection on {HOST_IP}:{HOST_PORT}...")
        self.conn, addr = self.sock.accept()
        logger.debug(f"[HOST] Connected by {addr}")
        threading.Thread(target=self.listenThread, daemon=True).start()

    def initClient(self):
        self.sock.connect((HOST_IP, HOST_PORT))
        logger.debug(f"[CLIENT] Connected to host at {HOST_IP}:{HOST_PORT}")
        self.conn = self.sock
        threading.Thread(target=self.listenThread, daemon=True).start()

    def listenThread(self):
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

    def handleNetworkAction(self, action):
        """
        Executes actions sent from the remote peer.
        Expects a dict with keys like: {"type": "playCard", "x": 4, "y": 3, ...}
        """
        actionType = action.get("type")

        if actionType == "playCard":
            self.gameSession.playCard(action["x"], action["y"])
        elif actionType == "playFigure":
            self.gameSession.playFigure(
                self.gameSession.getCurrentPlayer(),
                action["x"],
                action["y"],
                action["position"]
            )
        elif actionType == "skip":
            self.gameSession.skipCurrentAction()
        else:
            logger.warning(f"Unknown network action type: {actionType}")

    def sendAction(self, actionDict):
        try:
            data = pickle.dumps(actionDict)
            self.conn.sendall(data)
        except Exception as e:
            logger.exception(f"Failed to send network action: {e}")

    def stop(self):
        self.running = False
        self.conn.close()
