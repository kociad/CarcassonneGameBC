import pygame
import random
import logging

from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player

import settings

logger = logging.getLogger(__name__)

class Renderer:
    """
    Handles rendering of the game board, UI elements, and placed cards.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.offsetX = 0
        self.offsetY = 0
        self.scrollSpeed = 10
        self.font = pygame.font.Font(None, 36)
        
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
        
        # Define structure tints
        """
        structureColors = {
            "City": (200, 100, 100, 100),  # Light red tint
            "Road": (100, 100, 200, 100),  # Light blue tint
            "Monastery": (100, 200, 100, 100)  # Light green tint
        }
        """
        
        """
        if isFirstRound:
            startFont = pygame.font.Font(None, 72)
            message = "Press 'Enter' to start game"
            textSurface = startFont.render(message, True, (255, 255, 255))
            textRect = textSurface.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2))
            self.screen.blit(textSurface, textRect)
            return  # Skip board drawing entirely until game starts
        """
            
        if isGameOver:
            winner = max(players, key=lambda p: p.getScore())
            message = f"{winner.getName()} wins with {winner.getScore()} points!"
            gameOverFont = pygame.font.Font(None, 72)
            textSurface = gameOverFont.render(message, True, (255, 255, 255))
            textRect = textSurface.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2))
            self.screen.blit(textSurface, textRect)
            return  # Skip rest of rendering
                
        if settings.DEBUG:
            # Draw grid lines
            for x in range(0, (gameBoard.getGridSize() + 1) * settings.TILE_SIZE, settings.TILE_SIZE):
                pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.getGridSize() * settings.TILE_SIZE - self.offsetY))
            for y in range(0, (gameBoard.getGridSize() + 1) * settings.TILE_SIZE, settings.TILE_SIZE):
                pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.getGridSize() * settings.TILE_SIZE - self.offsetX, y - self.offsetY))
        
        # Draw placed cards and their grid coordinates
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
                    self.screen.blit(imageToDraw, (x * settings.TILE_SIZE - self.offsetX, y * settings.TILE_SIZE - self.offsetY))
                if settings.DEBUG:
                    # Draw X, Y coordinates at the center of each grid cell
                    textSurface = self.font.render(f"{x},{y}", True, (255, 255, 255))
                    textX = x * settings.TILE_SIZE - self.offsetX + settings.TILE_SIZE // 3
                    textY = y * settings.TILE_SIZE - self.offsetY + settings.TILE_SIZE // 3
                    self.screen.blit(textSurface, (textX, textY))
                
        if settings.DEBUG:            
            # Draw completed detected structures with tint only on relevant directions
            for structure in detectedStructures:
                #structure.checkCompletion()
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
                            rect = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                            rect.fill((0, 0, 0, 0))  # Transparent base
                            
                            # Draw only relevant edges for this structure
                            for direction in directions:
                                if direction == "N":
                                    pygame.draw.rect(rect, tintColor, (0, 0, settings.TILE_SIZE, settings.TILE_SIZE // 3))
                                elif direction == "S":
                                    pygame.draw.rect(rect, tintColor, (0, 2 * settings.TILE_SIZE // 3, settings.TILE_SIZE, settings.TILE_SIZE // 3))
                                elif direction == "E":
                                    pygame.draw.rect(rect, tintColor, (2 * settings.TILE_SIZE // 3, 0, settings.TILE_SIZE // 3, settings.TILE_SIZE))
                                elif direction == "W":
                                    pygame.draw.rect(rect, tintColor, (0, 0, settings.TILE_SIZE // 3, settings.TILE_SIZE))
                                elif direction == "C":
                                    centerX = settings.TILE_SIZE // 2
                                    centerY = settings.TILE_SIZE // 2
                                    radius = settings.TILE_SIZE // 6
                                    pygame.draw.circle(rect, tintColor, (centerX, centerY), radius)

                            self.screen.blit(rect, (cardX * settings.TILE_SIZE - self.offsetX, cardY * settings.TILE_SIZE - self.offsetY))

        # Draw placed figures (meeples) at correct positions on the card
        for figure in placedFigures:
            if figure.card:
                cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == figure.card]
                if cardPosition:
                    padding = settings.TILE_SIZE * 0.1 # Distance from the border
                    figureOffset = settings.FIGURE_SIZE / 2 # Compensate for figure size
                    baseX = cardPosition[0][0] * settings.TILE_SIZE - self.offsetX # + padding + settings.FIGURE_SIZE / 2
                    baseY = cardPosition[0][1] * settings.TILE_SIZE - self.offsetY # + padding + settings.FIGURE_SIZE / 2

                    # Use precise float values for accurate positioning
                    if figure.positionOnCard == "N":  # Top
                        figureX, figureY = baseX + settings.TILE_SIZE / 2, baseY + padding + figureOffset
                    elif figure.positionOnCard == "S":  # Bottom
                        figureX, figureY = baseX + settings.TILE_SIZE / 2, baseY + settings.TILE_SIZE - padding - figureOffset
                    elif figure.positionOnCard == "E":  # Right
                        figureX, figureY = baseX + settings.TILE_SIZE - padding - figureOffset, baseY + settings.TILE_SIZE / 2
                    elif figure.positionOnCard == "W":  # Left
                        figureX, figureY = baseX + padding + figureOffset, baseY + settings.TILE_SIZE / 2
                    else:  # Default to center if invalid position
                        figureX, figureY = baseX + settings.TILE_SIZE / 2, baseY + settings.TILE_SIZE / 2
                    
                    self.screen.blit(figure.image, (figureX - settings.TILE_SIZE * 0.15, figureY - settings.TILE_SIZE * 0.15))  # Adjust for better centering
                    
    def drawSidePanel(self, selectedCard, remainingCards, currentPlayer, placedFigures, detectedStructures):
        panelX = settings.WINDOW_WIDTH - 200  # Panel width of 200 pixels
        pygame.draw.rect(self.screen, (50, 50, 50), (panelX, 0, 200, settings.WINDOW_HEIGHT))  # Dark grey background

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
            if settings.NETWORK_MODE == "local":
                statusText = "Local mode"
                statusColor = (100, 100, 255)
            else:
                isMyTurn = currentPlayer.getIndex() == settings.PLAYER_INDEX
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
            figures = currentPlayer.getFigures()
            for i, figure in enumerate(figures):
                figX = panelX + 20 + (i % 4) * (settings.FIGURE_SIZE + 5)
                figY = textY + 4 * spacing + (i // 4) * (settings.FIGURE_SIZE + 5)
                self.screen.blit(figure.image, (figX, figY))

            if settings.DEBUG:
                # Structure count
                structureSurface = self.font.render(f"Structures: {len(detectedStructures)}", True, (255, 255, 255))
                self.screen.blit(structureSurface, (panelX + 20, textY + 6 * spacing))
                
    def updateDisplay(self):
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
            self.offsetY -= self.scrollSpeed
        elif direction == "down":
            self.offsetY += self.scrollSpeed
        elif direction == "left":
            self.offsetX -= self.scrollSpeed
        elif direction == "right":
            self.offsetX += self.scrollSpeed
            
    def drawMainMenu(self):
        """
        Draws the main menu screen with a title and start button.
        """
        self.screen.fill((30, 30, 30))  # Dark background

        # Title text
        titleFont = pygame.font.Font(None, 100)
        titleText = titleFont.render("Carcassonne", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 3))
        self.screen.blit(titleText, titleRect)

        # Button
        buttonFont = pygame.font.Font(None, 48)
        self.buttonText = buttonFont.render("Start Game", True, (0, 0, 0))
        self.buttonRect = pygame.Rect(settings.WINDOW_WIDTH // 2 - 100, settings.WINDOW_HEIGHT // 2, 200, 60)

        # Draw button background
        pygame.draw.rect(self.screen, (200, 200, 200), self.buttonRect)
        textRect = self.buttonText.get_rect(center=self.buttonRect.center)
        self.screen.blit(self.buttonText, textRect)