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
        #self.selectedCard = None  # Currently held card for placement
        self.keysPressed = {pygame.K_w: False,
                            pygame.K_s: False,
                            pygame.K_a: False,
                            pygame.K_d: False,
                            pygame.K_UP: False,
                            pygame.K_DOWN: False,
                            pygame.K_LEFT: False,
                            pygame.K_RIGHT: False,
                            pygame.K_SPACE: False}
    
    def handleEvents(self, gameSession, renderer):
        """
        Processes Pygame events (mouse clicks, keyboard input).
        :param gameSession: The GameSession object managing the game state.
        :param renderer: The Renderer object handling board rendering.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handleMouseClick(event, gameSession, renderer)
            
            if event.type == pygame.KEYDOWN:
                self.keysPressed[event.key] = True
                if event.key == pygame.K_SPACE:
                    gameSession.discardCurrentCard()  # Call discard method on spacebar press
            
            if event.type == pygame.KEYUP:
                self.keysPressed[event.key] = False
        
        self.handleKeyHold(renderer)
        
        return True  # Continue game loop
    
    def handleMouseClick(self, event, gameSession, renderer):
        """
        Handles mouse click events to place cards.
        :param event: The Pygame event object.
        :param gameSession: The GameSession object managing the game state.
        """
        x, y = event.pos
        gridX, gridY = (x + renderer.offsetX) // TILE_SIZE, (y + renderer.offsetY) // TILE_SIZE  # Convert screen position to grid position
        
        print(f"Registered mouse button click {event.button}")
        
        if event.button == 1:
            print("playCard triggered")
            gameSession.playCard(gridX, gridY) # Play a card if LMB is pressed
                
        if event.button == 3 and gameSession.currentCard: # Right-click to rotate a card
            print("currentCard.rotate triggered")
            gameSession.currentCard.rotate() 
    
    def handleKeyHold(self, renderer):
        """
        Handles continuous key press for scrolling.
        :param renderer: The Renderer object handling board rendering.
        """
        if self.keysPressed.get(pygame.K_w) or self.keysPressed.get(pygame.K_UP):
            renderer.scroll("up")
        if self.keysPressed.get(pygame.K_s) or self.keysPressed.get(pygame.K_DOWN):
            renderer.scroll("down")
        if self.keysPressed.get(pygame.K_a) or self.keysPressed.get(pygame.K_LEFT):
            renderer.scroll("left")
        if self.keysPressed.get(pygame.K_d) or self.keysPressed.get(pygame.K_RIGHT):
            renderer.scroll("right")