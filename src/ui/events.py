import pygame
import logging

from models.gameSession import GameSession
from ui.renderer import Renderer
from settings import TILE_SIZE, DEBUG, PLAYER_INDEX, NETWORK_MODE
logger = logging.getLogger(__name__)

class EventHandler:
    """
    Handles user input events such as mouse clicks and keyboard inputs.
    """
    
    def __init__(self):
        """
        Initializes the event handler.
        """
        #self.tilePlaced = False  # Track if a tile was placed this turn
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

            # Always allow input during first round
            if gameSession.getIsFirstRound():
                if event.type == pygame.KEYDOWN:
                    self.keysPressed[event.key] = True
                    if event.key == pygame.K_RETURN:
                        gameSession.placeStartingCard()
                if event.type == pygame.KEYUP:
                    self.keysPressed[event.key] = False
                continue

            # Allow scrolling input for everyone
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.keysPressed[event.key] = (event.type == pygame.KEYDOWN)

            # Block game actions if it's not this player's turn in network mode
            allowAction = True
            if NETWORK_MODE in ("host", "client"):
                currentPlayer = gameSession.getCurrentPlayer()
                if not currentPlayer or currentPlayer.getIndex() != PLAYER_INDEX:
                    allowAction = False

            if allowAction:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handleMouseClick(event, gameSession, renderer)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gameSession.skipCurrentAction()
                    if event.key == pygame.K_RETURN:
                        gameSession.placeStartingCard()
                    if event.key == pygame.K_ESCAPE:
                        return False # Manually quit game

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
        
        logger.debug(f"Registered {event.button}")
        
        if event.button == 1:  # Left-click
            logger.debug("Playing turn...")
            gameSession.playTurn(gridX, gridY, self.detectClickDirection(x, y, gridX, gridY, renderer, gameSession))
            
            """
            if not self.tilePlaced:
                logger.debug("Attempting to place card")
                if gameSession.playCard(gridX, gridY):
                    self.tilePlaced = True  # Track tile placement
            else:
                logger.debug("Attempting to place figure")
                currentPlayer = gameSession.getCurrentPlayer()
                if currentPlayer:
                    direction = self.detectClickDirection(x, y, gridX, gridY, renderer, gameSession)
                    if gameSession.playFigure(currentPlayer, gridX, gridY, direction):
                        logger.debug(f"{currentPlayer.name} placed a figure at ({gridX}, {gridY}) in {direction} direction")
                        self.tilePlaced = False  # Reset for the next turn
                        #gameSession.nextTurn()
            """
        
        if event.button == 3 and gameSession.getCurrentCard():  # Right-click to rotate a card
            logger.debug("currentCard.rotate triggered")
            gameSession.getCurrentCard().rotate() 
            
        if event.button ==2:
            logger.debug(f"logger.debuging card info for card {gridX};{gridY}")
            self.logger.debugCardInfo(gameSession.getGameBoard().getCard(gridX, gridY))
    
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
        logger.debug("Detecting click direction...")
        
        tileScreenX = gridX * TILE_SIZE - renderer.getOffsetX()
        tileScreenY = gridY * TILE_SIZE - renderer.getOffsetY()

        relativeX = mouseX - tileScreenX
        relativeY = mouseY - tileScreenY

        # Retrieve the card at this position
        card = gameSession.gameBoard.getCard(gridX, gridY)
        
        if not card:
            return None  # No card at this position, invalid click
            
        logger.debug(f"Retrieved card {card} at {gridX};{gridY}")

        # Check if the card supports "C" (center placement)
        supportsCenter = False
        
        if card.getTerrains()["C"]:
            supportsCenter = True
        
        logger.debug(f"Card supports C direction: {supportsCenter}")
        
        # Define click region thresholds
        thirdSize = TILE_SIZE // 3  # 1/3 of the tile
        twoThirdSize = 2 * TILE_SIZE // 3  # 2/3 of the tile
        
        if thirdSize < relativeX < twoThirdSize and thirdSize < relativeY < twoThirdSize:
            logger.debug("Detected center placement")
            if supportsCenter:
                logger.debug("Returning C direction")
                return "C"  # Click in center, and center is supported

        # If center is not available, assign the closest N, E, S, or W direction
        distances = {
            "N": relativeY,
            "S": TILE_SIZE - relativeY,
            "W": relativeX,
            "E": TILE_SIZE - relativeX
        }
        
        logger.debug(f"Returning {min(distances, key=distances.get)} direction")
        return min(distances, key=distances.get)  # Assigns the closest direction

    def printCardInfo(self, card):
        """
        Debug method to orint all available card information in the log
        :param card: Card of which info is to be logger.debuged
        """
        if card:
            logger.debug(f"Image: {card.getImage()}")
            logger.debug(f"Terrains: {card.getTerrains()}")
            logger.debug(f"Neighbors: {card.getNeighbors()}")
            logger.debug(f"Connections: {card.getConnections()}")