import socket
import threading
import pickle
import logging
import typing
import settings

logger = logging.getLogger(__name__)


class NetworkGameMode:
    """Handles networked game mode for host and client."""

    def __init__(self, game_session: typing.Any) -> None:
        self.game_session = game_session
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if settings.NETWORK_MODE == "host":
            self._init_host()
        elif settings.NETWORK_MODE == "client":
            self._init_client()
        else:
            raise ValueError(
                "Invalid settings.NETWORK_MODE in settings.py (must be 'host' or 'client')"
            )

    def _init_host(self) -> None:
        """Initialize as host and wait for a client connection."""
        self.sock.bind((settings.HOST_IP, settings.HOST_PORT))
        self.sock.listen(1)
        logger.debug(
            f"[HOST] Waiting for connection on {settings.HOST_IP}:{settings.HOST_PORT}..."
        )
        self.conn, addr = self.sock.accept()
        logger.debug(f"[HOST] Connected by {addr}")
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _init_client(self) -> None:
        """Initialize as client and connect to host."""
        self.sock.connect((settings.HOST_IP, settings.HOST_PORT))
        logger.debug(
            f"[CLIENT] Connected to host at {settings.HOST_IP}:{settings.HOST_PORT}"
        )
        self.conn = self.sock
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self) -> None:
        """Listen for incoming network actions."""
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    continue
                action = pickle.loads(data)
                self._handle_network_action(action)
            except Exception as e:
                logger.exception(f"Network thread exception: {e}")
                self.running = False

    def _handle_network_action(self, action: dict) -> None:
        """Execute actions sent from the remote peer."""
        action_type = action.get("type")
        if action_type == "playCard":
            self.game_session.play_card(action["x"], action["y"])
        elif action_type == "play_figure":
            self.game_session.play_figure(
                self.game_session.get_current_player(), action["x"],
                action["y"], action["position"])
        elif action_type == "skip":
            self.game_session.skip_current_action()
        else:
            logger.warning(f"Unknown network action type: {action_type}")

    def send_action(self, action_dict: dict) -> None:
        """Send an action to the remote peer."""
        try:
            data = pickle.dumps(action_dict)
            self.conn.sendall(data)
        except Exception as e:
            logger.exception(f"Failed to send network action: {e}")

    def stop(self) -> None:
        """Stop the network game mode and close the connection."""
        self.running = False
        self.conn.close()
