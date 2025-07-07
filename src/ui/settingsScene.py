import pygame
from ui.scene import Scene
from gameState import GameState
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast
from utils.settingsWriter import updateResolution

class SettingsScene(Scene):
    def __init__(self, screen, switchSceneCallback):
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        self.toastQueue = []
        self.activeToast = None

        self.playerNameField = InputField(
            rect=(screen.get_width() // 2 - 100, screen.get_height() // 2, 200, 40),
            font=self.inputFont,
            placeholder="Player Name"
        )

        def onResolutionSelect(value):
            width, height = map(int, value.split("x"))
            updateResolution(width, height)
            self.toastQueue.append(Toast("Restart the game to apply resolution changes", type="warning"))
            
        self.resolutionDropdown = Dropdown(
            rect=(screen.get_width() // 2 - 100, screen.get_height() // 2 + 60, 200, 40),
            font=self.dropdownFont,
            options=[
                "800x600", "1024x768", "1280x720", "1366x768",
                "1600x900", "1920x1080", "2560x1440", "3840x2160"
            ],
            onSelect=onResolutionSelect
        )

        self.applyButton = Button(
            "Apply",
            (screen.get_width() // 2 - 100, screen.get_height() // 2 + 120, 200, 60),
            self.buttonFont
        )

        self.backButton = Button(
            "Back",
            (screen.get_width() // 2 - 100, screen.get_height() // 2 + 200, 200, 60),
            self.buttonFont
        )

    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if self.resolutionDropdown.handleEvent(event):
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos):
                    self.switchScene(GameState.MENU)
                elif self.applyButton.isClicked(event.pos):
                    selected_resolution = self.resolutionDropdown.getSelected()
                    if selected_resolution:
                        width, height = map(int, selected_resolution.split("x"))
                        updateResolution(width, height)
                    self.toastQueue.append(Toast("Settings successfully saved", type="success"))

            self.playerNameField.handleEvent(event)

    def update(self):
        pass

    def draw(self):
        self.screen.fill((20, 20, 20))

        text = self.font.render("Settings", True, (255, 255, 255))
        textRect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))
        self.screen.blit(text, textRect)

        self.playerNameField.draw(self.screen)
        self.backButton.draw(self.screen)
        self.applyButton.draw(self.screen)
        self.resolutionDropdown.draw(self.screen)

        if not self.activeToast and self.toastQueue:
            self.activeToast = self.toastQueue.pop(0)
            self.activeToast.start()

        if self.activeToast:
            self.activeToast.draw(self.screen)
            if self.activeToast.isExpired():
                self.activeToast = None
                
        pygame.display.flip()
