import pygame
import logging

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, PLAYERS, DEBUG
from models.gameSession import GameSession
from models.player import Player
from ui.renderer import Renderer
from ui.events import EventHandler
from network.connection import NetworkConnection
from network.message import encodeMessage

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

class Game:
    """
    Manages the main game loop and interactions.
    """
    
    def __init__(self, playerNames):
        """
        Initializes the game, setting up Pygame and core components.
        :param playerNames: List of player names participating in the game.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Carcassonne")
        
        self.gameSession = GameSession(playerNames)
        self.renderer = Renderer(self.screen)
        self.renderer.drawBoard(self.gameSession.getGameBoard(), self.gameSession.getPlacedFigures(), self.gameSession.getStructures(), self.gameSession.getIsFirstRound(), self.gameSession.getGameOver(), self.gameSession.getPlayers())
        self.renderer.updateDisplay()
        self.eventHandler = EventHandler()
        self.clock = pygame.time.Clock()
        self.network = NetworkConnection()
        
        if self.network.networkMode == "host":
            self.network.onClientConnected = self.onClientConnected
        elif self.network.networkMode == "client":
            self.network.onInitialGameStateReceived = self.onInitialGameStateReceived
        
        self.network.onInitialGameStateReceived = self.onInitialGameStateReceived
        
        self.running = True  # Game loop control
    
    def run(self):
        """
        Runs the main game loop.
        """
        while self.running:
            currentPlayer = self.gameSession.getCurrentPlayer()

            if self.gameSession.getIsFirstRound() or not currentPlayer.getIsAI() or self.gameSession.getGameOver():
                # Wait for human input
                self.running = self.eventHandler.handleEvents(self.gameSession, self.renderer)
            else:
                # AI player's turn — no need to wait for input
                currentPlayer.playTurn(self.gameSession)

            # Always update visuals
            self.renderer.drawBoard(
                self.gameSession.getGameBoard(),
                self.gameSession.getPlacedFigures(),
                self.gameSession.getStructures(),
                self.gameSession.getIsFirstRound(),
                self.gameSession.getGameOver(),
                self.gameSession.getPlayers()
            )
            self.renderer.drawSidePanel(
                self.gameSession.getCurrentCard(),
                len(self.gameSession.getCardsDeck()) + 1,
                self.gameSession.getCurrentPlayer(),
                self.gameSession.getPlacedFigures(),
                self.gameSession.getStructures()
            )
            self.renderer.updateDisplay()

            self.clock.tick(FPS)
            
    def quit(self):
        """
        Cleans up resources and exits Pygame.
        """
        if self.network:
            self.network.close()
        pygame.quit()
        exit()
        
    def onInitialGameStateReceived(self, data):
        from models.gameSession import GameSession
        self.gameSession = GameSession.deserialize(data)
        logger.info("[GAME] Game session replaced with synchronized state from host")

        # Send ACK to host
        if self.network.networkMode == "client":
            self.network.sendToHost(encodeMessage("ack_game_state", {"status": "ok"}))
            
    def onClientConnected(self, conn):
        from network.message import encodeMessage
        logger.info("[GAME] Sending current game state to new client...")
        serialized = self.gameSession.serialize()
        message = encodeMessage("init_game_state", serialized)
        try:
            conn.sendall(message.encode())
        except Exception as e:
            logger.error(f"[GAME] Failed to send game state to client: {e}")
        
if __name__ == "__main__":
    playerNames = PLAYERS  # Example player names
    game = Game(playerNames)
    game.run()