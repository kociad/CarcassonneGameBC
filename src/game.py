"""
Main game controller and application entry point.

This module contains the main Game class that manages the game loop,
scene transitions, network communication, and overall game state.
"""

import pygame
import logging
from datetime import datetime
import typing

from ui.main_menu_scene import MainMenuScene
from ui.settings_scene import SettingsScene
from ui.game_prepare_scene import GamePrepareScene
from ui.scene import Scene
from ui.game_scene import GameScene
from ui.help_scene import HelpScene
from game_state import GameState
from utils.logging_config import configure_logging, log_error
from models.game_session import GameSession
from network.connection import NetworkConnection
from network.message import encode_message
from network.command import encode_command_message
from utils.settings_manager import settings_manager
from ui.components.game_log import GameLog
from utils.logging_config import set_game_log_instance
from ui.lobby_scene import LobbyScene

# Configure logging with exception handling
configure_logging()
logger = logging.getLogger(__name__)


class Game:
    """
    Main game controller class.
    
    Manages the game loop, scene transitions, network communication,
    and overall game state. Handles initialization, cleanup, and
    coordination between different game components.
    """

    def __init__(self) -> None:
        """
        Initialize the game and set up the main window.
        
        Sets up pygame, creates the display window, initializes
        the game log, and starts with the main menu scene.
        """
        try:
            pygame.init()

            # Lower resolution for web view
            if "pygbag" in sys.modules:
                self._screen = pygame.display.set_mode((1280, 720))

            # Desktop
            else:
                if settings_manager.get("FULLSCREEN", False):
                    info = pygame.display.Info()
                    self._screen = pygame.display.set_mode(
                        (info.current_w, info.current_h), pygame.FULLSCREEN)
                else:
                    width = settings_manager.get("WINDOW_WIDTH", 1920)
                    height = settings_manager.get("WINDOW_HEIGHT", 1080)
                    self._screen = pygame.display.set_mode((width, height))

                pygame.display.set_caption("Carcassonne")

                self._clock = pygame.time.Clock()
                self._running = True

                # Initialize persistent game log
                self._game_log = GameLog()
                set_game_log_instance(self._game_log)

                # Game-related attributes (deferred until game starts)
                self._game_session = None
                self._network = None

                self._current_scene = None
                self._init_scene(GameState.MENU)

                logger.debug("Game initialized successfully")

        except Exception as e:
            log_error("Failed to initialize game", e)
            raise

    def run(self) -> None:
        """
        Start the main game loop.
        
        Handles events, updates the current scene, and renders
        the game until the application is closed.
        """
        logger.debug("Starting main game loop")
        try:
            while self._running:
                events = pygame.event.get()
                self._current_scene.handle_events(events)
                self._current_scene.update()
                self._current_scene.draw()
        except Exception as e:
            log_error("Error in main game loop", e)
            raise
        finally:
            logger.debug("Game loop ended")

    def quit(self) -> None:
        """
        Clean up resources and exit the game.
        
        Performs cleanup of game resources, closes pygame,
        and exits the application.
        """
        try:
            self._cleanup_previous_game()
            pygame.quit()
            logger.debug("Game quit successfully")
            exit()
        except Exception as e:
            log_error("Error during game quit", e)
            exit()

    def _cleanup_previous_game(self) -> None:
        """
        Clean up resources from previous game session.
        
        Closes network connections, clears game session,
        and resets temporary settings and game log.
        """
        try:
            logger.debug("Cleaning up previous game resources...")

            if self._network:
                logger.debug("Closing network connection...")
                self._network.close()
                self._network = None

            if self._game_session:
                logger.debug("Clearing game session...")
                self._game_session.on_turn_ended = None
                self._game_session = None

            logger.debug("Clearing temporary settings...")
            settings_manager.reload_from_file()

            # Reset game log for new session
            if hasattr(self, '_game_log'):
                self._game_log.entries.clear()
                self._game_log.scroll_offset = 0
                self._game_log.add_entry("New game session started", "INFO")

            logger.debug("Previous game cleanup completed")

        except Exception as e:
            log_error("Error during previous game cleanup", e)

    def _init_scene(self, state: GameState, *args: typing.Any) -> None:
        """
        Initialize a new scene based on the game state.
        
        Args:
            state: The game state to transition to
            *args: Additional arguments passed to scene constructors
        """
        try:
            if state == GameState.MENU:
                self._current_scene = MainMenuScene(
                    self._screen, self._init_scene, self._get_game_session,
                    self._cleanup_previous_game)
            elif state == GameState.GAME:
                self._current_scene = GameScene(self._screen, self._init_scene,
                                                self._game_session,
                                                self._clock, self._network,
                                                self._game_log)
            elif state == GameState.SETTINGS:
                self._current_scene = SettingsScene(self._screen,
                                                    self._init_scene)
            elif state == GameState.PREPARE:
                self._current_scene = GamePrepareScene(self._screen,
                                                       self._init_scene)
            elif state == GameState.LOBBY:
                self._current_scene = LobbyScene(self._screen,
                                                 self._init_scene,
                                                 self._start_game,
                                                 self._get_game_session,
                                                 self._network, self._game_log)
            elif state == GameState.HELP:
                self._current_scene = HelpScene(self._screen, self._init_scene)
            # Handle dynamic callback from GamePrepareScene
            elif isinstance(state,
                            str) and state in ("start_game", "start_lobby"):
                player_names = args[0] if args else []
                if state == "start_game":
                    self._start_game(player_names)
                else:
                    self._start_lobby(player_names)
            logger.debug(f"Scene initialized: {state}")
        except Exception as e:
            log_error(f"Failed to initialize scene: {state}", e)
            raise

    def _start_game(self, player_names: list[str]) -> None:
        """
        Start a new game session.
        
        Args:
            player_names: List of player names for the game
        """
        try:
            logger.debug("Initializing new game session...")

            if not self._network:
                self._network = NetworkConnection()

            network_mode = self._network.network_mode
            if network_mode in ("host", "local"):
                lobby_completed = True
                self._game_session = GameSession(
                    player_names,
                    lobby_completed=lobby_completed,
                    network_mode=network_mode)
                player_index = settings_manager.get("PLAYER_INDEX", 0)
                host_player = self._game_session.players[player_index]
                host_player.set_is_human(True)
                logger.debug(
                    f"Player with index {host_player.get_index()} marked as human."
                )
                logger.debug(
                    f"Player name set to '{host_player.get_name()}' from host settings."
                )
                self._game_session.on_turn_ended = self._on_turn_ended
                self._game_session.on_show_notification = self._on_show_notification
                self._game_session.on_command_executed = self._on_command_executed
            self._network.on_initial_game_state_received = self._on_game_state_received
            self._network.on_sync_game_state = self._on_sync_game_state
            self._network.on_join_rejected = self._on_join_rejected
            self._network.on_start_game = self._on_start_game
            self._network.on_client_disconnected = self._on_client_disconnected
            self._network.on_host_disconnected = self._on_host_disconnected
            self._network.on_command_received = self._on_command_received
            self._network.on_command_ack = self._on_command_ack
            self._network.on_sync_request = self._on_sync_request
            if network_mode == "host":
                self._network.on_client_connected = self._on_client_connected
                self._network.on_client_submitted_turn = self._on_client_submitted_turn
                self._network.on_player_claimed = self._on_player_claimed
                self._network.on_join_failed = self._on_join_failed
            self._init_scene(GameState.GAME)
            logger.debug(f"Game started with {len(player_names)} players")

            if network_mode == "host":
                self._network.send_to_all(
                    encode_message(
                        "start_game",
                        {"game_session": self._game_session.serialize()}))
        except Exception as e:
            log_error("Failed to start game", e)
            raise

    def _start_lobby(self, player_names: list[str]) -> None:
        """
        Start a lobby for network games.
        
        Args:
            player_names: List of player names for the game
        """
        try:
            logger.debug("Preparing to enter lobby...")

            if not self._network:
                self._network = NetworkConnection()

            network_mode = self._network.network_mode
            if network_mode in ("host", "local"):
                lobby_completed = network_mode == "local"
                self._game_session = GameSession(
                    player_names,
                    lobby_completed=lobby_completed,
                    network_mode=network_mode)
                player_index = settings_manager.get("PLAYER_INDEX", 0)
                host_player = self._game_session.players[player_index]
                host_player.set_is_human(True)
                logger.debug(
                    f"Player with index {host_player.get_index()} marked as human."
                )
                logger.debug(
                    f"Player name set to '{host_player.get_name()}' from host settings."
                )
                self._game_session.on_turn_ended = self._on_turn_ended
                self._game_session.on_show_notification = self._on_show_notification
                self._game_session.on_command_executed = self._on_command_executed
            self._network.on_initial_game_state_received = self._on_game_state_received
            self._network.on_sync_game_state = self._on_sync_game_state
            self._network.on_join_rejected = self._on_join_rejected
            self._network.on_start_game = self._on_start_game
            self._network.on_client_disconnected = self._on_client_disconnected
            self._network.on_host_disconnected = self._on_host_disconnected
            self._network.on_command_received = self._on_command_received
            self._network.on_command_ack = self._on_command_ack
            self._network.on_sync_request = self._on_sync_request
            if network_mode == "host":
                self._network.on_client_connected = self._on_client_connected
                self._network.on_client_submitted_turn = self._on_client_submitted_turn
                self._network.on_player_claimed = self._on_player_claimed
                self._network.on_join_failed = self._on_join_failed
            if network_mode != "local":
                self._init_scene(GameState.LOBBY)
            else:
                self._init_scene(GameState.GAME)
        except Exception as e:
            log_error("Failed to start lobby", e)
            raise

    def _on_game_state_received(self, data: dict) -> None:
        """
        Handle received game state from network.
        
        Args:
            data: Serialized game state data
        """
        try:
            self._game_session = GameSession.deserialize(data)
            self._game_session.on_turn_ended = self._on_turn_ended
            self._game_session.on_show_notification = self._on_show_notification
            self._game_session.on_command_executed = self._on_command_executed
            logger.debug(
                "Game session replaced with synchronized state from host")

            if hasattr(self._current_scene, 'update_game_session'):
                self._current_scene.update_game_session(self._game_session)

            if self._network.network_mode == "client":
                assigned = False
                for player in self._game_session.get_players():
                    if not player.get_is_ai() and not player.is_human:
                        player.set_is_human(True)
                        logger.debug(
                            f"Player with index {player.get_index()} marked as human."
                        )
                        players_list = settings_manager.get(
                            "PLAYERS", ["Player 1"])
                        player.name = players_list[0]
                        logger.debug(
                            f"Player name set to '{player.name}' from client settings."
                        )
                        settings_manager.set("PLAYER_INDEX",
                                             player.get_index(),
                                             temporary=True)
                        logger.debug(
                            f"Client assigned to player index {player.get_index()}"
                        )
                        assigned = True
                        break

                if assigned:
                    updated_game_state = self._game_session.serialize()
                    self._network.send_to_host(
                        encode_message("player_claimed", updated_game_state))
                    logger.debug(
                        "Client claimed player and sent updated game state to host"
                    )

                    if self._game_session.lobby_completed:
                        self._init_scene(GameState.GAME)
                else:
                    logger.debug("No available player slots for client")
                    self._network.send_to_host(
                        encode_message("join_failed", {"reason": "no_slots"}))

        except Exception as e:
            log_error("Failed to process received game state", e)

    def _on_client_connected(self, conn) -> None:
        """
        Handle new client connection.
        
        Args:
            conn: Network connection to the client
        """
        try:
            logger.debug("Sending current game state to new client...")
            game_state = self._game_session.serialize()
            message = encode_message("init_game_state", game_state)
            conn.sendall((message + "\n").encode())
            logger.debug("Game state sent successfully.")
        except Exception as e:
            log_error("Failed to send game state to client", e)

    def _on_player_claimed(self, data: dict, conn) -> None:
        """
        Handle player claim from client.
        
        Args:
            data: Serialized game state from client with claimed player
            conn: Network connection to the client
        """
        try:
            self._game_session = GameSession.deserialize(data)
            self._game_session.on_turn_ended = self._on_turn_ended
            self._game_session.on_show_notification = self._on_show_notification
            self._game_session.on_command_executed = self._on_command_executed
            logger.debug(
                "Host updated game session with client's claimed player")

            if hasattr(self._current_scene, 'update_game_session'):
                self._current_scene.update_game_session(self._game_session)

            self._broadcast_game_state()
        except Exception as e:
            log_error("Failed to process player claim", e)

    def _on_client_submitted_turn(self, data: dict) -> None:
        """
        Handle turn submission from client.
        
        Args:
            data: Serialized game state from client
        """
        try:
            self._game_session = GameSession.deserialize(data)
            self._game_session.on_turn_ended = self._on_turn_ended
            self._game_session.on_show_notification = self._on_show_notification
            self._game_session.on_command_executed = self._on_command_executed
            logger.debug("Host applied client-submitted game state")

            if hasattr(self._current_scene, 'update_game_session'):
                self._current_scene.update_game_session(self._game_session)

            self._broadcast_game_state()
        except Exception as e:
            log_error("Failed to process client submitted turn", e)

    def _broadcast_game_state(self) -> None:
        """Broadcast current game state to all connected clients."""
        try:
            if self._network.network_mode == "host":
                game_state = self._game_session.serialize()
                message = encode_message("sync_game_state", game_state)
                self._network.send_to_all(message)
                logger.debug("Broadcasted updated game state to all clients.")
        except Exception as e:
            log_error("Failed to broadcast game state", e)

    def _on_start_game(self, data: dict) -> None:
        """
        Handle start game message from host.
        
        Args:
            data: Start game data with full game session
        """
        try:
            logger.debug("Client received start game message from host")
            if "game_session" in data:
                self._game_session = GameSession.deserialize(
                    data["game_session"])
                self._game_session.on_turn_ended = self._on_turn_ended
                self._game_session.on_show_notification = self._on_show_notification
                self._game_session.on_command_executed = self._on_command_executed
                if hasattr(self._current_scene, 'update_game_session'):
                    self._current_scene.update_game_session(self._game_session)
            self._init_scene(GameState.GAME)
        except Exception as e:
            log_error("Failed to handle start game message", e)

    def _on_sync_game_state(self, data: dict) -> None:
        """
        Handle game state synchronization from host.
        
        Args:
            data: Serialized game state data
        """
        try:
            self._game_session = GameSession.deserialize(data)
            self._game_session.on_turn_ended = self._on_turn_ended
            self._game_session.on_show_notification = self._on_show_notification
            self._game_session.on_command_executed = self._on_command_executed
            logger.debug("Client game session updated from host sync.")

            if hasattr(self._current_scene, 'update_game_session'):
                self._current_scene.update_game_session(self._game_session)
        except Exception as e:
            log_error("Failed to sync game state", e)

    def _on_turn_ended(self) -> None:
        """Handle turn completion and network synchronization."""
        try:
            network_mode = settings_manager.get("NETWORK_MODE", "local")
            if network_mode == "local":
                return

            logger.debug(
                "Turn ended - command-based sync handles synchronization")

        except Exception as e:
            log_error("Failed to handle turn ended", e)

    def _on_join_failed(self, data: dict, conn) -> None:
        """
        Handle failed client join attempt.
        
        Args:
            data: Join failure data
            conn: Network connection to the client
        """
        try:
            reason = data.get("reason", "unspecified")
            logger.debug(f"Client join failed: {reason}")
            response = encode_message("join_rejected", {"reason": reason})
            conn.sendall((response + "\n").encode())
            logger.debug("Sent join_rejected response to client.")
        except Exception as e:
            log_error("Failed to handle join failure", e)

    def _on_join_rejected(self, data: dict) -> None:
        """
        Handle join rejection from host.
        
        Args:
            data: Join rejection data
        """
        try:
            reason = data.get("reason", "unknown")
            logger.debug(f"Join rejected by host. Reason: {reason}")
            self._handle_join_rejected(reason)
        except Exception as e:
            log_error("Failed to handle join rejection", e)

    def _handle_join_rejected(self, reason: str) -> None:
        """
        Handle join rejection with user feedback.
        
        Args:
            reason: Reason for the rejection
        """
        try:
            logger.debug(f"Handling join rejection (reason: {reason})")
            print(f"Join rejected: {reason}")
            pygame.time.delay(3000)
            self.quit()
        except Exception as e:
            log_error("Failed to handle join rejection", e)

    def _get_game_session(self) -> typing.Optional['GameSession']:
        """
        Get the current game session.
        
        Returns:
            Current game session or None if no session exists
        """
        return self._game_session

    def _on_client_disconnected(self, conn) -> None:
        """
        Handle client disconnection (host mode).
        
        Args:
            conn: Network connection to the disconnected client
        """
        try:
            logger.debug("Client disconnected from host")

            # Show notification in current scene if it has show_notification method
            if hasattr(self._current_scene, 'show_notification'):
                self._current_scene.show_notification(
                    "warning", "Lost connection to one of the players")
            else:
                self.on_show_notification(
                    "warning",
                    "Lost connection to one of the players, returning to main menu"
                )

            pygame.time.delay(2000)
            self._cleanup_previous_game()
            self._init_scene(GameState.MENU)

        except Exception as e:
            log_error("Failed to handle client disconnection", e)

    def _on_host_disconnected(self) -> None:
        """
        Handle host disconnection (client mode).
        """
        try:
            logger.debug("Lost connection to host")

            # Show notification in current scene if it has show_notification method
            if hasattr(self._current_scene, 'show_notification'):
                self._current_scene.show_notification(
                    "error", "Lost connection to host")
            else:
                self.on_show_notification(
                    "error", "Lost connection to host, returning to main menu")

            pygame.time.delay(2000)
            self._cleanup_previous_game()
            self._init_scene(GameState.MENU)

        except Exception as e:
            log_error("Failed to handle host disconnection", e)

    def _on_command_received(self, command, conn=None) -> None:
        """
        Handle received command from network.
        
        Args:
            command: The received command object
            conn: Network connection (for host mode)
        """
        try:
            logger.debug(
                f"Received command {command.command_type} from player {command.player_index}"
            )

            success = self._game_session.execute_command(command)
            if success:
                logger.debug(
                    f"Successfully executed command {command.command_type}")

                if hasattr(self._current_scene, 'update_game_session'):
                    self._current_scene.update_game_session(self._game_session)

                if self._network.network_mode == "host" and conn:
                    for other_conn in self._network.connections[:]:
                        if other_conn != conn:
                            try:
                                from network.command import encode_command_message
                                message = encode_command_message(command)
                                other_conn.sendall((message + "\n").encode())
                            except Exception as e:
                                logger.exception(
                                    f"Failed to broadcast command to client: {e}"
                                )
            else:
                logger.warning(
                    f"Failed to execute command {command.command_type}")

        except Exception as e:
            log_error("Failed to handle received command", e)

    def _on_command_ack(self, command_id: str) -> None:
        """
        Handle command acknowledgment.
        
        Args:
            command_id: ID of the acknowledged command
        """
        try:
            logger.debug(f"Command {command_id} acknowledged")
        except Exception as e:
            log_error("Failed to handle command acknowledgment", e)

    def _on_command_executed(self, command) -> None:
        """
        Handle command execution completion.
        
        Args:
            command: The executed command
        """
        try:
            logger.debug(
                f"Command {command.command_type} executed successfully")
            if hasattr(self._current_scene, 'update_game_session'):
                self._current_scene.update_game_session(self._game_session)
        except Exception as e:
            log_error("Failed to handle command execution", e)

    def _on_sync_request(self, data: dict, conn=None) -> None:
        """
        Handle sync request from client.
        
        Args:
            data: Sync request data
            conn: Network connection to the client
        """
        try:
            logger.debug("Received sync request from client")
            game_state = self._game_session.serialize()
            message = encode_message("sync_game_state", game_state)
            if conn:
                conn.sendall((message + "\n").encode())
        except Exception as e:
            log_error("Failed to handle sync request", e)

    def _on_show_notification(self, notification_type: str,
                              message: str) -> None:
        """
        Handle notification requests from game session.
        
        Args:
            notification_type: Type of notification
            message: Notification message
        """
        try:
            logger.debug(
                f"on_show_notification called: type={notification_type}, message={message}"
            )

            if hasattr(self._current_scene, 'show_notification'):
                logger.debug("Scene has show_notification method, calling it")
                self._current_scene.show_notification(notification_type,
                                                      message)
            else:
                logger.debug(f"Scene doesn't support notifications: {message}")
        except Exception as e:
            log_error("Failed to show notification", e)


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        log_error("Critical error in main", e)
        input("Press Enter to exit...")
