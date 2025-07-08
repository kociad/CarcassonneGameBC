import pygame
from ui.scene import Scene
from ui.components.button import Button
from gameState import GameState
from utils.settingsReader import readSetting

import settings

class MainMenuScene(Scene):
    def __init__(self, screen, switchSceneCallback, startGameCallback):
        super().__init__(screen, switchSceneCallback)
        self.startGameCallback = startGameCallback

        self.font = pygame.font.Font(None, 100)
        self.buttonFont = pygame.font.Font(None, 48)

        # Start game
        self.startButton = Button(
            "New game",
            (screen.get_width() // 2 - 100, screen.get_height() // 2, 200, 60),
            self.buttonFont
        )

        # Settings
        self.settingsButton = Button(
            "Settings",
            (screen.get_width() // 2 - 100, screen.get_height() // 2 + 80, 200, 60),
            self.buttonFont
        )

        # Quit
        self.quitButton = Button(
            "Quit",
            (screen.get_width() // 2 - 100, screen.get_height() // 2 + 160, 200, 60),
            self.buttonFont
        )

    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.startButton.isClicked(event.pos):
                    self.startGameCallback(readSetting("PLAYERS"))
                elif self.settingsButton.isClicked(event.pos):
                    self.switchScene(GameState.SETTINGS)
                elif self.quitButton.isClicked(event.pos):
                    pygame.quit()
                    exit()

    def draw(self):
        # Background
        self.screen.fill((30, 30, 30))

        # Title
        titleText = self.font.render("Carcassonne", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))
        self.screen.blit(titleText, titleRect)

        # Buttons
        self.startButton.draw(self.screen)
        self.settingsButton.draw(self.screen)
        self.quitButton.draw(self.screen)

        pygame.display.flip()
