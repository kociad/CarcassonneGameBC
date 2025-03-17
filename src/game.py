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
        self.renderer.drawBoard(self.gameSession.getGameBoard(), self.gameSession.getPlacedFigures())
        self.renderer.updateDisplay()
        self.eventHandler = EventHandler()
        self.clock = pygame.time.Clock()
        
        self.running = True  # Game loop control
    
    def run(self):
        """
        Runs the main game loop.
        """
        while self.running:
            self.running = self.eventHandler.handleEvents(self.gameSession, self.renderer)
            
            self.renderer.drawBoard(self.gameSession.getGameBoard(), self.gameSession.getPlacedFigures())
            self.renderer.drawSidePanel(self.gameSession.getCurrentCard(), len(self.gameSession.getCardsDeck()) + 1, self.gameSession.getCurrentPlayer(), self.gameSession.getPlacedFigures())

            self.renderer.updateDisplay()
            
            self.clock.tick(FPS)
        
        self.quit()
    
    def quit(self):
        """
        Cleans up resources and exits Pygame.
        """
        pygame.quit()
        exit()

if __name__ == "__main__":
    playerNames = ["Player 1", "Player 2"]  # Example player names
    game = Game(playerNames)
    game.run()