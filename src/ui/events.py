import pygame
from models.gameSession import GameSession
from ui.renderer import Renderer
from settings import TILE_SIZE

class EventHandler:
    """
    Handles user input events such as mouse clicks and keyboard inputs.
    """
    
    def __init__(self):
        """
        Initializes the event handler.
        """
        self.tilePlaced = False  # Track if a tile was placed this turn
        self.keysPressed = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False,
                            pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False,
                            pygame.K_SPACE: False, pygame.K_RETURN: False}
    
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
                if event.key == pygame.K_RETURN:
                    gameSession.detectStructures()
                if event.key == pygame.K_SPACE and self.tilePlaced:
                    print("Skipping meeple placement")
                    self.tilePlaced = False  # Reset for the next turn
                    gameSession.nextTurn()
                if event.key == pygame.K_SPACE and not self.tilePlaced:
                    gameSession.discardCurrentCard()  # Call discard method on spacebar press
            
            if event.type == pygame.KEYUP:
                self.keysPressed[event.key] = False
        
        self.handleKeyHold(renderer)
        
        return True  # Continue game loop
    
    def handleMouseClick(self, event, gameSession, renderer):
        """
        Handles mouse click events to place tiles first, then figures
        :param event: The Pygame event object
        :param gameSession: The GameSession object managing the game state
        :param renderer: The Renderer object handling board rendering
        """
        x, y = event.pos
        gridX, gridY = (x + renderer.getOffsetX()) // TILE_SIZE, (y + renderer.getOffsetY()) // TILE_SIZE  # Convert screen position to grid position
        
        print(f"Registered {event.button}")
        
        if event.button == 1:  # Left-click
            if not self.tilePlaced:
                print("Attempting to place card")
                if gameSession.playCard(gridX, gridY):
                    self.tilePlaced = True  # Track tile placement
            else:
                print("Attempting to place figure")
                currentPlayer = gameSession.getCurrentPlayer()
                if currentPlayer:
                    direction = self.detectClickDirection(x, y, gridX, gridY, renderer, gameSession)
                    if gameSession.playFigure(currentPlayer, gridX, gridY, direction):
                        print(f"{currentPlayer.name} placed a figure at ({gridX}, {gridY}) in {direction} direction")
                        self.tilePlaced = False  # Reset for the next turn
                        #gameSession.nextTurn()
        
        if event.button == 3 and gameSession.getCurrentCard():  # Right-click to rotate a card
            print("currentCard.rotate triggered")
            gameSession.getCurrentCard().rotate() 
            
        if event.button ==2:
            print(f"Printing card info for card {gridX};{gridY}")
            self.printCardInfo(gameSession.getGameBoard().getCard(gridX, gridY))
    
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
            
    def detectClickDirection(self, mouseX, mouseY, gridX, gridY, renderer, gameSession):
        """
        Determines whether the click was in the North, South, East, West, or Center of the tile.
        If the card supports "C" (center), it will assign "C". Otherwise, it finds the closest valid direction.
        
        :param mouseX: Mouse X position
        :param mouseY: Mouse Y position
        :param gridX: Tile X position
        :param gridY: Tile Y position
        :param renderer: The Renderer object handling board rendering.
        :param gameSession: The GameSession object managing the game state (to check card details).
        :return: The direction ('N', 'S', 'E', 'W', or 'C') where the click occurred.
        """
        print("Detecting click direction...")
        
        tileScreenX = gridX * TILE_SIZE - renderer.getOffsetX()
        tileScreenY = gridY * TILE_SIZE - renderer.getOffsetY()

        relativeX = mouseX - tileScreenX
        relativeY = mouseY - tileScreenY

        # Retrieve the card at this position
        card = gameSession.gameBoard.getCard(gridX, gridY)
        
        if not card:
            return None  # No card at this position, invalid click
            
        print(f"Retrieved card {card} at {gridX};{gridY}")

        # Check if the card supports "C" (center placement)
        supportsCenter = False
        
        if card.getTerrains()["C"]:
            supportsCenter = True
        
        print(f"Card supports C direction: {supportsCenter}")
        
        # Define click region thresholds
        thirdSize = TILE_SIZE // 3  # 1/3 of the tile
        twoThirdSize = 2 * TILE_SIZE // 3  # 2/3 of the tile
        
        if thirdSize < relativeX < twoThirdSize and thirdSize < relativeY < twoThirdSize:
            print("Detected center placement")
            if supportsCenter:
                print("Returning C direction")
                return "C"  # Click in center, and center is supported

        # If center is not available, assign the closest N, E, S, or W direction
        distances = {
            "N": relativeY,
            "S": TILE_SIZE - relativeY,
            "W": relativeX,
            "E": TILE_SIZE - relativeX
        }
        
        print(f"Returning {min(distances, key=distances.get)} direction")
        return min(distances, key=distances.get)  # Assigns the closest direction

    def printCardInfo(self, card):
        """
        Debug method to print all available card information in the log
        :param card: Card of which info is to be printed
        """
        if card:
            print(f"Image: {card.getImage()}")
            print(f"Terrains: {card.getTerrains()}")
            print(f"Neighbors: {card.getNeighbors()}")
            print(f"Connections: {card.getConnections()}")