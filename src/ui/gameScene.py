import pygame
import logging
import typing
import settings

from ui.scene import Scene
from gameState import GameState
from utils.settingsManager import settingsManager
from ui.components.toast import Toast, ToastManager
from ui.components.button import Button
from ui.components.progressBar import ProgressBar

logger = logging.getLogger(__name__)

class GameScene(Scene):
    def __init__(self, screen: pygame.Surface, switchSceneCallback: typing.Callable, gameSession: typing.Any, clock: typing.Any, network: typing.Any, gameLog: typing.Any) -> None:
        super().__init__(screen, switchSceneCallback)
        self.session = gameSession
        self.clock = clock
        self.network = network
        self.gameLog = gameLog

        self.scrollSpeed = 10
        self.font = pygame.font.Font(None, 36)

        self.toastManager = ToastManager(maxToasts=5)

        self.sidebarScrollOffset = 0
        self.sidebarScrollSpeed = 30

        tileSize = settingsManager.get("TILE_SIZE")
        gridSize = settingsManager.get("GRID_SIZE")
        windowWidth = settingsManager.get("WINDOW_WIDTH")
        windowHeight = settingsManager.get("WINDOW_HEIGHT")
        sidebarWidth = settingsManager.get("SIDEBAR_WIDTH")
        
        gameAreaWidth = windowWidth - sidebarWidth
        
        boardCenterX = (gridSize * tileSize) // 2
        boardCenterY = (gridSize * tileSize) // 2
        
        self.offsetX = boardCenterX - gameAreaWidth // 2
        self.offsetY = boardCenterY - windowHeight // 2

        self.keysPressed = {
            pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False,
            pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False
        }

        self.validPlacements = set()
        self.lastCardState = (None, None)
        
        self.lastAITurnTime = 0
        self.playerActionTime = 0
        self.aiTurnStartTime = None

        barWidth = sidebarWidth - 40
        barHeight = 20
        barX = windowWidth - sidebarWidth + 20
        barY = 0
        self.aiThinkingProgressBar = ProgressBar(
            rect=(barX, barY, barWidth, barHeight),
            font=self.font,
            minValue=0.0,
            maxValue=1.0,
            value=0.0,
            backgroundColor=(80, 80, 80),
            progressColor=(100, 255, 100),
            borderColor=(150, 150, 150),
            showText=True,
            textColor=(255, 255, 255)
        )


    def applySidebarScroll(self, events: list[pygame.event.Event]) -> None:
        """Handle sidebar scrolling events"""
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                mouseX, mouseY = pygame.mouse.get_pos()
                windowWidth = settingsManager.get("WINDOW_WIDTH")
                sidebarWidth = settingsManager.get("SIDEBAR_WIDTH")
                panelX = windowWidth - sidebarWidth
                
                if mouseX >= panelX:
                    self.sidebarScrollOffset -= event.y * self.sidebarScrollSpeed
                    self.sidebarScrollOffset = max(0, self.sidebarScrollOffset)

    def getOffsetX(self) -> int:
        """
        Renderer x-axis offset getter method
        :return: Offset on the x-axis
        """
        return self.offsetX
        
    def getOffsetY(self) -> int:
        """
        Renderer y-axis offset getter method
        :return: Offset on the y-axis
        """
        return self.offsetY

    def updateValidPlacements(self):
        """Update the set of valid placements for the current card and board state."""
        currentCard = self.session.getCurrentCard()
        if not currentCard:
            self.validPlacements = set()
            self.lastCardState = (None, None)
            return
        
        card_id = id(currentCard)
        rotation = getattr(currentCard, 'rotation', 0)
        currentState = (card_id, rotation)
        
        if currentState == self.lastCardState:
            return
        
        self.lastCardState = currentState
        
        validPlacements = self.session.getValidPlacements(currentCard)
        self.validPlacements = {(x, y) for x, y, cardRotation in validPlacements if cardRotation == rotation}

    def drawBoard(self, gameBoard: typing.Any, placedFigures: list, detectedStructures: list, isFirstRound: bool, isGameOver: bool, players: list) -> None:
        """
        Draws the game board, including grid lines and placed cards.
        """
        self.updateValidPlacements()
        self.screen.fill((25, 25, 25))

        if settingsManager.get("SHOW_VALID_PLACEMENTS", True):
            tileSize = settingsManager.get("TILE_SIZE")
            highlightColor = (255, 255, 0, 100)
            for (x, y) in self.validPlacements:
                rect = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
                rect.fill(highlightColor)
                self.screen.blit(rect, (x * tileSize - self.offsetX, y * tileSize - self.offsetY))
        
        if isGameOver:
            winner = max(players, key=lambda p: p.getScore())
            message = f"{winner.getName()} wins with {winner.getScore()} points!"
            gameOverFont = pygame.font.Font(None, 72)
            window_width = settingsManager.get("WINDOW_WIDTH")
            window_height = settingsManager.get("WINDOW_HEIGHT")
            winnerY = window_height // 3 - 40
            textSurface = gameOverFont.render(message, True, (255, 255, 255))
            textRect = textSurface.get_rect(center=(window_width // 2, winnerY))
            self.screen.blit(textSurface, textRect)

            tableFont = pygame.font.Font(None, 48)
            rowFont = pygame.font.Font(None, 42)
            sortedPlayers = sorted(players, key=lambda p: (-p.getScore(), p.getName()))
            numRows = len(sortedPlayers) + 1  # header + players
            rowHeight = 55
            tableWidth = 600
            tableHeight = numRows * rowHeight + 20
            tableX = window_width // 2 - tableWidth // 2
            tableY = textRect.bottom + 30
            col1X = window_width // 2 - 150
            col2X = window_width // 2 + 150

            pygame.draw.rect(self.screen, (40, 40, 40), (tableX, tableY, tableWidth, tableHeight))
            headerY = tableY + rowHeight // 2
            headerPlayer = tableFont.render("Player", True, (255, 255, 255))
            headerScore = tableFont.render("Score", True, (255, 255, 255))
            self.screen.blit(headerPlayer, headerPlayer.get_rect(center=(col1X, headerY)))
            self.screen.blit(headerScore, headerScore.get_rect(center=(col2X, headerY)))
            pygame.draw.line(self.screen, (100, 100, 100), (tableX + 10, tableY + rowHeight), (tableX + tableWidth - 10, tableY + rowHeight), 2)

            for i, player in enumerate(sortedPlayers):
                rowY = tableY + rowHeight * (i + 1) + rowHeight // 2
                nameSurface = rowFont.render(player.getName(), True, (220, 220, 220))
                scoreSurface = rowFont.render(str(player.getScore()), True, (220, 220, 220))
                self.screen.blit(nameSurface, nameSurface.get_rect(center=(col1X, rowY)))
                self.screen.blit(scoreSurface, scoreSurface.get_rect(center=(col2X, rowY)))
                if i < len(sortedPlayers) - 1:
                    pygame.draw.line(self.screen, (70, 70, 70), (tableX + 10, tableY + rowHeight * (i + 2)), (tableX + tableWidth - 10, tableY + rowHeight * (i + 2)), 1)
            return
                
        if settingsManager.get("DEBUG"):
            tile_size = settingsManager.get("TILE_SIZE")
            for x in range(0, (gameBoard.getGridSize() + 1) * tile_size, tile_size):
                pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.getGridSize() * tile_size - self.offsetY))
            for y in range(0, (gameBoard.getGridSize() + 1) * tile_size, tile_size):
                pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.getGridSize() * tile_size - self.offsetX, y - self.offsetY))
        
        tile_size = settingsManager.get("TILE_SIZE")
        center_x, center_y = gameBoard.getCenterPosition()
        
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
                    
                    if x == center_x and y == center_y:
                        try:
                            compassImage = pygame.image.load(settings.ICONS_PATH + "compass.png")
                            compassSize = tile_size // 4
                            compassImage = pygame.transform.scale(compassImage, (compassSize, compassSize))
                            compassX = x * tile_size - self.offsetX + tile_size - compassSize - 5
                            compassY = y * tile_size - self.offsetY + 5
                            self.screen.blit(compassImage, (compassX, compassY))
                        except Exception as e:
                            logger.error(f"Failed to load compass icon: {e}")
                        
                if settingsManager.get("DEBUG"):
                    textSurface = self.font.render(f"{x},{y}", True, (255, 255, 255))
                    textX = x * tile_size - self.offsetX + tile_size // 3
                    textY = y * tile_size - self.offsetY + tile_size // 3
                    self.screen.blit(textSurface, (textX, textY))
                
        if settingsManager.get("DEBUG"):
            for structure in detectedStructures:
                if structure.getIsCompleted():
                    tintColor = structure.getColor()
                    
                    cardEdgeMap = {}
                    for card, direction in structure.cardSides:
                        if direction is None:
                            continue
                        if card not in cardEdgeMap:
                            cardEdgeMap[card] = []
                        cardEdgeMap[card].append(direction)

                    for card, directions in cardEdgeMap.items():
                        cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == card]
                        if cardPosition:
                            cardX, cardY = cardPosition[0]
                            rect = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                            rect.fill((0, 0, 0, 0))
                            
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

        tile_size = settingsManager.get("TILE_SIZE")
        figure_size = settingsManager.get("FIGURE_SIZE")
        for figure in placedFigures:
            if figure.card:
                cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == figure.card]
                if cardPosition:
                    padding = tile_size * 0.1
                    figureOffset = figure_size / 2
                    baseX = cardPosition[0][0] * tile_size - self.offsetX
                    baseY = cardPosition[0][1] * tile_size - self.offsetY

                    if figure.positionOnCard == "N":
                        figureX, figureY = baseX + tile_size / 2, baseY + padding + figureOffset
                    elif figure.positionOnCard == "S":
                        figureX, figureY = baseX + tile_size / 2, baseY + tile_size - padding - figureOffset
                    elif figure.positionOnCard == "E":
                        figureX, figureY = baseX + tile_size - padding - figureOffset, baseY + tile_size / 2
                    elif figure.positionOnCard == "W":
                        figureX, figureY = baseX + padding + figureOffset, baseY + tile_size / 2
                    else:
                        figureX, figureY = baseX + tile_size / 2, baseY + tile_size / 2
                    
                    self.screen.blit(figure.image, (figureX - tile_size * 0.15, figureY - tile_size * 0.15))
                    
    def drawSidePanel(self, selectedCard: typing.Any, remainingCards: int, currentPlayer: typing.Any, placedFigures: list, detectedStructures: list) -> None:
        windowWidth = settingsManager.get("WINDOW_WIDTH")
        windowHeight = settingsManager.get("WINDOW_HEIGHT")
        sidebarWidth = settingsManager.get("SIDEBAR_WIDTH")
        
        panelX = windowWidth - sidebarWidth
        sidebarCenterX = panelX + sidebarWidth // 2
        
        pygame.draw.rect(self.screen, (50, 50, 50), (panelX, 0, sidebarWidth, windowHeight))
        currentY = 50
        sectionSpacing = 25
        scrollableContentStartY = currentY

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
            scrollableContentStartY = currentY

        offsetY = self.sidebarScrollOffset

        if settingsManager.get("DEBUG", False):
            networkMode = settingsManager.get("NETWORK_MODE")
            if networkMode == "local":
                statusText = "Local mode"
                statusColor = (100, 100, 255)
            else:
                playerIndex = settingsManager.get("PLAYER_INDEX")
                isMyTurn = currentPlayer.getIndex() == playerIndex
                statusText = "Your Turn" if isMyTurn else "Waiting..."
                statusColor = (0, 255, 0) if isMyTurn else (200, 0, 0)
            
            statusSurface = self.font.render(statusText, True, statusColor)
            statusRect = statusSurface.get_rect()
            statusRect.centerx = sidebarCenterX
            statusRect.y = currentY - offsetY
            if statusRect.bottom > scrollableContentStartY and statusRect.top < windowHeight:
                self.screen.blit(statusSurface, statusRect)
            currentY += statusRect.height + sectionSpacing

        cardsSurface = self.font.render(f"Cards left: {remainingCards}", True, (255, 255, 255))
        cardsRect = cardsSurface.get_rect()
        cardsRect.centerx = sidebarCenterX
        cardsRect.y = currentY - offsetY
        if cardsRect.bottom > scrollableContentStartY and cardsRect.top < windowHeight:
            self.screen.blit(cardsSurface, cardsRect)
        currentY += cardsRect.height + sectionSpacing

        allPlayers = self.session.getPlayers()
        
        for i, player in enumerate(allPlayers):
            playerStartY = currentY
            isCurrentPlayer = (player == currentPlayer)
            
            playerSectionHeight = 80
            figures = player.getFigures()
            if figures:
                figureSize = settingsManager.get("FIGURE_SIZE")
                figuresPerRow = max(1, (sidebarWidth - 20) // (figureSize + 5))
                figuresPerRow = min(figuresPerRow, len(figures))
                totalRows = (len(figures) + figuresPerRow - 1) // figuresPerRow
                playerSectionHeight += totalRows * figureSize + (totalRows - 1) * 5
            
            if isCurrentPlayer:
                playerBgRect = pygame.Rect(panelX + 5, currentY - offsetY - 10, sidebarWidth - 10, playerSectionHeight)
                if playerBgRect.bottom > scrollableContentStartY and playerBgRect.top < windowHeight:
                    pygame.draw.rect(self.screen, (60, 80, 120), playerBgRect)
                    pygame.draw.rect(self.screen, (100, 150, 255), playerBgRect, 2)
            
            try:
                colorString = player.getColor()
                
                colorMap = {
                    "red": (255, 100, 100),
                    "blue": (100, 100, 255),
                    "green": (100, 255, 100),
                    "yellow": (255, 255, 100),
                    "pink": (255, 100, 255),
                    "black": (200, 200, 200),
                }
                
                playerColor = colorMap.get(colorString, (255, 255, 255))
                
            except Exception as e:
                logger.error(f"Failed to get player color: {e}")
                playerColor = (255, 255, 255)
            
            nameText = player.getName()
            nameSurface = self.font.render(nameText, True, playerColor)
            nameRect = nameSurface.get_rect()
            nameRect.centerx = sidebarCenterX
            nameRect.y = currentY - offsetY
            if nameRect.bottom > scrollableContentStartY and nameRect.top < windowHeight:
                self.screen.blit(nameSurface, nameRect)
            currentY += nameRect.height + 5

            scoreColor = (200, 200, 200)
            scoreSurface = self.font.render(f"Score: {player.getScore()}", True, scoreColor)
            scoreRect = scoreSurface.get_rect()
            scoreRect.centerx = sidebarCenterX
            scoreRect.y = currentY - offsetY
            if scoreRect.bottom > scrollableContentStartY and scoreRect.top < windowHeight:
                self.screen.blit(scoreSurface, scoreRect)
            currentY += scoreRect.height + 10

            if figures:
                
                figureSize = settingsManager.get("FIGURE_SIZE")
                padding = 10
                availableWidth = sidebarWidth - (2 * padding)
                figuresPerRow = max(1, availableWidth // (figureSize + 5))
                figuresPerRow = min(figuresPerRow, len(figures))
                
                totalRows = (len(figures) + figuresPerRow - 1) // figuresPerRow
                actualGridWidth = figuresPerRow * figureSize + (figuresPerRow - 1) * 5
                
                gridStartX = sidebarCenterX - actualGridWidth // 2
                gridStartY = currentY - offsetY
                
                if gridStartY + totalRows * (figureSize + 5) > scrollableContentStartY and gridStartY < windowHeight:
                    for j, figure in enumerate(figures):
                        row = j // figuresPerRow
                        col = j % figuresPerRow
                        
                        figX = gridStartX + col * (figureSize + 5)
                        figY = gridStartY + row * (figureSize + 5)
                        
                        if figY + figureSize > scrollableContentStartY and figY < windowHeight:
                            self.screen.blit(figure.image, (figX, figY))
                
                gridHeight = totalRows * figureSize + (totalRows - 1) * 5
                currentY += gridHeight

            if i < len(allPlayers) - 1:
                currentY += sectionSpacing

        if (currentPlayer.getIsAI() and hasattr(currentPlayer, 'isThinking') and 
            currentPlayer.isThinking() and settingsManager.get("DEBUG", False)):
            currentY += sectionSpacing
            
            thinkingText = f"AI is thinking..."
            thinkingSurface = self.font.render(thinkingText, True, (255, 255, 100))
            thinkingRect = thinkingSurface.get_rect()
            thinkingRect.centerx = sidebarCenterX
            thinkingRect.y = currentY - offsetY
            if thinkingRect.bottom > scrollableContentStartY and thinkingRect.top < windowHeight:
                self.screen.blit(thinkingSurface, thinkingRect)
            currentY += thinkingRect.height + 10
            
            progress = currentPlayer.getThinkingProgress()
            self.aiThinkingProgressBar.setProgress(progress)
            self.aiThinkingProgressBar.rect.y = currentY - offsetY
            
            if self.aiThinkingProgressBar.rect.bottom > scrollableContentStartY and self.aiThinkingProgressBar.rect.top < windowHeight:
                self.aiThinkingProgressBar.draw(self.screen, yOffset=0)
            
            currentY += self.aiThinkingProgressBar.rect.height + 10

        if settingsManager.get("DEBUG"):
            currentY += sectionSpacing
            structureSurface = self.font.render(f"Structures: {len(detectedStructures)}", True, (255, 255, 255))
            structureRect = structureSurface.get_rect()
            structureRect.centerx = sidebarCenterX
            structureRect.y = currentY - offsetY
            if structureRect.bottom > scrollableContentStartY and structureRect.top < windowHeight:
                self.screen.blit(structureSurface, structureRect)
            currentY += structureRect.height

        maxScroll = max(0, currentY - windowHeight + 50)
        self.sidebarScrollOffset = min(self.sidebarScrollOffset, maxScroll)

    def scroll(self, direction: str) -> None:
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

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEWHEEL and hasattr(self, 'gameLog') and self.gameLog.visible:
                self.gameLog.handleScroll(event.y)
                return
        
        if not (hasattr(self, 'gameLog') and self.gameLog.visible):
            self.applySidebarScroll(events)
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.keysPressed[event.key] = (event.type == pygame.KEYDOWN)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.gameLog.toggleVisibility()
                elif event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)

            allowAction = True
            network_mode = settingsManager.get("NETWORK_MODE")
            if network_mode in ("host", "client"):
                currentPlayer = self.session.getCurrentPlayer()
                player_index = settingsManager.get("PLAYER_INDEX")
                if not currentPlayer or currentPlayer.getIndex() != player_index or self.session.getGameOver():
                    allowAction = False

            if allowAction:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX, mouseY = event.pos
                    windowWidth = settingsManager.get("WINDOW_WIDTH")
                    sidebarWidth = settingsManager.get("SIDEBAR_WIDTH")
                    panelX = windowWidth - sidebarWidth
                    
                    if mouseX < panelX:
                        self.handleMouseClick(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.session.skipCurrentAction()
                        
        self.handleKeyHold()

    def handleMouseClick(self, event: pygame.event.Event) -> None:
        x, y = event.pos
        tile_size = settingsManager.get("TILE_SIZE")
        gridX, gridY = (x + self.getOffsetX()) // tile_size, (y + self.getOffsetY()) // tile_size

        logger.debug(f"Registered {event.button}")

        if event.button == 1:
            direction = self.detectClickDirection(x, y, gridX, gridY)
            self.session.playTurn(gridX, gridY, direction)
            self.updateValidPlacements()
            self.playerActionTime = pygame.time.get_ticks() / 1000.0
            self.aiTurnStartTime = None

        if event.button == 3 and self.session.getCurrentCard():
            self.session.getCurrentCard().rotate()
            self.updateValidPlacements()
        
    def handleKeyHold(self) -> None:
        if self.keysPressed.get(pygame.K_w) or self.keysPressed.get(pygame.K_UP):
            self.scroll("up")
        if self.keysPressed.get(pygame.K_s) or self.keysPressed.get(pygame.K_DOWN):
            self.scroll("down")
        if self.keysPressed.get(pygame.K_a) or self.keysPressed.get(pygame.K_LEFT):
            self.scroll("left")
        if self.keysPressed.get(pygame.K_d) or self.keysPressed.get(pygame.K_RIGHT):
            self.scroll("right")
            
    def detectClickDirection(self, mouseX: int, mouseY: int, gridX: int, gridY: int) -> typing.Optional[str]:
        tile_size = settingsManager.get("TILE_SIZE")
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
        
    def showNotification(self, notificationType: str, message: str) -> None:
        """
        Show notification toast - called via callback from game session
        """
        toastTypeMap = {
            "error": "error",
            "warning": "warning", 
            "info": "info",
            "success": "success"
        }
        
        toastType = toastTypeMap.get(notificationType, "info")
        toast = Toast(message, type=toastType, duration=3)
        
        self.toastManager.addToast(toast)
    
    def update(self) -> None:
        fps = settingsManager.get("FPS")
        if self.session.getGameOver():
            self.clock.tick(fps)
            return

        currentPlayer = self.session.getCurrentPlayer()

        if self.session.getIsFirstRound() or not currentPlayer.getIsAI():
            self.clock.tick(fps)
            return

        if self.session.getCurrentCard() is None:
            self.clock.tick(fps)
            return

        if hasattr(currentPlayer, 'isThinking') and currentPlayer.isThinking():
            currentPlayer.playTurn(self.session)
            self.clock.tick(fps)
            return

        if hasattr(currentPlayer, 'playTurn'):
            logger.debug(f"Starting AI turn for {currentPlayer.getName()}")
            currentPlayer.playTurn(self.session)
        else:
            logger.warning(f"Player {currentPlayer.getName()} is marked as AI but doesn't have playTurn method")
        
        self.clock.tick(fps)
        
    def draw(self) -> None:
        self.updateValidPlacements()
        self.drawBoard(
            self.session.getGameBoard(),
            self.session.getPlacedFigures(),
            self.session.getStructures(),
            self.session.getIsFirstRound(),
            self.session.getGameOver(),
            self.session.getPlayers()
        )
        
        if not self.session.getGameOver() and not self.session.getIsFirstRound():
            self.drawSidePanel(
                self.session.getCurrentCard(),
                len(self.session.getCardsDeck()),
                self.session.getCurrentPlayer(),
                self.session.getPlacedFigures(),
                self.session.getStructures()
            )
        
        self.gameLog.draw(self.screen)
        
        self.toastManager.draw(self.screen)
        
        pygame.display.flip()