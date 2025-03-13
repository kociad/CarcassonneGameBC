import pygame
from settings import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

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
    
    def drawBoard(self, gameBoard):
        """
        Draws the game board, including grid lines and placed cards.
        """
        self.screen.fill((0, 128, 0))  # Green background for the board
        
        # Draw grid lines
        for x in range(0, (gameBoard.gridSize + 1) * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (x - self.offsetX, 0 - self.offsetY), (x - self.offsetX, gameBoard.gridSize * TILE_SIZE - self.offsetY))
        for y in range(0, (gameBoard.gridSize + 1) * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (0 - self.offsetX, y - self.offsetY), (gameBoard.gridSize * TILE_SIZE - self.offsetX, y - self.offsetY))
        
        # Draw placed cards
        for y in range(gameBoard.gridSize):
            for x in range(gameBoard.gridSize):
                card = gameBoard.getCard(x, y)
                if card:
                    self.screen.blit(card.image, (x * TILE_SIZE - self.offsetX, y * TILE_SIZE - self.offsetY))
    
    def drawSidePanel(self, selectedCard, remainingCards, currentPlayer):
        """
        Draws a side panel where the currently selected card will be displayed.
        :param selectedCard: The card currently selected by the player.
        """
        panelX = WINDOW_WIDTH - 200  # Panel width of 200 pixels
        pygame.draw.rect(self.screen, (50, 50, 50), (panelX, 0, 200, WINDOW_HEIGHT))  # Dark grey background
        
        if selectedCard:
            cardX = panelX + 45
            cardY = 50
            self.screen.blit(selectedCard.image, (cardX, cardY))
            
        if currentPlayer:
            textY = 180
            spacing = 30
            
            # Display player's name
            nameSurface = self.font.render(f"{currentPlayer.name}'s Turn", True, (255, 255, 255))
            self.screen.blit(nameSurface, (panelX + 20, textY))
            
            # Display player's score
            scoreSurface = self.font.render(f"Score: {currentPlayer.score}", True, (255, 255, 255))
            self.screen.blit(scoreSurface, (panelX + 20, textY + spacing))
            
            # Display number of meeples remaining
            meeplesSurface = self.font.render(f"Meeples: {len(currentPlayer.figures)}", True, (255, 255, 255))
            self.screen.blit(meeplesSurface, (panelX + 20, textY + 2 * spacing))
            
        # Display number of remaining cards in the deck
        textY = 270
        nameSurface = self.font.render(f"Cards: {remainingCards}", True, (255, 255, 255))
        self.screen.blit(nameSurface, (panelX + 20, textY))
            
    
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
