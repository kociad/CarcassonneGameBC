import pygame
from ui.scene import Scene
from gameState import GameState
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast
from ui.components.checkbox import Checkbox
from ui.components.slider import Slider
from utils.settingsWriter import updateResolution, updateFullscreen, updateDebug, updateTileSize, updateFigureSize, updateGridSize
from utils.settingsReader import readSetting

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
        
        #Fetch settings from file
        w = readSetting("WINDOW_WIDTH")
        h = readSetting("WINDOW_HEIGHT")
        currentResolution = f"{w}x{h}"
        
        fsDefault = readSetting("FULLSCREEN")
        dbgDefault = readSetting("DEBUG")
        tszDefault = readSetting("TILE_SIZE")
        fszDefault = readSetting("FIGURE_SIZE")
        #gszDefault = readSetting("GRID_SIZE")


        #Layout anchor
        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 80

        #Resolution settings
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
            onSelect=lambda value: self.addToast(Toast("Restart the game to apply resolution changes", type="warning")),
        )
        self.resolutionDropdown.setDisabled(fsDefault)
        currentY += 60
        
        #Fullscreen checkbox
        self.fullscreenCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=fsDefault,
            onToggle=self.handleFullscreenToggle
        )
        currentY += 40
        
        #Debug mode checkbox
        self.debugCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=dbgDefault,
            onToggle=None
        )
        currentY += 60
        
        #TILE_SIZE slider
        self.tileSizeSlider = Slider(
            rect=(xCenter, currentY, 200, 20),
            font=self.dropdownFont,
            minValue=50, maxValue=150,
            value=tszDefault,
            onChange=lambda value: self.addToast(Toast("Start new game to apply tile size changes", type="warning"))
        )
        currentY += 60

        #FIGURE_SIZE slider
        self.figureSizeSlider = Slider(
            rect=(xCenter, currentY, 200, 20),
            font=self.dropdownFont,
            minValue=10, maxValue=50,
            value=fszDefault,
            onChange=lambda value: self.addToast(Toast("Start new game to apply figure size changes", type="warning"))
        )
        currentY += 40

        #GRID_SIZE slider
        """
        self.gridSizeSlider = Slider(
            rect=(xCenter, currentY, 200, 20),
            font=self.dropdownFont,
            minValue=15, maxValue=30,
            value=gszDefault,
            onChange=None
        )
        currentY += 60
        """
        
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
            self.tileSizeSlider.handleEvent(event)
            self.figureSizeSlider.handleEvent(event)
            #self.gridSizeSlider.handleEvent(event)
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos):
                    self.switchScene(GameState.MENU)
                elif self.applyButton.isClicked(event.pos):
                    selected_resolution = self.resolutionDropdown.getSelected()
                    if selected_resolution:
                        width, height = map(int, selected_resolution.split("x"))
                        updateResolution(width, height)
                        
                    updateFullscreen(self.fullscreenCheckbox.isChecked())
                    updateDebug(self.debugCheckbox.isChecked())
                    updateTileSize(self.tileSizeSlider.getValue())
                    updateFigureSize(self.figureSizeSlider.getValue())
                    #updateGridSize(self.gridSizeSlider.getValue())
                    
                    self.addToast(Toast("Settings successfully saved", type="success"))
                    
    def update(self):
        pass
        
    def draw(self):
        self.screen.fill((20, 20, 20))

        #Title
        titleText = self.font.render("Settings", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY))
        self.screen.blit(titleText, titleRect)

        #Labels
        labelFont = self.dropdownFont
        
        #Resolution dropdown label
        resLabel = labelFont.render("Resolution:", True, (255, 255, 255))
        resLabelRect = resLabel.get_rect(
            right=self.resolutionDropdown.rect.left - 10,
            centery=self.resolutionDropdown.rect.centery
        )
        self.screen.blit(resLabel, resLabelRect)
        
        #Fullscreen label
        fsLabel = labelFont.render("Fullscreen:", True, (255, 255, 255))
        fsLabelRect = fsLabel.get_rect(
            right=self.fullscreenCheckbox.rect.left - 10,
            centery=self.fullscreenCheckbox.rect.centery
        )
        self.screen.blit(fsLabel, fsLabelRect)
        
        #Debug label
        dbLabel = labelFont.render("Debug:", True, (255, 255, 255))
        dbLabelRect = dbLabel.get_rect(
            right=self.debugCheckbox.rect.left - 10,
            centery=self.debugCheckbox.rect.centery
        )
        self.screen.blit(dbLabel, dbLabelRect)
        
        #Tile size slider
        tszLabel = labelFont.render("Tile size:", True, (255, 255, 255))
        tszLabelRect = tszLabel.get_rect(
            right=self.tileSizeSlider.rect.left - 10,
            centery=self.tileSizeSlider.rect.centery
        )
        self.screen.blit(tszLabel, tszLabelRect)
        
        #Figure size slider
        fszLabel = labelFont.render("Figure size:", True, (255, 255, 255))
        fszLabelRect = fszLabel.get_rect(
            right=self.figureSizeSlider.rect.left - 10,
            centery=self.figureSizeSlider.rect.centery
        )
        self.screen.blit(fszLabel, fszLabelRect)
        
        #Grid size slider
        """
        gszLabel = labelFont.render("Grid size:", True, (255, 255, 255))
        gszLabelRect = gszLabel.get_rect(
            right=self.gridSizeSlider.rect.left - 10,
            centery=self.gridSizeSlider.rect.centery
        )
        self.screen.blit(gszLabel, gszLabelRect)
        """

        # Components
        self.debugCheckbox.draw(self.screen)
        self.fullscreenCheckbox.draw(self.screen)
        self.backButton.draw(self.screen)
        self.applyButton.draw(self.screen)
        self.tileSizeSlider.draw(self.screen)
        self.figureSizeSlider.draw(self.screen)
        #self.gridSizeSlider.draw(self.screen)
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
        
    def addToast(self, toast):
        if self.activeToast and self.activeToast.message == toast.message:
            return
        if any(t.message == toast.message for t in self.toastQueue):
            return
        self.toastQueue.append(toast)
        
    def handleFullscreenToggle(self, value):
        self.showResolutionDropdown = not value
        self.resolutionDropdown.setDisabled(value)
        self.addToast(Toast("Restart the game to apply fullscreen changes", type="warning"))