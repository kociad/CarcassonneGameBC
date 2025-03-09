import pygame
from settings import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

class Renderer:
    """
    Handles rendering of the game board, UI elements, and placed tiles.
    """
    
    def __init__(self, screen):
        """
        Initializes the renderer with a given Pygame screen and scrolling offset.
        :param screen: The Pygame display surface.
        """
        self.screen = screen
        self.offset_x = 0
        self.offset_y = 0
        self.scroll_speed = 10  # Adjust scrolling speed as needed
    
    def draw_board(self, board):
        """
        Draws the game board, including grid lines and placed tiles.
        """
        self.screen.fill((0, 128, 0))  # Green background for the board
        
        # Draw grid lines
        for x in range(0, board.grid_size * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (x - self.offset_x, 0 - self.offset_y), (x - self.offset_x, board.grid_size * TILE_SIZE - self.offset_y))
        for y in range(0, board.grid_size * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offset_x, y - self.offset_y), (board.grid_size * TILE_SIZE - self.offset_x, y - self.offset_y))
        
        # Draw placed tiles
        for y in range(board.grid_size):
            for x in range(board.grid_size):
                tile = board.get_tile(x, y)
                if tile:
                    self.screen.blit(tile.image, (x * TILE_SIZE - self.offset_x, y * TILE_SIZE - self.offset_y))
    
    def draw_side_panel(self, selected_tile):
        """
        Draws a side panel where the currently selected tile will be displayed.
        :param selected_tile: The tile currently selected by the player.
        """
        panel_x = WINDOW_WIDTH - 200  # Panel width of 200 pixels
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, 0, 200, WINDOW_HEIGHT))  # Dark grey background
        
        if selected_tile:
            tile_x = panel_x + 45
            tile_y = 50
            self.screen.blit(selected_tile.image, (tile_x, tile_y))
    
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
            self.offset_y -= self.scroll_speed
        elif direction == "down":
            self.offset_y += self.scroll_speed
        elif direction == "left":
            self.offset_x -= self.scroll_speed
        elif direction == "right":
            self.offset_x += self.scroll_speed
