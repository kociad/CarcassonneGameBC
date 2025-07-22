import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from gameState import GameState

class HelpScene(Scene):
    def __init__(self, screen, switchSceneCallback):
        super().__init__(screen, switchSceneCallback)
        
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.textFont = pygame.font.Font(None, 36)
        self.controlsFont = pygame.font.Font(None, 32)
        
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30
        
        # Layout
        centerX = screen.get_width() // 2 - 100
        currentY = 60
        
        self.titleY = currentY
        currentY += 80
        
        # Controls section start
        self.controlsStartY = currentY
        
        # Controls text
        self.controls = [
            "GAME CONTROLS:",
            "",
            "WASD or ARROW KEYS - Move around the game board",
            "LMB (Left Mouse Button) - Place card",
            "RMB (Right Mouse Button) - Rotate card",
            "SPACEBAR - Discard card (only if unplaceable) or skip meeple",
            "ESC - Return to main menu",
            "",
            "MOUSE WHEEL - Scroll in menus and sidebar",
            "",
            "GAME PHASES:",
            "",
            "Phase 1: Place the drawn card on the board",
            "Phase 2: Optionally place a meeple on the placed card",
            "",
            "RULES:",
            "",
            "• Cards must be placed adjacent to existing cards",
            "• Terrain types must match on adjacent edges", 
            "• You can only discard if no valid placement exists",
            "• Meeples can only be placed on unoccupied structures",
            "• Completed structures score points immediately"
        ]
        
        # Calculate content height
        lineHeight = 35
        self.controlsHeight = len(self.controls) * lineHeight
        currentY += self.controlsHeight + 40
        
        # Buttons
        self.rulesButton = Button(
            "Wiki",
            (centerX, currentY, 200, 60),
            self.buttonFont
        )
        currentY += 80
        
        self.backButton = Button(
            "Back",
            (centerX, currentY, 200, 60),
            self.buttonFont
        )
        
        # Set max scroll based on content
        self.maxScroll = max(screen.get_height(), currentY + 100)

    def handleEvents(self, events):
        self.applyScroll(events)
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.MENU)
                elif self.rulesButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    webbrowser.open("https://wikicarpedia.com/car/Base_game")

    def draw(self):
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        
        # Title
        titleText = self.font.render("How to Play", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY + offsetY))
        self.screen.blit(titleText, titleRect)
        
        # Controls text
        currentY = self.controlsStartY + offsetY
        lineHeight = 35
        
        for line in self.controls:
            if line == "":
                currentY += lineHeight // 2  # Half spacing for empty lines
                continue
                
            # Different styling for headers
            if line.endswith(":") and not line.startswith(" "):
                # Header style
                color = (255, 215, 0)  # Gold color for headers
                font = self.textFont
            elif line.startswith("•"):
                # Bullet point style
                color = (200, 200, 255)  # Light blue for bullet points
                font = self.controlsFont
            else:
                # Regular control text
                color = (255, 255, 255)
                font = self.controlsFont
            
            textSurface = font.render(line, True, color)
            
            # Center align headers, left align others
            if line.endswith(":") and not line.startswith(" "):
                textRect = textSurface.get_rect(center=(self.screen.get_width() // 2, currentY))
            else:
                textRect = textSurface.get_rect(left=50, centery=currentY)
            
            # Only draw if visible on screen
            if textRect.bottom > 0 and textRect.top < self.screen.get_height():
                self.screen.blit(textSurface, textRect)
            
            currentY += lineHeight
        
        # Buttons
        self.rulesButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        
        pygame.display.flip()