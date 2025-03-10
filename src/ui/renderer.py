import pygame
from settings import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

class Renderer:
    """
    Handles rendering of the game board, UI elements, and placed cards.
    """
    
    def __init__(self, screen):
        """
        Initializes the renderer with a given Pygame screen and scrolling offset.
        :param screen: The Pygame display surface.
        """
        self.screen = screen
        self.offsetX = 0
        self.offsetY = 0
        self.scrollSpeed = 10  # Adjust scrolling speed as needed
    
    def draw_board(self, gameBoard):
        """
        Draws the game board, including grid lines and placed cards.
        """
        self.screen.fill((0, 128, 0))  # Green background for the board
        
        # Draw grid lines
        for x in range(0, gameBoard.gridSize * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.gridSize * TILE_SIZE - self.offsetY))
        for y in range(0, gameBoard.gridSize * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.gridSize * TILE_SIZE - self.offsetX, y - self.offsetY))
        
        # Draw placed cards
        for y in range(gameBoard.gridSize):
            for x in range(gameBoard.gridSize):
                card = gameBoard.getCard(x, y)
                if card:
                    self.screen.blit(card.image, (x * TILE_SIZE - self.offsetX, y * TILE_SIZE - self.offsetY))
    
    def draw_side_panel(self, selected_card):
        """
        Draws a side panel where the currently selected card will be displayed.
        :param selected_card: The card currently selected by the player.
        """
        panel_x = WINDOW_WIDTH - 200  # Panel width of 200 pixels
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, 0, 200, WINDOW_HEIGHT))  # Dark grey background
        
        if selected_card:
            card_x = panel_x + 45
            card_y = 50
            self.screen.blit(selected_card.image, (card_x, card_y))
    
    def update_display(self):
        """
        Updates the Pygame display with the latest frame.
        """
        pygame.display.flip()
    
    def scroll(self, direction):
        """
        Scrolls the view of the board based on user input.
        :param direction: The direction to scroll ('up', 'down', 'left', 'right').
        """
        if direction == "up":
            self.offsetY -= self.scrollSpeed
        elif direction == "down":
            self.offsetY += self.scrollSpeed
        elif direction == "left":
            self.offsetX -= self.scrollSpeed
        elif direction == "right":
            self.offsetX += self.scrollSpeed
