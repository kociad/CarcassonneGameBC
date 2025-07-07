import pygame
import logging

from ui.scene import Scene
from gameState import GameState

from settings import TILE_SIZE, PLAYER_INDEX, NETWORK_MODE, FPS

logger = logging.getLogger(__name__)

class GameScene(Scene):
    def __init__(self, screen, switchSceneCallback, gameSession, renderer, clock, network):
        super().__init__(screen, switchSceneCallback)
        self.session = gameSession
        self.renderer = renderer
        self.clock = clock
        self.network = network

        self.keysPressed = {
            pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False,
            pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False
        }

    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.keysPressed[event.key] = (event.type == pygame.KEYDOWN)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)

            # Block game actions if it's not this player's turn in network mode
            allowAction = True
            if NETWORK_MODE in ("host", "client"):
                currentPlayer = self.session.getCurrentPlayer()
                if not currentPlayer or currentPlayer.getIndex() != PLAYER_INDEX or self.session.getGameOver():
                    allowAction = False

            if allowAction:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handleMouseClick(event)
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.session.skipCurrentAction()
                        
        self.handleKeyHold()

    def handleMouseClick(self, event):
        x, y = event.pos
        gridX, gridY = (x + self.renderer.getOffsetX()) // TILE_SIZE, (y + self.renderer.getOffsetY()) // TILE_SIZE

        logger.debug(f"Registered {event.button}")

        if event.button == 1:
            direction = self.detectClickDirection(x, y, gridX, gridY)
            logger.debug(f"self.session.playTurn triggered for {gridX},{gridY}")
            self.session.playTurn(gridX, gridY, direction)

        if event.button == 3 and self.session.getCurrentCard():
            logger.debug("currentCard.rotate triggered")
            self.session.getCurrentCard().rotate()

        """
        if event.button == 2:
            logger.debug(f"Logging card info for {gridX};{gridY}")
            self.printCardInfo(self.session.getGameBoard().getCard(gridX, gridY))
        """
        
    def handleKeyHold(self):
        if self.keysPressed.get(pygame.K_w) or self.keysPressed.get(pygame.K_UP):
            self.renderer.scroll("up")
        if self.keysPressed.get(pygame.K_s) or self.keysPressed.get(pygame.K_DOWN):
            self.renderer.scroll("down")
        if self.keysPressed.get(pygame.K_a) or self.keysPressed.get(pygame.K_LEFT):
            self.renderer.scroll("left")
        if self.keysPressed.get(pygame.K_d) or self.keysPressed.get(pygame.K_RIGHT):
            self.renderer.scroll("right")
            
    def detectClickDirection(self, mouseX, mouseY, gridX, gridY):
        tileScreenX = gridX * TILE_SIZE - self.renderer.getOffsetX()
        tileScreenY = gridY * TILE_SIZE - self.renderer.getOffsetY()

        relativeX = mouseX - tileScreenX
        relativeY = mouseY - tileScreenY

        card = self.session.getGameBoard().getCard(gridX, gridY)
        if not card:
            return None

        logger.debug(f"Retrieved card {card} at {gridX};{gridY}")

        supportsCenter = card.getTerrains().get("C") is not None

        thirdSize = TILE_SIZE // 3
        twoThirdSize = 2 * TILE_SIZE // 3

        if thirdSize < relativeX < twoThirdSize and thirdSize < relativeY < twoThirdSize:
            if supportsCenter:
                return "C"

        distances = {
            "N": relativeY,
            "S": TILE_SIZE - relativeY,
            "W": relativeX,
            "E": TILE_SIZE - relativeX
        }

        return min(distances, key=distances.get)
        
    """
    def printCardInfo(self, card):
        if card:
            logger.debug(f"Image: {card.getImage()}")
            logger.debug(f"Terrains: {card.getTerrains()}")
            logger.debug(f"Neighbors: {card.getNeighbors()}")
            logger.debug(f"Connections: {card.getConnections()}")
    """
    
    def update(self):
        self.clock.tick(60)
        
    def draw(self):
        self.renderer.drawBoard(
            self.session.getGameBoard(),
            self.session.getPlacedFigures(),
            self.session.getStructures(),
            self.session.getIsFirstRound(),
            self.session.getGameOver(),
            self.session.getPlayers()
        )
        self.renderer.drawSidePanel(
            self.session.getCurrentCard(),
            len(self.session.getCardsDeck()) + 1,
            self.session.getCurrentPlayer(),
            self.session.getPlacedFigures(),
            self.session.getStructures()
        )
        self.renderer.updateDisplay()
        
    def update(self):
        if self.session.getGameOver():
            self.clock.tick(FPS)
            return

        currentPlayer = self.session.getCurrentPlayer()

        if self.session.getIsFirstRound() or not currentPlayer.getIsAI():
            self.clock.tick(FPS)
            return

        # AI turn
        currentPlayer.playTurn(self.session)
        self.clock.tick(FPS)