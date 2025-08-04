import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from gameState import GameState
import typing


class HelpScene(Scene):
    """Scene displaying help and controls for the game."""

    def __init__(self, screen: pygame.Surface,
                 switchSceneCallback: typing.Callable) -> None:
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.textFont = pygame.font.Font(None, 36)
        self.controlsFont = pygame.font.Font(None, 32)
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30
        centerX = screen.get_width() // 2 - 100
        currentY = 60
        self.titleY = currentY
        currentY += 80
        self.controlsStartY = currentY
        self.controls = [
            "GAME CONTROLS:", "",
            "WASD or ARROW KEYS - Move around the game board",
            "LMB (Left Mouse Button) - Place card",
            "RMB (Right Mouse Button) - Rotate card",
            "SPACEBAR - Discard card (only if unplaceable) or skip meeple",
            "ESC - Return to main menu", "TAB - Toggle the game log", "",
            "MOUSE WHEEL - Scroll in menus and sidebar", "", "GAME PHASES:",
            "", "Phase 1: Place the drawn card on the board",
            "Phase 2: Optionally place a meeple on the placed card", "",
            "RULES:", "", "Cards must be placed adjacent to existing cards",
            "Terrain types must match on adjacent edges",
            "You can only discard if no valid placement exists",
            "Meeples can only be placed on unoccupied structures",
            "Completed structures score points immediately"
        ]
        lineHeight = 30
        self.controlsHeight = len(self.controls) * lineHeight
        currentY += self.controlsHeight + 40
        self.rulesButton = Button((centerX, currentY, 200, 60), "Wiki",
                                  self.buttonFont)
        currentY += 80
        self.backButton = Button((centerX, currentY, 200, 60), "Back",
                                 self.buttonFont)
        self.maxScroll = max(screen.get_height(), currentY + 100)

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the help scene."""
        self._applyScroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton._isClicked(event.pos,
                                             yOffset=self.scrollOffset):
                    self.switchScene(GameState.MENU)
                elif self.rulesButton._isClicked(event.pos,
                                                yOffset=self.scrollOffset):
                    webbrowser.open("https://wikicarpedia.com/car/Base_game")

    def draw(self) -> None:
        """Draw the help scene."""
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        titleText = self.font.render("How to Play", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2,
                                               self.titleY + offsetY))
        self.screen.blit(titleText, titleRect)
        currentY = self.controlsStartY + offsetY
        lineHeight = 35
        for line in self.controls:
            if line == "":
                currentY += lineHeight // 2
                continue
            if line.endswith(":") and not line.startswith(" "):
                color = (255, 215, 0)
                font = self.textFont
            elif line.startswith("2"):
                color = (200, 200, 255)
                font = self.controlsFont
            else:
                color = (255, 255, 255)
                font = self.controlsFont
            textSurface = font.render(line, True, color)
            if line.endswith(":") and not line.startswith(" "):
                textRect = textSurface.get_rect(
                    center=(self.screen.get_width() // 2, currentY))
            else:
                textRect = textSurface.get_rect(left=50, centery=currentY)
            if textRect.bottom > 0 and textRect.top < self.screen.get_height():
                self.screen.blit(textSurface, textRect)
            currentY += lineHeight
        self.rulesButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        pygame.display.flip()
