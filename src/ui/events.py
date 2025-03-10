import pygame

from settings import TILE_SIZE

class EventHandler:
    """
    Handles user input events such as mouse clicks and keyboard inputs.
    """
    
    def __init__(self):
        """
        Initializes the event handler.
        """
        self.selected_tile = None  # Currently held tile for placement
        self.keys_pressed = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
    
    def handle_events(self, game_session, renderer):
        """
        Processes Pygame events (mouse clicks, keyboard input).
        :param game_session: The GameSession object managing the game state.
        :param renderer: The Renderer object handling board rendering.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event, game_session, renderer)
            
            if event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
            
            if event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
        
        self.handle_key_hold(renderer)
        
        return True  # Continue game loop
    
    def handle_mouse_click(self, event, game_session, renderer):
        """
        Handles mouse click events to place tiles.
        :param event: The Pygame event object.
        :param game_session: The GameSession object managing the game state.
        """
        x, y = event.pos
        grid_x, grid_y = (x + renderer.offset_x) // TILE_SIZE, (y + renderer.offset_y) // TILE_SIZE  # Convert screen position to grid position
        
        if event.button == 1:  # Left-click to place a tile
            if self.selected_tile is None:
                self.selected_tile = game_session.draw_tile()  # Draw a new tile if none is selected
            
            if self.selected_tile:
                game_session.place_tile(self.selected_tile, grid_x, grid_y)
                renderer.draw_side_panel(self.selected_tile)  # Ensure selected tile is drawn in side panel
                #self.selected_tile = None  # Reset after placement
                self.selected_tile = game_session.draw_tile()  # Draw a new tile if none is selected
    
    def handle_key_hold(self, renderer):
        """
        Handles continuous key press for scrolling.
        :param renderer: The Renderer object handling board rendering.
        """
        if self.keys_pressed.get(pygame.K_w, False) or self.keys_pressed.get(pygame.K_UP, False):
            renderer.scroll("up")
        if self.keys_pressed.get(pygame.K_s, False) or self.keys_pressed.get(pygame.K_DOWN, False):
            renderer.scroll("down")
        if self.keys_pressed.get(pygame.K_a, False) or self.keys_pressed.get(pygame.K_LEFT, False):
            renderer.scroll("left")
        if self.keys_pressed.get(pygame.K_d, False) or self.keys_pressed.get(pygame.K_RIGHT, False):
            renderer.scroll("right")