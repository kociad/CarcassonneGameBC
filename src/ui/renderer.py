import pygame
from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from settings import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, FIGURE_SIZE

class Renderer:
    """
    Handles rendering of the game board, UI elements, and placed cards.
    """
    
    def __init__(self, screen):
        """
        Initializes the renderer with a given Pygame screen and scrolling offset.
        :param screen: The Pygame display surface.
        """
        self.screen = screen
        self.offsetX = 0
        self.offsetY = 0
        self.scrollSpeed = 10  # Adjust scrolling speed as needed
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
    
    def drawBoard(self, gameBoard, placedFigures):
        """
        Draws the game board, including grid lines and placed cards.
        """
        self.screen.fill((0, 128, 0))  # Green background for the board
        
        # Draw grid lines
        for x in range(0, (gameBoard.getGridSize() + 1) * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.getGridSize() * TILE_SIZE - self.offsetY))
        for y in range(0, (gameBoard.getGridSize() + 1) * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.getGridSize() * TILE_SIZE - self.offsetX, y - self.offsetY))
        
        # Draw placed cards and their grid coordinates
        for y in range(gameBoard.gridSize):
            for x in range(gameBoard.gridSize):
                card = gameBoard.getCard(x, y)
                if card:
                    self.screen.blit(card.image, (x * TILE_SIZE - self.offsetX, y * TILE_SIZE - self.offsetY))
                # Draw X, Y coordinates at the center of each grid cell
                textSurface = self.font.render(f"{x},{y}", True, (255, 255, 255))
                textX = x * TILE_SIZE - self.offsetX + TILE_SIZE // 3
                textY = y * TILE_SIZE - self.offsetY + TILE_SIZE // 3
                self.screen.blit(textSurface, (textX, textY))
                  
        # Draw placed figures (meeples) at correct positions on the card
        for figure in placedFigures:
            if figure.card:
                cardPosition = [(x, y) for y in range(gameBoard.gridSize) for x in range(gameBoard.gridSize) if gameBoard.getCard(x, y) == figure.card]
                if cardPosition:
                    padding = TILE_SIZE * 0.1 # Distance from the border
                    figureOffset = FIGURE_SIZE / 2 # Compensate for figure size
                    baseX = cardPosition[0][0] * TILE_SIZE - self.offsetX # + padding + FIGURE_SIZE / 2
                    baseY = cardPosition[0][1] * TILE_SIZE - self.offsetY # + padding + FIGURE_SIZE / 2

                    # Use precise float values for accurate positioning
                    if figure.positionOnCard == "N":  # Top
                        figureX, figureY = baseX + TILE_SIZE / 2, baseY + padding + figureOffset
                    elif figure.positionOnCard == "S":  # Bottom
                        figureX, figureY = baseX + TILE_SIZE / 2, baseY + TILE_SIZE - padding - figureOffset
                    elif figure.positionOnCard == "E":  # Right
                        figureX, figureY = baseX + TILE_SIZE - padding - figureOffset, baseY + TILE_SIZE / 2
                    elif figure.positionOnCard == "W":  # Left
                        figureX, figureY = baseX + padding + figureOffset, baseY + TILE_SIZE / 2
                    else:  # Default to center if invalid position
                        figureX, figureY = baseX + TILE_SIZE / 2, baseY + TILE_SIZE / 2
                    
                    self.screen.blit(figure.image, (figureX - TILE_SIZE * 0.15, figureY - TILE_SIZE * 0.15))  # Adjust for better centering
    
    def drawSidePanel(self, selectedCard, remainingCards, currentPlayer, placedFigures):
        """
        Draws a side panel where the currently selected card and player info will be displayed.
        :param selectedCard: The card currently selected by the player.
        """
        panelX = WINDOW_WIDTH - 200  # Panel width of 200 pixels
        pygame.draw.rect(self.screen, (50, 50, 50), (panelX, 0, 200, WINDOW_HEIGHT))  # Dark grey background
        
        if selectedCard:
            cardX = panelX + 45
            cardY = 50
            self.screen.blit(selectedCard.getImage(), (cardX, cardY))
            
        if currentPlayer:
            textY = 180
            spacing = 30
            
            # Display player's name
            nameSurface = self.font.render(f"{currentPlayer.getName()}'s Turn", True, (255, 255, 255))
            self.screen.blit(nameSurface, (panelX + 20, textY))
            
            # Display player's score
            scoreSurface = self.font.render(f"Score: {currentPlayer.getScore()}", True, (255, 255, 255))
            self.screen.blit(scoreSurface, (panelX + 20, textY + spacing))
            
            # Display number of meeples remaining
            meeplesSurface = self.font.render(f"Meeples: {len(currentPlayer.getFigures())}", True, (255, 255, 255))
            self.screen.blit(meeplesSurface, (panelX + 20, textY + 2 * spacing))
            
        # Display number of remaining cards in the deck
        nameSurface = self.font.render(f"Cards: {remainingCards}", True, (255, 255, 255))
        self.screen.blit(nameSurface, (panelX + 20, 270))
        
        # Display number of meeples palced
        placedMeeplesSurface = self.font.render(f"Placed: {len(placedFigures)}", True, (255, 255, 255))
        self.screen.blit(placedMeeplesSurface, (panelX + 20, 300))
            
    
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
