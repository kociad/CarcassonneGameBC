import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from models.gameSession import GameSession
from ui.renderer import Renderer
from ui.events import EventHandler

class Game:
    """
    Manages the main game loop and interactions.
    """
    
    def __init__(self, player_names):
        """
        Initializes the game, setting up Pygame and core components.
        :param player_names: List of player names participating in the game.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Carcassonne")
        
        self.gameSession = GameSession(player_names)
        self.renderer = Renderer(self.screen)
        self.renderer.draw_board(self.gameSession.gameBoard)
        self.renderer.update_display()
        self.eventHandler = EventHandler()
        self.clock = pygame.time.Clock()
        
        self.running = True  # Game loop control
    
    def run(self):
        """
        Runs the main game loop.
        """
        while self.running:
            self.running = self.eventHandler.handle_events(self.gameSession, self.renderer)
            
            self.renderer.draw_board(self.gameSession.gameBoard)
            self.renderer.draw_side_panel(self.gameSession.currentCard)

            self.renderer.update_display()
            
            self.clock.tick(FPS)
        
        self.quit()
    
    def quit(self):
        """
        Cleans up resources and exits Pygame.
        """
        pygame.quit()
        exit()

if __name__ == "__main__":
    player_names = ["Player 1", "Player 2"]  # Example player names
    game = Game(player_names)
    game.run()
