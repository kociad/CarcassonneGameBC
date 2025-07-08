import pygame
import logging
from datetime import datetime

from ui.renderer import Renderer
from ui.mainMenuScene import MainMenuScene
from ui.settingsScene import SettingsScene
from ui.scene import Scene
from ui.gameScene import GameScene
from gameState import GameState
from utils.loggingConfig import configureLogging
from models.gameSession import GameSession
from network.connection import NetworkConnection
from network.message import encodeMessage

import settings

# Configure logging
configureLogging()
logger = logging.getLogger()


class Game:
    def __init__(self):
        pygame.init()

        if settings.FULLSCREEN:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        pygame.display.set_caption("Carcassonne")

        self.renderer = Renderer(self.screen)
        self.clock = pygame.time.Clock()
        self.running = True

        # Game-related attributes (deferred until game starts)
        self.gameSession = None
        self.network = None

        self.currentScene = None
        self.initScene(GameState.MENU)

    def run(self):
        while self.running:
            events = pygame.event.get()
            self.currentScene.handleEvents(events)
            self.currentScene.update()
            self.currentScene.draw()

    def quit(self):
        if self.network:
            self.network.close()
        pygame.quit()
        exit()

    def initScene(self, state):
        if state == GameState.MENU:
            self.currentScene = MainMenuScene(self.screen, self.initScene, self.startGame)
        elif state == GameState.GAME:
            self.currentScene = GameScene(
                self.screen, self.initScene, self.gameSession,
                self.renderer, self.clock, self.network
            )
        elif state == GameState.SETTINGS:
            self.currentScene = SettingsScene(self.screen, self.initScene)

    def startGame(self, playerNames):
        logger.debug("Initializing new game session...")

        self.gameSession = GameSession(playerNames)
        self.network = NetworkConnection()

        self.network.onGameStateReceived = self.onGameStateReceived
        self.network.onSyncGameState = self.onSyncGameState

        if self.network.networkMode == "host":
            self.network.onClientConnected = self.onClientConnected
            self.network.onClientSubmittedTurn = self.onClientSubmittedTurn

        self.gameSession.onTurnEnded = self.onTurnEnded

        self.initScene(GameState.GAME)

    def onGameStateReceived(self, data):
        self.gameSession = GameSession.deserialize(data)
        self.gameSession.onTurnEnded = self.onTurnEnded
        logger.debug("Game session replaced with synchronized state from host")
        if self.network.networkMode == "client":
            self.network.sendToHost(encodeMessage("ack_game_state", {"status": "ok"}))

    def onClientConnected(self, conn):
        logger.debug("Sending current game state to new client...")
        gameState = self.gameSession.serialize()
        try:
            message = encodeMessage("init_game_state", gameState)
            conn.sendall((message + "\n").encode())
            logger.debug("Game state sent successfully.")
        except Exception as e:
            logger.debug(f"Failed to send game state to client: {e}")

    def onClientSubmittedTurn(self, data):
        self.gameSession = GameSession.deserialize(data)
        self.gameSession.onTurnEnded = self.onTurnEnded
        logger.debug("Host applied client-submitted game state")
        self.broadcastGameState()

    def broadcastGameState(self):
        if self.network.networkMode == "host":
            gameState = self.gameSession.serialize()
            message = encodeMessage("sync_game_state", gameState)
            self.network.sendToAll(message)
            logger.debug("Broadcasted updated game state to all clients.")

    def onSyncGameState(self, data):
        self.gameSession = GameSession.deserialize(data)
        self.gameSession.onTurnEnded = self.onTurnEnded
        logger.debug("Client game session updated from host sync.")

    def onTurnEnded(self):
        if self.network.networkMode == "local":
            return

        logger.debug("Synchronizing game state after turn...")

        if self.gameSession.getIsFirstRound():
            return

        serialized = self.gameSession.serialize()

        if self.network.networkMode == "host":
            message = encodeMessage("sync_game_state", serialized)
            self.network.sendToAll(message)
            logger.debug("Host broadcasted updated game state after turn.")

        elif self.network.networkMode == "client":
            message = encodeMessage("submit_turn", serialized)
            self.network.sendToHost(message)
            logger.debug("Client submitted turn to host.")


if __name__ == "__main__":
    game = Game()
    game.run()
