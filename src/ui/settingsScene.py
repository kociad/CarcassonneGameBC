import pygame
from ui.scene import Scene
from gameState import GameState
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast
from ui.components.checkbox import Checkbox
from ui.components.slider import Slider
from utils.settingsManager import settings_manager

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

        # Subscribe to settings changes for automatic UI updates
        settings_manager.subscribe("FULLSCREEN", self.onFullscreenChanged)
        settings_manager.subscribe("DEBUG", self.onDebugChanged)

        # Get current values from SettingsManager
        currentResolution = f"{settings_manager.get('WINDOW_WIDTH')}x{settings_manager.get('WINDOW_HEIGHT')}"

        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 60

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
        self.resolutionDropdown.setDisabled(settings_manager.get("FULLSCREEN"))
        currentY += 60

        self.fullscreenCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settings_manager.get("FULLSCREEN"),
            onToggle=self.handleFullscreenToggle
        )
        currentY += 40

        self.debugCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settings_manager.get("DEBUG"),
            onToggle=None
        )
        currentY += 60

        self.tileSizeSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=50, maxValue=150,
            value=settings_manager.get("TILE_SIZE"),
            onChange=self.onTileSizeChanged
        )
        
        self.tileSizeSlider.setDisabled(not settings_manager.get("DEBUG"))
        currentY += 40

        self.figureSizeSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=10, maxValue=50,
            value=settings_manager.get("FIGURE_SIZE"),
            onChange=lambda value: self.addToast(Toast("Start new game to apply figure size changes", type="warning"))
        )
        
        self.figureSizeSlider.setDisabled(not settings_manager.get("DEBUG"))
        currentY += 40

        currentTileSize = settings_manager.get("TILE_SIZE")
        currentSidebarWidth = settings_manager.get("SIDEBAR_WIDTH")
        minSidebarWidth = currentTileSize + 20

        self.sidebarWidthSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=minSidebarWidth,
            maxValue=400,
            value=max(currentSidebarWidth, minSidebarWidth),
            onChange=lambda value: self.addToast(Toast("Start new game to apply sidebar width changes", type="warning"))
        )
        
        
        self.sidebarWidthSlider.setDisabled(not settings_manager.get("DEBUG"))
        currentY += 60

        self.applyButton = Button("Apply", (xCenter, currentY, 200, 60), self.buttonFont)
        currentY += 80

        self.backButton = Button("Back", (xCenter, currentY, 200, 60), self.buttonFont)

    def onTileSizeChanged(self, newTileSize):
        """Handle tile size change - update sidebar width slider minimum"""
        newMinSidebarWidth = newTileSize + 20
        self.sidebarWidthSlider.setMinValue(newMinSidebarWidth)
        
        currentSidebarWidth = self.sidebarWidthSlider.getValue()
        if currentSidebarWidth < newMinSidebarWidth:
            self.sidebarWidthSlider.setValue(newMinSidebarWidth)
            self.addToast(Toast(f"Sidebar width adjusted to minimum ({newMinSidebarWidth}px)", type="info"))
        
        self.addToast(Toast("Start new game to apply tile size changes", type="warning"))

    def onFullscreenChanged(self, key, old_value, new_value):
        """Callback for when fullscreen setting changes"""
        self.resolutionDropdown.setDisabled(new_value)

    def onDebugChanged(self, key, old_value, new_value):
        """Callback for when DEBUG setting changes"""
        from utils.loggingConfig import updateLoggingLevel
        updateLoggingLevel()
        
        self.sidebarWidthSlider.setDisabled(not new_value)
        self.tileSizeSlider.setDisabled(not new_value)
        self.figureSizeSlider.setDisabled(not new_value)

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
            self.sidebarWidthSlider.handleEvent(event, yOffset=self.scrollOffset)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.MENU)
                elif self.applyButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.applySettings()

    def applySettings(self):
        """Apply all settings using SettingsManager"""
        changes = {}
        
        # Resolution
        selected_resolution = self.resolutionDropdown.getSelected()
        if selected_resolution:
            width, height = map(int, selected_resolution.split("x"))
            changes["WINDOW_WIDTH"] = width
            changes["WINDOW_HEIGHT"] = height

        # Other settings
        changes["FULLSCREEN"] = self.fullscreenCheckbox.isChecked()
        changes["DEBUG"] = self.debugCheckbox.isChecked()
        
        # Tile size a figure size jen pokud nejsou disabled
        if not self.tileSizeSlider.isDisabled():
            changes["TILE_SIZE"] = self.tileSizeSlider.getValue()
        
        if not self.figureSizeSlider.isDisabled():
            changes["FIGURE_SIZE"] = self.figureSizeSlider.getValue()
        
        # Sidebar width jen pokud není disabled
        if not self.sidebarWidthSlider.isDisabled():
            changes["SIDEBAR_WIDTH"] = self.sidebarWidthSlider.getValue()

        # Apply all changes at once
        success = True
        for key, value in changes.items():
            if not settings_manager.set(key, value, temporary=False):
                success = False

        if success:
            self.addToast(Toast("Settings successfully saved", type="success"))
        else:
            self.addToast(Toast("Failed to save some settings", type="error"))

    def handleFullscreenToggle(self, value):
        settings_manager.set("FULLSCREEN", value, temporary=True)
        self.addToast(Toast("Restart the game to apply fullscreen changes", type="warning"))

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

        labelColor = (120, 120, 120) if self.tileSizeSlider.isDisabled() else (255, 255, 255)
        tszLabel = labelFont.render("Tile size:", True, labelColor)
        tszLabelRect = tszLabel.get_rect(
            right=self.tileSizeSlider.rect.left - 10,
            centery=self.tileSizeSlider.rect.centery + offsetY
        )
        self.screen.blit(tszLabel, tszLabelRect)

        labelColor = (120, 120, 120) if self.figureSizeSlider.isDisabled() else (255, 255, 255)
        fszLabel = labelFont.render("Figure size:", True, labelColor)
        fszLabelRect = fszLabel.get_rect(
            right=self.figureSizeSlider.rect.left - 10,
            centery=self.figureSizeSlider.rect.centery + offsetY
        )
        self.screen.blit(fszLabel, fszLabelRect)

        labelColor = (120, 120, 120) if self.sidebarWidthSlider.isDisabled() else (255, 255, 255)
        sbwLabel = labelFont.render("Sidebar width:", True, labelColor)
        sbwLabelRect = sbwLabel.get_rect(
            right=self.sidebarWidthSlider.rect.left - 10,
            centery=self.sidebarWidthSlider.rect.centery + offsetY
        )
        self.screen.blit(sbwLabel, sbwLabelRect)

        self.fullscreenCheckbox.draw(self.screen, yOffset=offsetY)
        self.debugCheckbox.draw(self.screen, yOffset=offsetY)
        self.tileSizeSlider.draw(self.screen, yOffset=offsetY)  # Vždy vykreslit
        self.figureSizeSlider.draw(self.screen, yOffset=offsetY)  # Vždy vykreslit
        self.sidebarWidthSlider.draw(self.screen, yOffset=offsetY)  # Vždy vykreslit
        self.applyButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        self.resolutionDropdown.draw(self.screen, yOffset=offsetY)

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