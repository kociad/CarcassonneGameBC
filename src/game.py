"""
Main game controller and application entry point.

This module contains the main Game class that manages the game loop,
scene transitions, network communication, and overall game state.
"""

import pygame
import logging
from datetime import datetime
import typing

from ui.mainMenuScene import MainMenuScene
from ui.settingsScene import SettingsScene
from ui.gamePrepareScene import GamePrepareScene
from ui.scene import Scene
from ui.gameScene import GameScene
from ui.helpScene import HelpScene
from gameState import GameState
from utils.loggingConfig import configureLogging, logError
from models.gameSession import GameSession
from network.connection import NetworkConnection
from network.message import encodeMessage
from utils.settingsManager import settingsManager
from ui.components.gameLog import GameLog
from utils.loggingConfig import setGameLogInstance
from ui.lobbyScene import LobbyScene

# Configure logging with exception handling
configureLogging()
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

            if settingsManager.get("FULLSCREEN", False):
                info = pygame.display.Info()
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            else:
                width = settingsManager.get("WINDOW_WIDTH", 1920)
                height = settingsManager.get("WINDOW_HEIGHT", 1080)
                self.screen = pygame.display.set_mode((width, height))

            pygame.display.set_caption("Carcassonne")

            self.clock = pygame.time.Clock()
            self.running = True
            
            # Initialize persistent game log
            self.gameLog = GameLog()
            setGameLogInstance(self.gameLog)

            # Game-related attributes (deferred until game starts)
            self.gameSession = None
            self.network = None

            self.currentScene = None
            self.initScene(GameState.MENU)
            
            logger.debug("Game initialized successfully")
            
        except Exception as e:
            logError("Failed to initialize game", e)
            raise

    def run(self) -> None:
        """
        Start the main game loop.
        
        Handles events, updates the current scene, and renders
        the game until the application is closed.
        """
        logger.debug("Starting main game loop")
        try:
            while self.running:
                events = pygame.event.get()
                self.currentScene.handleEvents(events)
                self.currentScene.update()
                self.currentScene.draw()
        except Exception as e:
            logError("Error in main game loop", e)
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
            self.cleanupPreviousGame()
            pygame.quit()
            logger.debug("Game quit successfully")
            exit()
        except Exception as e:
            logError("Error during game quit", e)
            exit()

    def cleanupPreviousGame(self) -> None:
        """
        Clean up resources from previous game session.
        
        Closes network connections, clears game session,
        and resets temporary settings and game log.
        """
        try:
            logger.debug("Cleaning up previous game resources...")
            
            if self.network:
                logger.debug("Closing network connection...")
                self.network.close()
                self.network = None
            
            if self.gameSession:
                logger.debug("Clearing game session...")
                self.gameSession.onTurnEnded = None
                self.gameSession = None
            
            logger.debug("Clearing temporary settings...")
            settingsManager.reloadFromFile()
            
            # Reset game log for new session
            if hasattr(self, 'gameLog'):
                self.gameLog.entries.clear()
                self.gameLog.scrollOffset = 0
                self.gameLog.addEntry("New game session started", "INFO")
            
            logger.debug("Previous game cleanup completed")
            
        except Exception as e:
            logError("Error during previous game cleanup", e)

    def initScene(self, state: GameState, *args: typing.Any) -> None:
        """
        Initialize a new scene based on the game state.
        
        Args:
            state: The game state to transition to
            *args: Additional arguments passed to scene constructors
        """
        try:
            if state == GameState.MENU:
                self.currentScene = MainMenuScene(self.screen, self.initScene, self.getGameSession, self.cleanupPreviousGame)
            elif state == GameState.GAME:
                self.currentScene = GameScene(
                    self.screen, self.initScene, self.gameSession,
                    self.clock, self.network, self.gameLog
                )
            elif state == GameState.SETTINGS:
                self.currentScene = SettingsScene(self.screen, self.initScene)
            elif state == GameState.PREPARE:
                self.currentScene = GamePrepareScene(self.screen, self.initScene)
            elif state == GameState.LOBBY:
                self.currentScene = LobbyScene(
                    self.screen, self.initScene, self.startGame, self.getGameSession, self.network, self.gameLog
                )
            elif state == GameState.HELP:
                self.currentScene = HelpScene(self.screen, self.initScene)
            # Handle dynamic callback from GamePrepareScene
            elif isinstance(state, str) and state in ("startGame", "startLobby"):
                playerNames = args[0] if args else []
                if state == "startGame":
                    self.startGame(playerNames)
                else:
                    self.startLobby(playerNames)
            logger.debug(f"Scene initialized: {state}")
        except Exception as e:
            logError(f"Failed to initialize scene: {state}", e)
            raise

    def startGame(self, playerNames: list[str]) -> None:
        """
        Start a new game session.
        
        Args:
            playerNames: List of player names for the game
        """
        try:
            logger.debug("Initializing new game session...")
            
            if not self.network:
                self.network = NetworkConnection()
            
            networkMode = self.network.networkMode
            if networkMode in ("host", "local"):
                lobbyCompleted = True
                self.gameSession = GameSession(playerNames, lobbyCompleted=lobbyCompleted, networkMode=networkMode)
                playerIndex = settingsManager.get("PLAYER_INDEX", 0)
                hostPlayer = self.gameSession.players[playerIndex]
                hostPlayer.setIsHuman(True)
                logger.debug(f"Player with index {hostPlayer.getIndex()} marked as human.")
                logger.debug(f"Player name set to '{hostPlayer.getName()}' from host settings.")
                self.gameSession.onTurnEnded = self.onTurnEnded
                self.gameSession.onShowNotification = self.onShowNotification
            self.network.onInitialGameStateReceived = self.onGameStateReceived
            self.network.onSyncGameState = self.onSyncGameState
            self.network.onJoinRejected = self.onJoinRejected
            self.network.onStartGame = self.onStartGame
            self.network.onClientDisconnected = self.onClientDisconnected
            self.network.onHostDisconnected = self.onHostDisconnected
            if networkMode == "host":
                self.network.onClientConnected = self.onClientConnected
                self.network.onClientSubmittedTurn = self.onClientSubmittedTurn
                self.network.onPlayerClaimed = self.onPlayerClaimed
                self.network.onJoinFailed = self.onJoinFailed
            self.initScene(GameState.GAME)
            logger.debug(f"Game started with {len(playerNames)} players")
            
            if networkMode == "host":
                self.network.sendToAll(encodeMessage("start_game", {"game_session": self.gameSession.serialize()}))
        except Exception as e:
            logError("Failed to start game", e)
            raise

    def startLobby(self, playerNames: list[str]) -> None:
        """
        Start a lobby for network games.
        
        Args:
            playerNames: List of player names for the game
        """
        try:
            logger.debug("Preparing to enter lobby...")
            
            if not self.network:
                self.network = NetworkConnection()
                
            networkMode = self.network.networkMode
            if networkMode in ("host", "local"):
                lobbyCompleted = networkMode == "local"
                self.gameSession = GameSession(playerNames, lobbyCompleted=lobbyCompleted, networkMode=networkMode)
                playerIndex = settingsManager.get("PLAYER_INDEX", 0)
                hostPlayer = self.gameSession.players[playerIndex]
                hostPlayer.setIsHuman(True)
                logger.debug(f"Player with index {hostPlayer.getIndex()} marked as human.")
                logger.debug(f"Player name set to '{hostPlayer.getName()}' from host settings.")
                self.gameSession.onTurnEnded = self.onTurnEnded
                self.gameSession.onShowNotification = self.onShowNotification
            self.network.onInitialGameStateReceived = self.onGameStateReceived
            self.network.onSyncGameState = self.onSyncGameState
            self.network.onJoinRejected = self.onJoinRejected
            self.network.onStartGame = self.onStartGame
            self.network.onClientDisconnected = self.onClientDisconnected
            self.network.onHostDisconnected = self.onHostDisconnected
            if networkMode == "host":
                self.network.onClientConnected = self.onClientConnected
                self.network.onClientSubmittedTurn = self.onClientSubmittedTurn
                self.network.onPlayerClaimed = self.onPlayerClaimed
                self.network.onJoinFailed = self.onJoinFailed
            # Only go to lobby for network modes
            if networkMode != "local":
                self.initScene(GameState.LOBBY)
            else:
                self.initScene(GameState.GAME)
        except Exception as e:
            logError("Failed to start lobby", e)
            raise

    def onGameStateReceived(self, data: dict) -> None:
        """
        Handle received game state from network.
        
        Args:
            data: Serialized game state data
        """
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            self.gameSession.onShowNotification = self.onShowNotification
            logger.debug("Game session replaced with synchronized state from host")

            if hasattr(self.currentScene, 'updateGameSession'):
                self.currentScene.updateGameSession(self.gameSession)

            if self.network.networkMode == "client":
                assigned = False
                for player in self.gameSession.getPlayers():
                    if not player.getIsAI() and not player.isHuman:
                        player.setIsHuman(True)
                        logger.debug(f"Player with index {player.getIndex()} marked as human.")
                        playersList = settingsManager.get("PLAYERS", ["Player 1"])
                        player.name = playersList[0]
                        logger.debug(f"Player name set to '{player.name}' from client settings.")
                        settingsManager.set("PLAYER_INDEX", player.getIndex(), temporary=True)
                        logger.debug(f"Client assigned to player index {player.getIndex()}")
                        assigned = True
                        break

                if assigned:
                    updatedGameState = self.gameSession.serialize()
                    self.network.sendToHost(encodeMessage("player_claimed", updatedGameState))
                    logger.debug("Client claimed player and sent updated game state to host")
                    
                    if self.gameSession.lobbyCompleted:
                        self.initScene(GameState.GAME)
                else:
                    logger.debug("No available player slots for client")
                    self.network.sendToHost(encodeMessage("join_failed", {"reason": "no_slots"}))
                    
        except Exception as e:
            logError("Failed to process received game state", e)

    def onClientConnected(self, conn) -> None:
        """
        Handle new client connection.
        
        Args:
            conn: Network connection to the client
        """
        try:
            logger.debug("Sending current game state to new client...")
            gameState = self.gameSession.serialize()
            message = encodeMessage("init_game_state", gameState)
            conn.sendall((message + "\n").encode())
            logger.debug("Game state sent successfully.")
        except Exception as e:
            logError("Failed to send game state to client", e)

    def onPlayerClaimed(self, data: dict, conn) -> None:
        """
        Handle player claim from client.
        
        Args:
            data: Serialized game state from client with claimed player
            conn: Network connection to the client
        """
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            self.gameSession.onShowNotification = self.onShowNotification
            logger.debug("Host updated game session with client's claimed player")
            
            if hasattr(self.currentScene, 'updateGameSession'):
                self.currentScene.updateGameSession(self.gameSession)
                
            self.broadcastGameState()
        except Exception as e:
            logError("Failed to process player claim", e)

    def onClientSubmittedTurn(self, data: dict) -> None:
        """
        Handle turn submission from client.
        
        Args:
            data: Serialized game state from client
        """
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            self.gameSession.onShowNotification = self.onShowNotification
            logger.debug("Host applied client-submitted game state")
            
            if hasattr(self.currentScene, 'updateGameSession'):
                self.currentScene.updateGameSession(self.gameSession)
                
            self.broadcastGameState()
        except Exception as e:
            logError("Failed to process client submitted turn", e)

    def broadcastGameState(self) -> None:
        """Broadcast current game state to all connected clients."""
        try:
            if self.network.networkMode == "host":
                gameState = self.gameSession.serialize()
                message = encodeMessage("sync_game_state", gameState)
                self.network.sendToAll(message)
                logger.debug("Broadcasted updated game state to all clients.")
        except Exception as e:
            logError("Failed to broadcast game state", e)

    def onStartGame(self, data: dict) -> None:
        """
        Handle start game message from host.
        
        Args:
            data: Start game data with full game session
        """
        try:
            logger.debug("Client received start game message from host")
            if "game_session" in data:
                self.gameSession = GameSession.deserialize(data["game_session"])
                self.gameSession.onTurnEnded = self.onTurnEnded
                self.gameSession.onShowNotification = self.onShowNotification
                if hasattr(self.currentScene, 'updateGameSession'):
                    self.currentScene.updateGameSession(self.gameSession)
            self.initScene(GameState.GAME)
        except Exception as e:
            logError("Failed to handle start game message", e)

    def onSyncGameState(self, data: dict) -> None:
        """
        Handle game state synchronization from host.
        
        Args:
            data: Serialized game state data
        """
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            self.gameSession.onShowNotification = self.onShowNotification
            logger.debug("Client game session updated from host sync.")
            
            if hasattr(self.currentScene, 'updateGameSession'):
                self.currentScene.updateGameSession(self.gameSession)
        except Exception as e:
            logError("Failed to sync game state", e)

    def onTurnEnded(self) -> None:
        """Handle turn completion and network synchronization."""
        try:
            networkMode = settingsManager.get("NETWORK_MODE", "local")
            if networkMode == "local":
                return

            logger.debug("Synchronizing game state after turn...")

            if self.gameSession.getIsFirstRound():
                return

            serialized = self.gameSession.serialize()

            if networkMode == "host":
                message = encodeMessage("sync_game_state", serialized)
                self.network.sendToAll(message)
                logger.debug("Host broadcasted updated game state after turn.")

            elif networkMode == "client":
                message = encodeMessage("submit_turn", serialized)
                self.network.sendToHost(message)
                logger.debug("Client submitted turn to host.")
                
        except Exception as e:
            logError("Failed to handle turn ended", e)

    def onJoinFailed(self, data: dict, conn) -> None:
        """
        Handle failed client join attempt.
        
        Args:
            data: Join failure data
            conn: Network connection to the client
        """
        try:
            reason = data.get("reason", "unspecified")
            logger.debug(f"Client join failed: {reason}")
            response = encodeMessage("join_rejected", {"reason": reason})
            conn.sendall((response + "\n").encode())
            logger.debug("Sent join_rejected response to client.")
        except Exception as e:
            logError("Failed to handle join failure", e)

    def onJoinRejected(self, data: dict) -> None:
        """
        Handle join rejection from host.
        
        Args:
            data: Join rejection data
        """
        try:
            reason = data.get("reason", "unknown")
            logger.debug(f"Join rejected by host. Reason: {reason}")
            self.handleJoinRejected(reason)
        except Exception as e:
            logError("Failed to handle join rejection", e)

    def handleJoinRejected(self, reason: str) -> None:
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
            logError("Failed to handle join rejection", e)

    def getGameSession(self) -> typing.Optional['GameSession']:
        """
        Get the current game session.
        
        Returns:
            Current game session or None if no session exists
        """
        return self.gameSession

    def onClientDisconnected(self, conn) -> None:
        """
        Handle client disconnection (host mode).
        
        Args:
            conn: Network connection to the disconnected client
        """
        try:
            logger.debug("Client disconnected from host")
            
            playerIndex = None
            for player in self.gameSession.getPlayers():
                if player.isHuman and player.getIndex() != settingsManager.get("PLAYER_INDEX", 0):
                    player.setIsHuman(False)
                    player.name = f"Player {player.getIndex() + 1}"
                    playerIndex = player.getIndex()
                    logger.debug(f"Unclaimed player {playerIndex}")
                    break
            
            if playerIndex is not None:
                self.onShowNotification("warning", f"Player {playerIndex + 1} disconnected and is available for rejoin")
            else:
                self.onShowNotification("warning", "A client disconnected")
            
            if hasattr(self.currentScene, 'updateGameSession'):
                self.currentScene.updateGameSession(self.gameSession)
                
        except Exception as e:
            logError("Failed to handle client disconnection", e)

    def onHostDisconnected(self) -> None:
        """
        Handle host disconnection (client mode).
        """
        try:
            logger.debug("Lost connection to host")
            
            self.onShowNotification("error", "Lost connection to host")
            
            pygame.time.delay(2000)
            self.initScene(GameState.MENU)
            
        except Exception as e:
            logError("Failed to handle host disconnection", e)
        
    def onShowNotification(self, notificationType: str, message: str) -> None:
        """
        Handle notification requests from game session.
        
        Args:
            notificationType: Type of notification
            message: Notification message
        """
        try:
            logger.debug(f"onShowNotification called: type={notificationType}, message={message}")
            
            if hasattr(self.currentScene, 'showNotification'):
                logger.debug("Scene has showNotification method, calling it")
                self.currentScene.showNotification(notificationType, message)
            else:
                logger.debug(f"Scene doesn't support notifications: {message}")
        except Exception as e:
            logError("Failed to show notification", e)


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        logError("Critical error in main", e)
        input("Press Enter to exit...")