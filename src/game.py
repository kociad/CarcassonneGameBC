import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from models.gameSession import GameSession
from models.player import Player
from ui.renderer import Renderer
from ui.events import EventHandler

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
        self.renderer.drawBoard(self.gameSession.getGameBoard(), self.gameSession.getPlacedFigures(), self.gameSession.getStructures())
        self.renderer.updateDisplay()
        self.eventHandler = EventHandler()
        self.clock = pygame.time.Clock()
        
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
                self.gameSession.getStructures()
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
        pygame.quit()
        exit()

if __name__ == "__main__":
    playerNames = ["AI_Player 1", "AI_Player 2"]  # Example player names
    game = Game(playerNames)
    game.run()