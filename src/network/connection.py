import socket
import threading
import logging
import typing
import time
from network.message import decode_message, encode_message
from network.command import CommandManager, decode_command_message, encode_command_message
from models.game_session import GameSession
from utils.settings_manager import settings_manager

logger = logging.getLogger(__name__)

BUFFER_SIZE = 4096


class NetworkConnection:
    """Handles network connections for host and client modes."""

    def __init__(self) -> None:
        self.network_mode = settings_manager.get("NETWORK_MODE", "local")
        self.running = False
        self.connections = []
        self.socket = None
        self.command_manager = CommandManager()

        self.on_client_connected = None
        self.on_client_submitted_turn = None
        self.on_initial_game_state_received = None
        self.on_sync_game_state = None
        self.on_join_failed = None
        self.on_join_rejected = None
        self.on_player_claimed = None
        self.on_start_game = None
        self.on_client_disconnected = None
        self.on_host_disconnected = None

        self.on_command_received = None
        self.on_command_ack = None
        self.on_sync_request = None

        if self.network_mode == "local":
            logger.debug("Running in local mode. Networking is disabled.")
            return
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.network_mode == "host":
            try:
                host_ip = settings_manager.get("HOST_IP", "0.0.0.0")
                host_port = settings_manager.get("HOST_PORT", 222)
                self.socket.bind((host_ip, host_port))
                self.socket.listen()
                logger.debug(f"Host listening on {host_ip}:{host_port}...")
                threading.Thread(target=self._accept_connections,
                                 daemon=True).start()
                threading.Thread(target=self._command_cleanup_loop,
                                 daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to bind socket: {e}")
        elif self.network_mode == "client":
            try:
                host_ip = settings_manager.get("HOST_IP", "0.0.0.0")
                host_port = settings_manager.get("HOST_PORT", 222)
                self.socket.connect((host_ip, host_port))
                logger.debug(f"Connected to host at {host_ip}:{host_port}")
                threading.Thread(target=self._receive_loop,
                                 args=(self.socket, ),
                                 daemon=True).start()
                threading.Thread(target=self._command_cleanup_loop,
                                 daemon=True).start()
            except Exception as e:
                logger.exception(f"Failed to connect to host: {e}")

    def _accept_connections(self):
        """Accept incoming client connections (host mode)."""
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.connections.append(conn)
                logger.debug(
                    f"Connection received and established with {addr}")
                if self.on_client_connected:
                    self.on_client_connected(conn)
                threading.Thread(target=self._receive_loop,
                                 args=(conn, ),
                                 daemon=True).start()
            except Exception as e:
                if self.running:
                    logger.exception(f"Failed to accept connection: {e}")
                break

    def _receive_loop(self, conn):
        """Receive and process messages from a connection."""
        buffer = ""
        while self.running:
            try:
                data = conn.recv(BUFFER_SIZE).decode()
                if not data:
                    logger.debug("Connection closed by peer")
                    self._handle_connection_drop(conn)
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        logger.debug(f"Receiving message: {line}")
                        self._on_message_received(line, conn)
            except Exception as e:
                if self.running:
                    logger.exception(f"Socket error: {e}")
                self._handle_connection_drop(conn)
                break

    def _on_message_received(self, message, conn=None):
        """Handle a received message and dispatch to the appropriate handler."""
        parsed = decode_message(message)
        if not parsed:
            return
        action = parsed.get("action")
        payload = parsed.get("payload")

        if action == "command":
            logger.debug("Received command from network")
            command = decode_command_message(message)
            if command and self.on_command_received:
                self.on_command_received(command, conn)
            ack_message = encode_message("command_ack",
                                         {"command_id": command.command_id})
            if conn:
                try:
                    conn.sendall((ack_message + "\n").encode())
                except Exception as e:
                    logger.exception(f"Failed to send command ack: {e}")
            elif self.network_mode == "client":
                self.send_to_host(ack_message)
        elif action == "command_ack":
            logger.debug("Received command acknowledgment")
            command_id = payload.get("command_id")
            if command_id:
                self.command_manager.ack_command(command_id)
                if self.on_command_ack:
                    self.on_command_ack(command_id)
        elif action == "sync_request":
            logger.debug("Received sync request")
            if self.on_sync_request:
                self.on_sync_request(payload, conn)
        elif action == "init_game_state":
            logger.debug("Received initial game state from host")
            if self.on_initial_game_state_received:
                self.on_initial_game_state_received(payload)
        elif action == "ack_game_state":
            logger.debug("Client confirmed receiving game state: %s", payload)
        elif action == "player_claimed" and self.network_mode == "host":
            logger.debug("Received player claimed from client")
            if self.on_player_claimed:
                self.on_player_claimed(payload, conn)
        elif action == "submit_turn" and self.network_mode == "host":
            logger.debug("Received submitted turn from client")
            if self.on_client_submitted_turn:
                self.on_client_submitted_turn(payload)
        elif action == "sync_game_state":
            logger.debug("Received updated game state from host")
            if self.on_sync_game_state:
                self.on_sync_game_state(payload)
        elif action == "join_failed" and self.network_mode == "host":
            logger.debug("Received join_failed from client")
            if self.on_join_failed:
                self.on_join_failed(payload, conn)
        elif action == "start_game" and self.network_mode == "client":
            logger.debug("Received start_game from host")
            if self.on_start_game:
                self.on_start_game(payload)
        elif action == "join_rejected" and self.network_mode == "client":
            logger.debug("Received join_rejected from host")
            if self.on_join_rejected:
                self.on_join_rejected(payload)

    def send_to_all(self, message):
        """Send a message to all connected clients (host mode)."""
        if self.network_mode != "host":
            return
        logger.debug(f"Sending message to all: {message}")
        for conn in self.connections[:]:
            try:
                conn.sendall((message + "\n").encode())
            except Exception as e:
                logger.exception(
                    f"Failed to send message to client, removing connection: {e}"
                )
                try:
                    conn.close()
                except:
                    pass
                if conn in self.connections:
                    self.connections.remove(conn)

    def send_to_host(self, message):
        """Send a message to the host (client mode)."""
        if self.network_mode != "client":
            return
        try:
            logger.debug(f"Sending message to host: {message}")
            self.socket.sendall((message + "\n").encode())
        except Exception as e:
            logger.exception(f"Failed to send to host: {e}")

    def send_command(self, command):
        """Send a command to the network with acknowledgment tracking."""
        if self.network_mode == "local":
            return

        message = encode_command_message(command)
        self.command_manager.mark_command_pending_ack(command.command_id)

        if self.network_mode == "host":
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
        elif self.network_mode == "client":
            self.send_to_host(message)

        logger.debug(
            f"Sent command {command.command_type} with ID {command.command_id}"
        )

    def _command_cleanup_loop(self):
        """Background thread to clean up expired commands."""
        while self.running:
            try:
                self.command_manager.clear_expired_commands()
                time.sleep(1.0)
            except Exception as e:
                logger.exception(f"Error in command cleanup loop: {e}")
                time.sleep(1.0)

    def close(self) -> None:
        """Close the network connection and clean up resources."""
        if self.network_mode == "local":
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
            self.on_client_connected = None
            self.on_client_submitted_turn = None
            self.on_initial_game_state_received = None
            self.on_sync_game_state = None
            self.on_join_failed = None
            self.on_join_rejected = None
            self.on_player_claimed = None
            self.on_start_game = None
            self.on_client_disconnected = None
            self.on_host_disconnected = None
            self.socket = None

    def _handle_connection_drop(self, conn):
        """Handle a dropped connection."""
        try:
            if conn in self.connections:
                self.connections.remove(conn)
                logger.debug("Client disconnected")
                if self.on_client_disconnected:
                    self.on_client_disconnected(conn)
            else:
                logger.debug("Lost connection to host")
                if self.on_host_disconnected:
                    self.on_host_disconnected()
        except Exception as e:
            logger.exception(f"Error handling connection drop: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
