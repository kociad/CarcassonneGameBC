import pygame
import logging

from datetime import datetime

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, PLAYERS, DEBUG
from models.gameSession import GameSession
from models.player import Player
from ui.renderer import Renderer
from ui.events import EventHandler
from network.connection import NetworkConnection
from network.message import encodeMessage

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# Avoid adding handlers multiple times (especially in interactive/restarts)
if not logger.hasHandlers():
    # Generate filename
    log_filename = datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.log")

    # File handler
    file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Add both handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

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
            self.network.onClientSubmittedTurn = self.onClientSubmittedTurn
        elif self.network.networkMode == "client":
            self.network.onInitialGameStateReceived = self.onInitialGameStateReceived
        
        self.network.onInitialGameStateReceived = self.onInitialGameStateReceived
        self.network.onSyncGameState = self.onSyncGameState
        
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
                
                # If turn finished and we're the client, send updated state to host
                if not self.gameSession.getIsFirstRound() and self.network.networkMode == "client":
                    serialized = self.gameSession.serialize()
                    message = encodeMessage("submit_turn", serialized)
                    self.network.sendToHost(message)
                    logger.debug("Client submitted turn to host")
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
        self.gameSession = GameSession.deserialize(data)
        logger.debug("Game session replaced with synchronized state from host")

        # Send ACK to host
        if self.network.networkMode == "client":
            self.network.sendToHost(encodeMessage("ack_game_state", {"status": "ok"}))
            
    def onClientConnected(self, conn):
        logger.debug("Sending current game state to new client...")
        gameState = self.gameSession.serialize()
        logger.debug(f"Serializing game state with {len(self.gameSession.getPlayers())} players and {len(self.gameSession.getCardsDeck())} cards...")

        try:
            message = encodeMessage("init_game_state", gameState)
            logger.debug(f"Message length: {len(message)} bytes")
            conn.sendall((message + "\n").encode())
            logger.debug("Game state sent successfully.")
        except Exception as e:
            logger.debug(f"Failed to send game state to client: {e}")
            
    def onClientSubmittedTurn(self, data):
        self.gameSession = GameSession.deserialize(data)
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
        logger.debug("Client game session updated from host sync.")
        
if __name__ == "__main__":
    playerNames = PLAYERS  # Example player names
    game = Game(playerNames)
    game.run()
