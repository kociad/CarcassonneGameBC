import pygame
from ui.scene import Scene
from gameState import GameState
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast
from ui.components.checkbox import Checkbox
from utils.settingsWriter import updateResolution, updateFullscreen, updateDebug

import settings

class SettingsScene(Scene):
    def __init__(self, screen, switchSceneCallback):
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        self.toastQueue = []
        self.activeToast = None

        #Layout anchor
        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 80

        #Resolution settings
        currentResolution = f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}"
        resolutionOptions = [
            "800x600", "1024x768", "1280x720", "1366x768",
            "1600x900", "1920x1080", "2560x1440", "3840x2160"
        ]
        defaultIndex = resolutionOptions.index(currentResolution) if currentResolution in resolutionOptions else 0

        self.resolutionDropdown = Dropdown(
            rect=(xCenter, currentY, 200, 40),
            font=self.dropdownFont,
            options=resolutionOptions,
            defaultIndex=defaultIndex,
            onSelect=lambda value: self.toastQueue.append(Toast("Restart the game to apply resolution changes", type="warning"))
        )
        currentY += 60
        
        #Fullscreen checkbox
        self.fullscreenCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settings.FULLSCREEN,
            onToggle=lambda value: self.toastQueue.append(Toast("Restart the game to apply fullscreen changes", type="warning"))
        )
        currentY += 40
        
        #Debug mode checkbox
        self.debugCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settings.DEBUG,
            onToggle=None
        )
        currentY += 40

        
        #Apply button
        self.applyButton = Button(
            "Apply",
            (xCenter, currentY, 200, 60),
            self.buttonFont
        )
        currentY += 80

        #Back button
        self.backButton = Button(
            "Back",
            (xCenter, currentY, 200, 60),
            self.buttonFont
        )
        
    def handleEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if self.resolutionDropdown.handleEvent(event):
                continue
            self.fullscreenCheckbox.handleEvent(event)
            self.debugCheckbox.handleEvent(event)
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos):
                    self.switchScene(GameState.MENU)
                elif self.applyButton.isClicked(event.pos):
                    selected_resolution = self.resolutionDropdown.getSelected()
                    if selected_resolution:
                        width, height = map(int, selected_resolution.split("x"))
                        updateResolution(width, height)
                        
                    fullscreen = self.fullscreenCheckbox.isChecked()
                    updateFullscreen(fullscreen)
                    
                    debug_state = self.debugCheckbox.isChecked()
                    updateDebug(debug_state)
                    
                    self.toastQueue.append(Toast("Settings successfully saved", type="success"))
                    
    def update(self):
        pass
        
    def draw(self):
        self.screen.fill((20, 20, 20))

        # Title
        titleText = self.font.render("Settings", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY))
        self.screen.blit(titleText, titleRect)

        # Labels
        labelFont = self.dropdownFont
        # Resolution label
        resLabel = labelFont.render("Resolution:", True, (255, 255, 255))
        resLabelRect = resLabel.get_rect(
            right=self.resolutionDropdown.rect.left - 10,
            centery=self.resolutionDropdown.rect.centery
        )
        self.screen.blit(resLabel, resLabelRect)
        # Fullscreen label
        fsLabel = labelFont.render("Fullscreen:", True, (255, 255, 255))
        fsLabelRect = fsLabel.get_rect(
            right=self.fullscreenCheckbox.rect.left - 10,
            centery=self.fullscreenCheckbox.rect.centery
        )
        self.screen.blit(fsLabel, fsLabelRect)
        # Debug label
        dbLabel = labelFont.render("Debug:", True, (255, 255, 255))
        dbLabelRect = dbLabel.get_rect(
            right=self.debugCheckbox.rect.left - 10,
            centery=self.debugCheckbox.rect.centery
        )
        self.screen.blit(dbLabel, dbLabelRect)

        # Components
        self.fullscreenCheckbox.draw(self.screen)
        self.debugCheckbox.draw(self.screen)
        self.backButton.draw(self.screen)
        self.applyButton.draw(self.screen)
        self.resolutionDropdown.draw(self.screen)

        # Toast queue
        if not self.activeToast and self.toastQueue:
            self.activeToast = self.toastQueue.pop(0)
            self.activeToast.start()

        if self.activeToast:
            self.activeToast.draw(self.screen)
            if self.activeToast.isExpired():
                self.activeToast = None

        pygame.display.flip()
