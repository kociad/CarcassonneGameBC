import pygame
import logging

from ui.scene import Scene
from gameState import GameState
from utils.settingsManager import settings_manager

logger = logging.getLogger(__name__)

class GameScene(Scene):
    def __init__(self, screen, switchSceneCallback, gameSession, clock, network):
        super().__init__(screen, switchSceneCallback)
        self.session = gameSession
        self.clock = clock
        self.network = network

        # Renderer properties moved from renderer.py
        self.scrollSpeed = 10
        self.font = pygame.font.Font(None, 36)

        # Calculate initial offset to center the game board (accounting for sidebar)
        tileSize = settings_manager.get("TILE_SIZE", 96)
        gridSize = settings_manager.get("GRID_SIZE", 20)
        windowWidth = settings_manager.get("WINDOW_WIDTH", 1920)
        windowHeight = settings_manager.get("WINDOW_HEIGHT", 1080)
        sidebarWidth = settings_manager.get("SIDEBAR_WIDTH", 200)
        
        # Available game area (excluding sidebar)
        gameAreaWidth = windowWidth - sidebarWidth
        
        # Center of the game board in pixels
        boardCenterX = (gridSize * tileSize) // 2
        boardCenterY = (gridSize * tileSize) // 2
        
        # Calculate offset to center board in available game area
        self.offsetX = boardCenterX - gameAreaWidth // 2
        self.offsetY = boardCenterY - windowHeight // 2

        self.keysPressed = {
            pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False,
            pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False
        }

    def getOffsetX(self):
        """
        Renderer x-axis offset getter method
        :return: Offset on the x-axis
        """
        return self.offsetX
        
    def getOffsetY(self):
        """
        Renderer y-axis offset getter method
        :return: Offset on the y-axis
        """
        return self.offsetY

    def drawBoard(self, gameBoard, placedFigures, detectedStructures, isFirstRound, isGameOver, players):
        """
        Draws the game board, including grid lines and placed cards.
        """
        self.screen.fill((0, 128, 0))  # Green background for the board
        
        if isGameOver:
            winner = max(players, key=lambda p: p.getScore())
            message = f"{winner.getName()} wins with {winner.getScore()} points!"
            gameOverFont = pygame.font.Font(None, 72)
            textSurface = gameOverFont.render(message, True, (255, 255, 255))
            window_width = settings_manager.get("WINDOW_WIDTH", 1920)
            window_height = settings_manager.get("WINDOW_HEIGHT", 1080)
            textRect = textSurface.get_rect(center=(window_width // 2, window_height // 2))
            self.screen.blit(textSurface, textRect)
            return  # Skip rest of rendering
                
        if settings_manager.get("DEBUG", True):
            tile_size = settings_manager.get("TILE_SIZE", 96)
            # Draw grid lines
            for x in range(0, (gameBoard.getGridSize() + 1) * tile_size, tile_size):
                pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.getGridSize() * tile_size - self.offsetY))
            for y in range(0, (gameBoard.getGridSize() + 1) * tile_size, tile_size):
                pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.getGridSize() * tile_size - self.offsetX, y - self.offsetY))
        
        # Draw placed cards and their grid coordinates
        tile_size = settings_manager.get("TILE_SIZE", 96)
        for y in range(gameBoard.gridSize):
            for x in range(gameBoard.gridSize):
                card = gameBoard.getCard(x, y)
                if card:
                    imageToDraw = card.image
                    if hasattr(card, "rotation") and card.rotation:
                        try:
                            imageToDraw = pygame.transform.rotate(card.image, -card.rotation)
                        except Exception as e:
                            logger.error(f"Rotation failed for card: {e}")
                            imageToDraw = card.image
                    self.screen.blit(imageToDraw, (x * tile_size - self.offsetX, y * tile_size - self.offsetY))
                if settings_manager.get("DEBUG", True):
                    # Draw X, Y coordinates at the center of each grid cell
                    textSurface = self.font.render(f"{x},{y}", True, (255, 255, 255))
                    textX = x * tile_size - self.offsetX + tile_size // 3
                    textY = y * tile_size - self.offsetY + tile_size // 3
                    self.screen.blit(textSurface, (textX, textY))
                
        if settings_manager.get("DEBUG", True):            
            # Draw completed detected structures with tint only on relevant directions
            for structure in detectedStructures:
                if structure.getIsCompleted():
                    tintColor = structure.getColor()
                    
                    # Group card sides by card for drawing
                    cardEdgeMap = {}
                    for card, direction in structure.cardSides:
                        if direction is None:
                            continue  # Skip invalid directions
                        if card not in cardEdgeMap:
                            cardEdgeMap[card] = []
                        cardEdgeMap[card].append(direction)

                    for card, directions in cardEdgeMap.items():
                        cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == card]
                        if cardPosition:
                            cardX, cardY = cardPosition[0]
                            rect = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                            rect.fill((0, 0, 0, 0))  # Transparent base
                            
                            # Draw only relevant edges for this structure
                            for direction in directions:
                                if direction == "N":
                                    pygame.draw.rect(rect, tintColor, (0, 0, tile_size, tile_size // 3))
                                elif direction == "S":
                                    pygame.draw.rect(rect, tintColor, (0, 2 * tile_size // 3, tile_size, tile_size // 3))
                                elif direction == "E":
                                    pygame.draw.rect(rect, tintColor, (2 * tile_size // 3, 0, tile_size // 3, tile_size))
                                elif direction == "W":
                                    pygame.draw.rect(rect, tintColor, (0, 0, tile_size // 3, tile_size))
                                elif direction == "C":
                                    centerX = tile_size // 2
                                    centerY = tile_size // 2
                                    radius = tile_size // 6
                                    pygame.draw.circle(rect, tintColor, (centerX, centerY), radius)

                            self.screen.blit(rect, (cardX * tile_size - self.offsetX, cardY * tile_size - self.offsetY))

        # Draw placed figures (meeples) at correct positions on the card
        tile_size = settings_manager.get("TILE_SIZE", 96)
        figure_size = settings_manager.get("FIGURE_SIZE", 25)
        for figure in placedFigures:
            if figure.card:
                cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == figure.card]
                if cardPosition:
                    padding = tile_size * 0.1 # Distance from the border
                    figureOffset = figure_size / 2 # Compensate for figure size
                    baseX = cardPosition[0][0] * tile_size - self.offsetX
                    baseY = cardPosition[0][1] * tile_size - self.offsetY

                    # Use precise float values for accurate positioning
                    if figure.positionOnCard == "N":  # Top
                        figureX, figureY = baseX + tile_size / 2, baseY + padding + figureOffset
                    elif figure.positionOnCard == "S":  # Bottom
                        figureX, figureY = baseX + tile_size / 2, baseY + tile_size - padding - figureOffset
                    elif figure.positionOnCard == "E":  # Right
                        figureX, figureY = baseX + tile_size - padding - figureOffset, baseY + tile_size / 2
                    elif figure.positionOnCard == "W":  # Left
                        figureX, figureY = baseX + padding + figureOffset, baseY + tile_size / 2
                    else:  # Default to center if invalid position
                        figureX, figureY = baseX + tile_size / 2, baseY + tile_size / 2
                    
                    self.screen.blit(figure.image, (figureX - tile_size * 0.15, figureY - tile_size * 0.15))  # Adjust for better centering
                    
    def drawSidePanel(self, selectedCard, remainingCards, currentPlayer, placedFigures, detectedStructures):
        windowWidth = settings_manager.get("WINDOW_WIDTH", 1920)
        windowHeight = settings_manager.get("WINDOW_HEIGHT", 1080)
        sidebarWidth = settings_manager.get("SIDEBAR_WIDTH", 200)
        
        panelX = windowWidth - sidebarWidth
        pygame.draw.rect(self.screen, (50, 50, 50), (panelX, 0, sidebarWidth, windowHeight))

        if selectedCard:
            cardX = panelX + 45
            cardY = 50
            imageToDraw = selectedCard.getImage()
            if hasattr(selectedCard, "rotation") and selectedCard.rotation:
                try:
                    imageToDraw = pygame.transform.rotate(imageToDraw, -selectedCard.rotation)
                except Exception as e:
                    logger.error(f"Rotation failed in side panel for selected card: {e}")
                    imageToDraw = selectedCard.getImage()
            self.screen.blit(imageToDraw, (cardX, cardY))

        if currentPlayer:
            textY = 180
            spacing = 30

            # Turn ownership status
            network_mode = settings_manager.get("NETWORK_MODE", "local")
            if network_mode == "local":
                statusText = "Local mode"
                statusColor = (100, 100, 255)
            else:
                player_index = settings_manager.get("PLAYER_INDEX", 0)
                isMyTurn = currentPlayer.getIndex() == player_index
                statusText = "Your Turn" if isMyTurn else "Waiting..."
                statusColor = (0, 255, 0) if isMyTurn else (200, 0, 0)

            statusSurface = self.font.render(statusText, True, statusColor)
            self.screen.blit(statusSurface, (panelX + 20, textY))

            # Player name
            nameSurface = self.font.render(f"{currentPlayer.getName()}", True, (255, 255, 255))
            self.screen.blit(nameSurface, (panelX + 20, textY + spacing))

            # Score
            scoreSurface = self.font.render(f"Score: {currentPlayer.getScore()}", True, (255, 255, 255))
            self.screen.blit(scoreSurface, (panelX + 20, textY + 2 * spacing))

            # Cards remaining
            cardsSurface = self.font.render(f"Cards: {remainingCards}", True, (255, 255, 255))
            self.screen.blit(cardsSurface, (panelX + 20, textY + 3 * spacing))

            # Meeple images
            figure_size = settings_manager.get("FIGURE_SIZE", 25)
            figures = currentPlayer.getFigures()
            for i, figure in enumerate(figures):
                figX = panelX + 20 + (i % 4) * (figure_size + 5)
                figY = textY + 4 * spacing + (i // 4) * (figure_size + 5)
                self.screen.blit(figure.image, (figX, figY))

            if settings_manager.get("DEBUG", True):
                # Structure count
                structureSurface = self.font.render(f"Structures: {len(detectedStructures)}", True, (255, 255, 255))
                self.screen.blit(structureSurface, (panelX + 20, textY + 6 * spacing))

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
            network_mode = settings_manager.get("NETWORK_MODE", "local")
            if network_mode in ("host", "client"):
                currentPlayer = self.session.getCurrentPlayer()
                player_index = settings_manager.get("PLAYER_INDEX", 0)
                if not currentPlayer or currentPlayer.getIndex() != player_index or self.session.getGameOver():
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
        tile_size = settings_manager.get("TILE_SIZE", 96)
        gridX, gridY = (x + self.getOffsetX()) // tile_size, (y + self.getOffsetY()) // tile_size

        logger.debug(f"Registered {event.button}")

        if event.button == 1:
            direction = self.detectClickDirection(x, y, gridX, gridY)
            logger.debug(f"self.session.playTurn triggered for {gridX},{gridY}")
            self.session.playTurn(gridX, gridY, direction)

        if event.button == 3 and self.session.getCurrentCard():
            logger.debug("currentCard.rotate triggered")
            self.session.getCurrentCard().rotate()
        
    def handleKeyHold(self):
        if self.keysPressed.get(pygame.K_w) or self.keysPressed.get(pygame.K_UP):
            self.scroll("up")
        if self.keysPressed.get(pygame.K_s) or self.keysPressed.get(pygame.K_DOWN):
            self.scroll("down")
        if self.keysPressed.get(pygame.K_a) or self.keysPressed.get(pygame.K_LEFT):
            self.scroll("left")
        if self.keysPressed.get(pygame.K_d) or self.keysPressed.get(pygame.K_RIGHT):
            self.scroll("right")
            
    def detectClickDirection(self, mouseX, mouseY, gridX, gridY):
        tile_size = settings_manager.get("TILE_SIZE", 96)
        tileScreenX = gridX * tile_size - self.getOffsetX()
        tileScreenY = gridY * tile_size - self.getOffsetY()

        relativeX = mouseX - tileScreenX
        relativeY = mouseY - tileScreenY

        card = self.session.getGameBoard().getCard(gridX, gridY)
        if not card:
            return None

        logger.debug(f"Retrieved card {card} at {gridX};{gridY}")

        supportsCenter = card.getTerrains().get("C") is not None

        thirdSize = tile_size // 3
        twoThirdSize = 2 * tile_size // 3

        if thirdSize < relativeX < twoThirdSize and thirdSize < relativeY < twoThirdSize:
            if supportsCenter:
                return "C"

        distances = {
            "N": relativeY,
            "S": tile_size - relativeY,
            "W": relativeX,
            "E": tile_size - relativeX
        }

        return min(distances, key=distances.get)
    
    def update(self):
        fps = settings_manager.get("FPS", 60)
        if self.session.getGameOver():
            self.clock.tick(fps)
            return

        currentPlayer = self.session.getCurrentPlayer()

        if self.session.getIsFirstRound() or not currentPlayer.getIsAI():
            self.clock.tick(fps)
            return

        # AI turn
        currentPlayer.playTurn(self.session)
        self.clock.tick(fps)
        
    def draw(self):
        self.drawBoard(
            self.session.getGameBoard(),
            self.session.getPlacedFigures(),
            self.session.getStructures(),
            self.session.getIsFirstRound(),
            self.session.getGameOver(),
            self.session.getPlayers()
        )
        self.drawSidePanel(
            self.session.getCurrentCard(),
            len(self.session.getCardsDeck()) + 1,
            self.session.getCurrentPlayer(),
            self.session.getPlacedFigures(),
            self.session.getStructures()
        )
        pygame.display.flip()