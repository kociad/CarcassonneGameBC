import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from gameState import GameState
from utils.settingsReader import readSetting

import settings

class MainMenuScene(Scene):
    def __init__(self, screen, switchSceneCallback, getGameSession):
        super().__init__(screen, switchSceneCallback)

        self.font = pygame.font.Font(None, 100)
        self.buttonFont = pygame.font.Font(None, 48)
        
        self.getGameSession = getGameSession

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
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.continueButton.isClicked(event.pos) and not self.continueButton.disabled:
                    self.switchScene(GameState.GAME)
                elif self.startButton.isClicked(event.pos):
                    self.switchScene(GameState.PREPARE)
                elif self.settingsButton.isClicked(event.pos):
                    self.switchScene(GameState.SETTINGS)
                elif self.quitButton.isClicked(event.pos):
                    pygame.quit()
                    exit()
                elif self.howToPlayButton.isClicked(event.pos):
                    webbrowser.open("https://wikicarpedia.com/car/Base_game")  # Replace with your actual URL

    def draw(self):
        # Background
        self.screen.fill((30, 30, 30))

        # Title
        titleText = self.font.render("Carcassonne", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3 - 60))
        self.screen.blit(titleText, titleRect)

        # Update continue button state
        self.continueButton.disabled = self.getGameSession() is None

        # Buttons
        self.continueButton.draw(self.screen)
        self.startButton.draw(self.screen)
        self.settingsButton.draw(self.screen)
        self.quitButton.draw(self.screen)
        self.howToPlayButton.draw(self.screen)

        pygame.display.flip()

