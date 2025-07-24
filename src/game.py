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
from ui.lobbyScene import LobbyScene  # NEW: import the lobby scene

# Configure logging with exception handling
configureLogging()
logger = logging.getLogger(__name__)


class Game:
    def __init__(self) -> None:
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

    def quit(self):
        try:
            self.cleanupPreviousGame()
            pygame.quit()
            logger.debug("Game quit successfully")
            exit()
        except Exception as e:
            logError("Error during game quit", e)
            exit()

    def cleanupPreviousGame(self) -> None:
        """Clean up resources from previous game session"""
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
        try:
            logger.debug("Initializing new game session...")
            self.network = NetworkConnection()
            networkMode = self.network.networkMode
            if networkMode in ("host", "local"):
                lobbyCompleted = True
                self.gameSession = GameSession(playerNames, lobbyCompleted=lobbyCompleted, networkMode=networkMode)
                # Assign host as human player
                playerIndex = settingsManager.get("PLAYER_INDEX", 0)
                hostPlayer = self.gameSession.players[playerIndex]
                hostPlayer.setIsHuman(True)
                logger.debug(f"Player with index {hostPlayer.getIndex()} marked as human.")
                logger.debug(f"Player name set to '{hostPlayer.getName()}' from host settings.")
                self.gameSession.onTurnEnded = self.onTurnEnded
                self.gameSession.onShowNotification = self.onShowNotification
            # Set up network callbacks
            self.network.onInitialGameStateReceived = self.onGameStateReceived
            self.network.onSyncGameState = self.onSyncGameState
            self.network.onJoinRejected = self.onJoinRejected
            if networkMode == "host":
                self.network.onClientConnected = self.onClientConnected
                self.network.onClientSubmittedTurn = self.onClientSubmittedTurn
                self.network.onJoinFailed = self.onJoinFailed
            self.initScene(GameState.GAME)
            logger.debug(f"Game started with {len(playerNames)} players")
        except Exception as e:
            logError("Failed to start game", e)
            raise

    def startLobby(self, playerNames: list[str]) -> None:
        try:
            logger.debug("Preparing to enter lobby...")
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
            # Only go to lobby for network modes
            if networkMode != "local":
                self.initScene(GameState.LOBBY)
            else:
                self.initScene(GameState.GAME)
        except Exception as e:
            logError("Failed to start lobby", e)
            raise

    def onGameStateReceived(self, data: dict) -> None:
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            logger.debug("Game session replaced with synchronized state from host")

            if self.network.networkMode == "client":
                assigned = False
                for player in self.gameSession.getPlayers():
                    if not player.getIsAI() and not player.isHuman:
                        player.isHuman = True
                        logger.debug(f"Player with index {player.getIndex()} marked as human.")
                        playersList = settingsManager.get("PLAYERS", ["Player 1"])
                        player.name = playersList[0]
                        logger.debug(f"Player name set to '{player.name}' from client settings.")
                        settingsManager.set("PLAYER_INDEX", player.getIndex(), temporary=True)
                        logger.debug(f"Client assigned to player index {player.getIndex()}")
                        assigned = True
                        break

                if assigned:
                    self.network.sendToHost(encodeMessage("ack_game_state", {"status": "ok"}))
                else:
                    logger.debug("No available player slots for client")
                    self.network.sendToHost(encodeMessage("join_failed", {"reason": "no_slots"}))
                    
        except Exception as e:
            logError("Failed to process received game state", e)

    def onClientConnected(self, conn):
        try:
            logger.debug("Sending current game state to new client...")
            gameState = self.gameSession.serialize()
            message = encodeMessage("init_game_state", gameState)
            conn.sendall((message + "\n").encode())
            logger.debug("Game state sent successfully.")
        except Exception as e:
            logError("Failed to send game state to client", e)

    def onClientSubmittedTurn(self, data):
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            logger.debug("Host applied client-submitted game state")
            self.broadcastGameState()
        except Exception as e:
            logError("Failed to process client submitted turn", e)

    def broadcastGameState(self):
        try:
            if self.network.networkMode == "host":
                gameState = self.gameSession.serialize()
                message = encodeMessage("sync_game_state", gameState)
                self.network.sendToAll(message)
                logger.debug("Broadcasted updated game state to all clients.")
        except Exception as e:
            logError("Failed to broadcast game state", e)

    def onSyncGameState(self, data):
        try:
            self.gameSession = GameSession.deserialize(data)
            self.gameSession.onTurnEnded = self.onTurnEnded
            logger.debug("Client game session updated from host sync.")
        except Exception as e:
            logError("Failed to sync game state", e)

    def onTurnEnded(self):
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

    def onJoinFailed(self, data, conn):
        try:
            reason = data.get("reason", "unspecified")
            logger.debug(f"Client join failed: {reason}")
            response = encodeMessage("join_rejected", {"reason": reason})
            conn.sendall((response + "\n").encode())
            logger.debug("Sent join_rejected response to client.")
        except Exception as e:
            logError("Failed to handle join failure", e)

    def onJoinRejected(self, data):
        try:
            reason = data.get("reason", "unknown")
            logger.debug(f"Join rejected by host. Reason: {reason}")
            self.handleJoinRejected(reason)
        except Exception as e:
            logError("Failed to handle join rejection", e)

    def handleJoinRejected(self, reason):
        try:
            logger.debug(f"Handling join rejection (reason: {reason})")
            print(f"Join rejected: {reason}")
            pygame.time.delay(3000)
            self.quit()
        except Exception as e:
            logError("Failed to handle join rejection", e)

    def getGameSession(self) -> typing.Optional['GameSession']:
        return self.gameSession
        
    def onShowNotification(self, notificationType, message):
        """
        Handle notification requests from game session
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