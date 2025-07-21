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

        # Sidebar scrolling
        self.sidebarScrollOffset = 0
        self.sidebarScrollSpeed = 20

        # Calculate initial offset to center the game board (accounting for sidebar)
        tileSize = settings_manager.get("TILE_SIZE")  # Odstraněn fallback
        gridSize = settings_manager.get("GRID_SIZE")  # Odstraněn fallback
        windowWidth = settings_manager.get("WINDOW_WIDTH")  # Odstraněn fallback
        windowHeight = settings_manager.get("WINDOW_HEIGHT")  # Odstraněn fallback
        sidebarWidth = settings_manager.get("SIDEBAR_WIDTH")  # Odstraněn fallback
        
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
            window_width = settings_manager.get("WINDOW_WIDTH")  # Odstraněn fallback
            window_height = settings_manager.get("WINDOW_HEIGHT")  # Odstraněn fallback
            textRect = textSurface.get_rect(center=(window_width // 2, window_height // 2))
            self.screen.blit(textSurface, textRect)
            return  # Skip rest of rendering
                
        if settings_manager.get("DEBUG"):  # Odstraněn fallback
            tile_size = settings_manager.get("TILE_SIZE")  # Odstraněn fallback
            # Draw grid lines
            for x in range(0, (gameBoard.getGridSize() + 1) * tile_size, tile_size):
                pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.getGridSize() * tile_size - self.offsetY))
            for y in range(0, (gameBoard.getGridSize() + 1) * tile_size, tile_size):
                pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.getGridSize() * tile_size - self.offsetX, y - self.offsetY))
        
        # Draw placed cards and their grid coordinates
        tile_size = settings_manager.get("TILE_SIZE")  # Odstraněn fallback
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
                if settings_manager.get("DEBUG"):  # Odstraněn fallback
                    # Draw X, Y coordinates at the center of each grid cell
                    textSurface = self.font.render(f"{x},{y}", True, (255, 255, 255))
                    textX = x * tile_size - self.offsetX + tile_size // 3
                    textY = y * tile_size - self.offsetY + tile_size // 3
                    self.screen.blit(textSurface, (textX, textY))
                
        if settings_manager.get("DEBUG"):  # Odstraněn fallback
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
        tile_size = settings_manager.get("TILE_SIZE")  # Odstraněn fallback
        figure_size = settings_manager.get("FIGURE_SIZE")  # Odstraněn fallback
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
        windowWidth = settings_manager.get("WINDOW_WIDTH")
        windowHeight = settings_manager.get("WINDOW_HEIGHT")
        sidebarWidth = settings_manager.get("SIDEBAR_WIDTH")
        
        panelX = windowWidth - sidebarWidth
        sidebarCenterX = panelX + sidebarWidth // 2
        
        pygame.draw.rect(self.screen, (50, 50, 50), (panelX, 0, sidebarWidth, windowHeight))

        currentY = 50
        sectionSpacing = 25
        fixedContentHeight = 0

        # FIXED CONTENT - Current card (neposunuje se)
        if selectedCard:
            imageToDraw = selectedCard.getImage()
            if hasattr(selectedCard, "rotation") and selectedCard.rotation:
                try:
                    imageToDraw = pygame.transform.rotate(imageToDraw, -selectedCard.rotation)
                except Exception as e:
                    logger.error(f"Rotation failed in side panel for selected card: {e}")
                    imageToDraw = selectedCard.getImage()
            
            cardRect = imageToDraw.get_rect()
            cardRect.centerx = sidebarCenterX
            cardRect.y = currentY
            self.screen.blit(imageToDraw, cardRect)
            currentY += cardRect.height + sectionSpacing
            fixedContentHeight = currentY

        # SCROLLABLE CONTENT - zbytek obsahu
        scrollableStartY = currentY
        scrollableHeight = windowHeight - fixedContentHeight
        clipSurface = pygame.Surface((sidebarWidth, scrollableHeight))
        clipSurface.fill((50, 50, 50))
        
        # Draw scrollable content on clip surface
        clipY = 0

        # Turn status
        networkMode = settings_manager.get("NETWORK_MODE")
        if networkMode == "local":
            statusText = "Local mode"
            statusColor = (100, 100, 255)
        else:
            playerIndex = settings_manager.get("PLAYER_INDEX")
            isMyTurn = currentPlayer.getIndex() == playerIndex
            statusText = "Your Turn" if isMyTurn else "Waiting..."
            statusColor = (0, 255, 0) if isMyTurn else (200, 0, 0)

        statusSurface = self.font.render(statusText, True, statusColor)
        statusRect = statusSurface.get_rect()
        statusRect.centerx = sidebarWidth // 2
        statusRect.y = clipY
        clipSurface.blit(statusSurface, statusRect)
        clipY += statusRect.height + sectionSpacing

        # Cards remaining
        cardsSurface = self.font.render(f"Cards: {remainingCards}", True, (255, 255, 255))
        cardsRect = cardsSurface.get_rect()
        cardsRect.centerx = sidebarWidth // 2
        cardsRect.y = clipY
        clipSurface.blit(cardsSurface, cardsRect)
        clipY += cardsRect.height + sectionSpacing

        # Get all players from game session
        allPlayers = self.session.getPlayers()
        
        # Display each player's info
        for i, player in enumerate(allPlayers):
            # Get player's color and convert string to RGB
            try:
                colorString = player.getColor() if hasattr(player, 'getColor') else player.color
                
                # Convert color name to RGB tuple
                colorMap = {
                    "red": (255, 100, 100),
                    "blue": (100, 100, 255),
                    "green": (100, 255, 100),
                    "yellow": (255, 255, 100),
                    "pink": (255, 100, 255),
                    "black": (200, 200, 200),  # Light gray for visibility
                }
                playerColor = colorMap.get(colorString, (255, 255, 255))
                
            except Exception as e:
                logger.error(f"Failed to get player color: {e}")
                playerColor = (255, 255, 255)

            # Highlight current player with brighter color
            if player == currentPlayer:
                playerColor = tuple(min(255, int(c) + 50) for c in playerColor)

            # Player name in their color
            nameSurface = self.font.render(f"{player.getName()}", True, playerColor)
            nameRect = nameSurface.get_rect()
            nameRect.centerx = sidebarWidth // 2
            nameRect.y = clipY
            clipSurface.blit(nameSurface, nameRect)
            clipY += nameRect.height + 5

            # Player score
            scoreSurface = self.font.render(f"Score: {player.getScore()}", True, (200, 200, 200))
            scoreRect = scoreSurface.get_rect()
            scoreRect.centerx = sidebarWidth // 2
            scoreRect.y = clipY
            clipSurface.blit(scoreSurface, scoreRect)
            clipY += scoreRect.height + 10

            # Player's meeples
            figures = player.getFigures()
            if figures:
                figureSize = settings_manager.get("FIGURE_SIZE")
                padding = 10
                availableWidth = sidebarWidth - (2 * padding)
                figuresPerRow = max(1, availableWidth // (figureSize + 5))
                figuresPerRow = min(figuresPerRow, len(figures))
                
                totalRows = (len(figures) + figuresPerRow - 1) // figuresPerRow
                actualGridWidth = figuresPerRow * figureSize + (figuresPerRow - 1) * 5
                
                gridStartX = (sidebarWidth - actualGridWidth) // 2
                gridStartY = clipY
                
                for j, figure in enumerate(figures):
                    row = j // figuresPerRow
                    col = j % figuresPerRow
                    
                    figX = gridStartX + col * (figureSize + 5)
                    figY = gridStartY + row * (figureSize + 5)
                    clipSurface.blit(figure.image, (figX, figY))
                
                # Update clipY based on meeple grid height
                gridHeight = totalRows * figureSize + (totalRows - 1) * 5
                clipY += gridHeight

            # Add consistent spacing between players (except after last player)
            if i < len(allPlayers) - 1:
                clipY += sectionSpacing

        # Debug info at the very end (after all players)
        if settings_manager.get("DEBUG"):
            clipY += sectionSpacing  # Same spacing as other sections
            structureSurface = self.font.render(f"Structures: {len(detectedStructures)}", True, (255, 255, 255))
            structureRect = structureSurface.get_rect()
            structureRect.centerx = sidebarWidth // 2
            structureRect.y = clipY
            clipSurface.blit(structureSurface, structureRect)
            clipY += structureRect.height

        # Limit scroll based on content height
        maxScroll = max(0, clipY - scrollableHeight)
        self.sidebarScrollOffset = min(self.sidebarScrollOffset, maxScroll)

        # Blit the scrollable content to main screen
        self.screen.blit(clipSurface, (panelX, scrollableStartY))

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

            # Sidebar scrolling - pouze pokud je myš nad sidebarem
            if event.type == pygame.MOUSEWHEEL:
                mouseX, mouseY = pygame.mouse.get_pos()
                windowWidth = settings_manager.get("WINDOW_WIDTH")
                sidebarWidth = settings_manager.get("SIDEBAR_WIDTH")
                panelX = windowWidth - sidebarWidth
                
                if mouseX >= panelX:  # Myš je nad sidebarem
                    self.sidebarScrollOffset += event.y * self.sidebarScrollSpeed
                    self.sidebarScrollOffset = max(0, self.sidebarScrollOffset)  # Nemůže být záporný
                    continue  # Nepokračuj s dalším zpracováním

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.keysPressed[event.key] = (event.type == pygame.KEYDOWN)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)

            # Block game actions if it's not this player's turn in network mode
            allowAction = True
            network_mode = settings_manager.get("NETWORK_MODE")  # Odstraněn fallback
            if network_mode in ("host", "client"):
                currentPlayer = self.session.getCurrentPlayer()
                player_index = settings_manager.get("PLAYER_INDEX")  # Odstraněn fallback
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
        tile_size = settings_manager.get("TILE_SIZE")  # Odstraněn fallback
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
        tile_size = settings_manager.get("TILE_SIZE")  # Odstraněn fallback
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
        fps = settings_manager.get("FPS")  # Odstraněn fallback
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