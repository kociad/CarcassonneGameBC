import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from gameState import GameState

import settings

class MainMenuScene(Scene):
    def __init__(self, screen, switchSceneCallback, getGameSession):
        super().__init__(screen, switchSceneCallback)

        self.font = pygame.font.Font(None, 100)
        self.buttonFont = pygame.font.Font(None, 48)

        self.getGameSession = getGameSession

        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

        centerX = screen.get_width() // 2 - 100
        centerY = screen.get_height() // 2

        # Continue
        self.continueButton = Button(
            "Continue",
            (centerX, centerY - 80, 200, 60),
            self.buttonFont,
            disabled=(self.getGameSession() is None)
        )

        # Start game
        self.startButton = Button(
            "New Game",
            (centerX, centerY, 200, 60),
            self.buttonFont
        )

        # How to play
        self.howToPlayButton = Button(
            "How to play",
            (centerX, centerY + 80, 200, 60),
            self.buttonFont
        )

        # Settings
        self.settingsButton = Button(
            "Settings",
            (centerX, centerY + 160, 200, 60),
            self.buttonFont
        )

        # Quit
        self.quitButton = Button(
            "Quit",
            (centerX, centerY + 240, 200, 60),
            self.buttonFont
        )

    def handleEvents(self, events):
        self.applyScroll(events)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.continueButton.isClicked(event.pos, yOffset=self.scrollOffset) and not self.continueButton.disabled:
                    self.switchScene(GameState.GAME)
                elif self.startButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.PREPARE)
                elif self.settingsButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.SETTINGS)
                elif self.quitButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    pygame.quit()
                    exit()
                elif self.howToPlayButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    webbrowser.open("https://wikicarpedia.com/car/Base_game")

    def draw(self):
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset

        # Title
        titleText = self.font.render("Carcassonne", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3 - 60 + offsetY))
        self.screen.blit(titleText, titleRect)

        # Update continue button state
        self.continueButton.disabled = self.getGameSession() is None

        # Draw buttons with scroll offset
        self.continueButton.draw(self.screen, yOffset=offsetY)
        self.startButton.draw(self.screen, yOffset=offsetY)
        self.settingsButton.draw(self.screen, yOffset=offsetY)
        self.quitButton.draw(self.screen, yOffset=offsetY)
        self.howToPlayButton.draw(self.screen, yOffset=offsetY)

        # Update maxScroll if buttons extend past screen
        self.maxScroll = max(
            self.screen.get_height(),
            self.quitButton.rect.bottom + 100
        )

        pygame.display.flip()
