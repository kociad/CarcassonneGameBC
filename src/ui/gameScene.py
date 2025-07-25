import pygame
import logging
import typing

from ui.scene import Scene
from gameState import GameState
from utils.settingsManager import settingsManager
from ui.components.toast import Toast, ToastManager

logger = logging.getLogger(__name__)

class GameScene(Scene):
    """
    Main scene for rendering and managing the Carcassonne game board, sidebar, and user interactions.
    Handles drawing, event processing, notifications, and game state updates.
    """
    def __init__(self, screen: pygame.Surface, switchSceneCallback: typing.Callable, gameSession: typing.Any, clock: typing.Any, network: typing.Any, gameLog: typing.Any) -> None:
        """Initialize the GameScene with references to the main screen, callbacks, game session, clock, network, and game log"""
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

        self._candidatePositionsCache = []
        self._candidatePositionsCard = None
        self._candidatePositionsRotation = None

        self._lastAITurnTime = 0

    def updateCandidatePositionsCache(self):
        """Update the candidate positions cache"""
        currentCard = self.session.getCurrentCard()
        if currentCard is None:
            self._candidatePositionsCache = []
            self._candidatePositionsCard = None
            self._candidatePositionsRotation = None
            return
        self._candidatePositionsCard = currentCard
        self._candidatePositionsRotation = getattr(currentCard, 'rotation', 0)
        candidatePositions = self.session.getCandidatePositions()
        gameBoard = self.session.getGameBoard()
        self._candidatePositionsCache = [
            (x, y) for (x, y) in candidatePositions
            if gameBoard.validateCardPlacement(currentCard, x, y)
        ]

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
        """Get the current x-axis offset for board rendering"""
        return self.offsetX
        
    def getOffsetY(self) -> int:
        """Get the current y-axis offset for board rendering"""
        return self.offsetY

    def drawBoard(self, gameBoard: typing.Any, placedFigures: list, detectedStructures: list, isFirstRound: bool, isGameOver: bool, players: list) -> None:
        """
        Draw the game board, grid, placed cards, figures, and completed structures.
        :param gameBoard: The game board object.
        :param placedFigures: List of placed figure objects.
        :param detectedStructures: List of detected structure objects.
        :param isFirstRound: Whether it is the first round.
        :param isGameOver: Whether the game is over.
        :param players: List of player objects.
        """
        self.screen.fill((0, 128, 0))
        
        if isGameOver:
            sortedPlayers = sorted(players, key=lambda p: p.getScore(), reverse=True)
            winner = sortedPlayers[0]
            windowWidth = settingsManager.get("WINDOW_WIDTH")
            windowHeight = settingsManager.get("WINDOW_HEIGHT")

            gameOverFont = pygame.font.Font(None, 72)
            playerFont = pygame.font.Font(None, 48)
            infoFont = pygame.font.Font(None, 36)

            winnerMessage = f"{winner.getName()} wins with {winner.getScore()} points!"
            winnerSurface = gameOverFont.render(winnerMessage, True, (255, 255, 255))
            winnerRect = winnerSurface.get_rect(center=(windowWidth // 2, windowHeight // 2 - 100))
            self.screen.blit(winnerSurface, winnerRect)

            startY = windowHeight // 2 - 20
            for i, player in enumerate(sortedPlayers):
                colorMap = {
                    "red": (255, 100, 100),
                    "blue": (100, 100, 255),
                    "green": (100, 255, 100),
                    "yellow": (255, 255, 100),
                    "pink": (255, 100, 255),
                    "black": (200, 200, 200),
                }
                playerColor = colorMap.get(player.getColor(), (255, 255, 255))
                playerMsg = f"{player.getName()}: {player.getScore()} points"
                playerSurface = playerFont.render(playerMsg, True, playerColor)
                playerRect = playerSurface.get_rect(center=(windowWidth // 2, startY + i * 55))
                self.screen.blit(playerSurface, playerRect)

            escMsg = "Press ESC to return to menu"
            escSurface = infoFont.render(escMsg, True, (200, 200, 200))
            escRect = escSurface.get_rect(center=(windowWidth // 2, startY + len(sortedPlayers) * 60 + 20))
            self.screen.blit(escSurface, escRect)
            return
                
        if settingsManager.get("DEBUG"):
            tileSize = settingsManager.get("TILE_SIZE")
            for x in range(0, (gameBoard.getGridSize() + 1) * tileSize, tileSize):
                pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.getGridSize() * tileSize - self.offsetY))
            for y in range(0, (gameBoard.getGridSize() + 1) * tileSize, tileSize):
                pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.getGridSize() * tileSize - self.offsetX, y - self.offsetY))
        
        tileSize = settingsManager.get("TILE_SIZE")
        if not isGameOver:
            currentCard = self.session.getCurrentCard()
            currentRotation = getattr(currentCard, 'rotation', 0) if currentCard else None
            if (
                currentCard is not None and
                (self._candidatePositionsCard is not currentCard or self._candidatePositionsRotation != currentRotation)
            ):
                self.updateCandidatePositionsCache()
            for (x, y) in self._candidatePositionsCache:
                highlightColor = (255, 255, 0, 100)
                highlightSurface = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
                highlightSurface.fill(highlightColor)
                self.screen.blit(
                    highlightSurface,
                    (x * tileSize - self.offsetX, y * tileSize - self.offsetY)
                )
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
                    self.screen.blit(imageToDraw, (x * tileSize - self.offsetX, y * tileSize - self.offsetY))
                if settingsManager.get("DEBUG"):
                    textSurface = self.font.render(f"{x},{y}", True, (255, 255, 255))
                    textX = x * tileSize - self.offsetX + tileSize // 3
                    textY = y * tileSize - self.offsetY + tileSize // 3
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
                            rect = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
                            rect.fill((0, 0, 0, 0))
                            
                            for direction in directions:
                                if direction == "N":
                                    pygame.draw.rect(rect, tintColor, (0, 0, tileSize, tileSize // 3))
                                elif direction == "S":
                                    pygame.draw.rect(rect, tintColor, (0, 2 * tileSize // 3, tileSize, tileSize // 3))
                                elif direction == "E":
                                    pygame.draw.rect(rect, tintColor, (2 * tileSize // 3, 0, tileSize // 3, tileSize))
                                elif direction == "W":
                                    pygame.draw.rect(rect, tintColor, (0, 0, tileSize // 3, tileSize))
                                elif direction == "C":
                                    centerX = tileSize // 2
                                    centerY = tileSize // 2
                                    radius = tileSize // 6
                                    pygame.draw.circle(rect, tintColor, (centerX, centerY), radius)

                            self.screen.blit(rect, (cardX * tileSize - self.offsetX, cardY * tileSize - self.offsetY))

        tileSize = settingsManager.get("TILE_SIZE")
        figureSize = settingsManager.get("FIGURE_SIZE")
        for figure in placedFigures:
            if figure.card:
                cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == figure.card]
                if cardPosition:
                    padding = tileSize * 0.1
                    figureOffset = figureSize / 2
                    baseX = cardPosition[0][0] * tileSize - self.offsetX
                    baseY = cardPosition[0][1] * tileSize - self.offsetY

                    if figure.positionOnCard == "N":
                        figureX, figureY = baseX + tileSize / 2, baseY + padding + figureOffset
                    elif figure.positionOnCard == "S":
                        figureX, figureY = baseX + tileSize / 2, baseY + tileSize - padding - figureOffset
                    elif figure.positionOnCard == "E":
                        figureX, figureY = baseX + tileSize - padding - figureOffset, baseY + tileSize / 2
                    elif figure.positionOnCard == "W":
                        figureX, figureY = baseX + padding + figureOffset, baseY + tileSize / 2
                    else:
                        figureX, figureY = baseX + tileSize / 2, baseY + tileSize / 2
                    
                    self.screen.blit(figure.image, (figureX - tileSize * 0.15, figureY - tileSize * 0.15))
                    
    def drawSidePanel(self, selectedCard: typing.Any, remainingCards: int, currentPlayer: typing.Any, placedFigures: list, detectedStructures: list) -> None:
        """
        Draw the sidebar panel with current card, player info, and game status.
        :param selectedCard: The currently drawn card.
        :param remainingCards: Number of cards left in the deck.
        :param currentPlayer: The player whose turn it is.
        :param placedFigures: List of placed figures.
        :param detectedStructures: List of detected structures.
        """
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
                    pygame.draw.rect(self.screen, (60, 80, 120), playerBgRect)  # Blue background
                    pygame.draw.rect(self.screen, (100, 150, 255), playerBgRect, 2)  # Blue border
            
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
        """Scroll the view of the board in the specified direction"""
        if direction == "up":
            self.offsetY -= self.scrollSpeed
        elif direction == "down":
            self.offsetY += self.scrollSpeed
        elif direction == "left":
            self.offsetX -= self.scrollSpeed
        elif direction == "right":
            self.offsetX += self.scrollSpeed

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        """Handle all pygame events for the game scene, including input, quitting, and game actions"""
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
            networkMode = settingsManager.get("NETWORK_MODE")
            if networkMode in ("host", "client"):
                currentPlayer = self.session.getCurrentPlayer()
                playerIndex = settingsManager.get("PLAYER_INDEX")
                if not currentPlayer or currentPlayer.getIndex() != playerIndex or self.session.getGameOver():
                    allowAction = False

            if allowAction:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handleMouseClick(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.session.skipCurrentAction()
                        
        self.handleKeyHold()

    def handleMouseClick(self, event: pygame.event.Event) -> None:
        """Handle mouse click events for board interaction"""
        x, y = event.pos
        tileSize = settingsManager.get("TILE_SIZE")
        gridX, gridY = (x + self.getOffsetX()) // tileSize, (y + self.getOffsetY()) // tileSize

        logger.debug(f"Registered {event.button}")

        if event.button == 1:
            direction = self.detectClickDirection(x, y, gridX, gridY)
            self.session.playTurn(gridX, gridY, direction)
        if event.button == 3 and self.session.getCurrentCard():
            self.session.getCurrentCard().rotate()
            self.updateCandidatePositionsCache()
        
    def handleKeyHold(self) -> None:
        """Handle continuous key presses for board scrolling"""
        if self.keysPressed.get(pygame.K_w) or self.keysPressed.get(pygame.K_UP):
            self.scroll("up")
        if self.keysPressed.get(pygame.K_s) or self.keysPressed.get(pygame.K_DOWN):
            self.scroll("down")
        if self.keysPressed.get(pygame.K_a) or self.keysPressed.get(pygame.K_LEFT):
            self.scroll("left")
        if self.keysPressed.get(pygame.K_d) or self.keysPressed.get(pygame.K_RIGHT):
            self.scroll("right")
            
    def detectClickDirection(self, mouseX: int, mouseY: int, gridX: int, gridY: int) -> typing.Optional[str]:
        """Detect which direction (N, S, E, W, C) was clicked on a card"""
        tileSize = settingsManager.get("TILE_SIZE")
        tileScreenX = gridX * tileSize - self.getOffsetX()
        tileScreenY = gridY * tileSize - self.getOffsetY()

        relativeX = mouseX - tileScreenX
        relativeY = mouseY - tileScreenY

        card = self.session.getGameBoard().getCard(gridX, gridY)
        if not card:
            return None

        logger.debug(f"Retrieved card {card} at {gridX};{gridY}")

        supportsCenter = card.getTerrains().get("C") is not None

        thirdSize = tileSize // 3
        twoThirdSize = 2 * tileSize // 3

        if thirdSize < relativeX < twoThirdSize and thirdSize < relativeY < twoThirdSize:
            if supportsCenter:
                return "C"

        distances = {
            "N": relativeY,
            "S": tileSize - relativeY,
            "W": relativeX,
            "E": tileSize - relativeX
        }

        return min(distances, key=distances.get)
        
    def showNotification(self, notificationType: str, message: str) -> None:
        """Show a notification toast message in the UI"""
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
        """Update the game state, including AI turns and frame timing"""
        fps = settingsManager.get("FPS")
        if self.session.getGameOver():
            self.clock.tick(fps)
            return

        currentPlayer = self.session.getCurrentPlayer()

        if self.session.getIsFirstRound() or not currentPlayer.getIsAI():
            self.clock.tick(fps)
            return

        aiDelay = settingsManager.get("AI_TURN_DELAY")
        now = pygame.time.get_ticks()
        if now - self._lastAITurnTime < aiDelay * 1000:
            self.clock.tick(fps)
            return
        currentPlayer.playTurn(self.session)
        self._lastAITurnTime = pygame.time.get_ticks()
        self.clock.tick(fps)
        
    def draw(self) -> None:
        """Draw the entire game scene, including the board, sidebar, game log, and notifications"""
        currentCard = self.session.getCurrentCard()
        currentRotation = getattr(currentCard, 'rotation', 0) if currentCard else None
        if (
            currentCard is not None and
            (self._candidatePositionsCard is not currentCard or self._candidatePositionsRotation != currentRotation)
        ):
            self.updateCandidatePositionsCache()
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