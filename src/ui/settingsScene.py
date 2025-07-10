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

        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

        # Fetch settings
        w = readSetting("WINDOW_WIDTH")
        h = readSetting("WINDOW_HEIGHT")
        currentResolution = f"{w}x{h}"
        fsDefault = readSetting("FULLSCREEN")
        dbgDefault = readSetting("DEBUG")
        tszDefault = readSetting("TILE_SIZE")
        fszDefault = readSetting("FIGURE_SIZE")
        #gszDefault = readSetting("GRID_SIZE")

        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 80

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

        self.fullscreenCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=fsDefault,
            onToggle=self.handleFullscreenToggle
        )
        currentY += 40

        self.debugCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=dbgDefault,
            onToggle=None
        )
        currentY += 60

        self.tileSizeSlider = Slider(
            rect=(xCenter, currentY, 200, 20),
            font=self.dropdownFont,
            minValue=50, maxValue=150,
            value=tszDefault,
            onChange=lambda value: self.addToast(Toast("Start new game to apply tile size changes", type="warning"))
        )
        currentY += 60

        self.figureSizeSlider = Slider(
            rect=(xCenter, currentY, 200, 20),
            font=self.dropdownFont,
            minValue=10, maxValue=50,
            value=fszDefault,
            onChange=lambda value: self.addToast(Toast("Start new game to apply figure size changes", type="warning"))
        )
        currentY += 40

        # self.gridSizeSlider = Slider(...)
        # currentY += 60

        self.applyButton = Button("Apply", (xCenter, currentY, 200, 60), self.buttonFont)
        currentY += 80

        self.backButton = Button("Back", (xCenter, currentY, 200, 60), self.buttonFont)

    def handleEvents(self, events):
        self.applyScroll(events)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switchScene(GameState.MENU)

            if self.resolutionDropdown.handleEvent(event, yOffset=self.scrollOffset):
                continue

            self.fullscreenCheckbox.handleEvent(event, yOffset=self.scrollOffset)
            self.debugCheckbox.handleEvent(event, yOffset=self.scrollOffset)
            self.tileSizeSlider.handleEvent(event, yOffset=self.scrollOffset)
            self.figureSizeSlider.handleEvent(event, yOffset=self.scrollOffset)
            # self.gridSizeSlider.handleEvent(event, yOffset=self.scrollOffset)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.MENU)
                elif self.applyButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    selected_resolution = self.resolutionDropdown.getSelected()
                    if selected_resolution:
                        width, height = map(int, selected_resolution.split("x"))
                        updateResolution(width, height)

                    updateFullscreen(self.fullscreenCheckbox.isChecked())
                    updateDebug(self.debugCheckbox.isChecked())
                    updateTileSize(self.tileSizeSlider.getValue())
                    updateFigureSize(self.figureSizeSlider.getValue())
                    # updateGridSize(self.gridSizeSlider.getValue())

                    self.addToast(Toast("Settings successfully saved", type="success"))

    def draw(self):
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        labelFont = self.dropdownFont

        titleText = self.font.render("Settings", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY + offsetY))
        self.screen.blit(titleText, titleRect)

        resLabel = labelFont.render("Resolution:", True, (255, 255, 255))
        resLabelRect = resLabel.get_rect(
            right=self.resolutionDropdown.rect.left - 10,
            centery=self.resolutionDropdown.rect.centery + offsetY
        )
        self.screen.blit(resLabel, resLabelRect)

        fsLabel = labelFont.render("Fullscreen:", True, (255, 255, 255))
        fsLabelRect = fsLabel.get_rect(
            right=self.fullscreenCheckbox.rect.left - 10,
            centery=self.fullscreenCheckbox.rect.centery + offsetY
        )
        self.screen.blit(fsLabel, fsLabelRect)

        dbLabel = labelFont.render("Debug:", True, (255, 255, 255))
        dbLabelRect = dbLabel.get_rect(
            right=self.debugCheckbox.rect.left - 10,
            centery=self.debugCheckbox.rect.centery + offsetY
        )
        self.screen.blit(dbLabel, dbLabelRect)

        tszLabel = labelFont.render("Tile size:", True, (255, 255, 255))
        tszLabelRect = tszLabel.get_rect(
            right=self.tileSizeSlider.rect.left - 10,
            centery=self.tileSizeSlider.rect.centery + offsetY
        )
        self.screen.blit(tszLabel, tszLabelRect)

        fszLabel = labelFont.render("Figure size:", True, (255, 255, 255))
        fszLabelRect = fszLabel.get_rect(
            right=self.figureSizeSlider.rect.left - 10,
            centery=self.figureSizeSlider.rect.centery + offsetY
        )
        self.screen.blit(fszLabel, fszLabelRect)

        # gszLabel = labelFont.render("Grid size:", True, ...)
        # self.screen.blit(gszLabel, ...)

        self.resolutionDropdown.draw(self.screen, yOffset=offsetY)
        self.fullscreenCheckbox.draw(self.screen, yOffset=offsetY)
        self.debugCheckbox.draw(self.screen, yOffset=offsetY)
        self.tileSizeSlider.draw(self.screen, yOffset=offsetY)
        self.figureSizeSlider.draw(self.screen, yOffset=offsetY)
        # self.gridSizeSlider.draw(self.screen, yOffset=offsetY)
        self.applyButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)

        if not self.activeToast and self.toastQueue:
            self.activeToast = self.toastQueue.pop(0)
            self.activeToast.start()

        if self.activeToast:
            self.activeToast.draw(self.screen)
            if self.activeToast.isExpired():
                self.activeToast = None

        self.maxScroll = max(self.screen.get_height(), self.backButton.rect.bottom + 80)
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
