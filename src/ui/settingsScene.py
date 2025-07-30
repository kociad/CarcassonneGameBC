import pygame
from ui.scene import Scene
from gameState import GameState
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast, ToastManager
from ui.components.checkbox import Checkbox
from ui.components.slider import Slider
from utils.settingsManager import settingsManager
import typing

class SettingsScene(Scene):
    def __init__(self, screen: pygame.Surface, switchSceneCallback: typing.Callable) -> None:
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        self.toastManager = ToastManager(maxToasts=5)
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

        settingsManager.subscribe("FULLSCREEN", self.onFullscreenChanged)
        settingsManager.subscribe("DEBUG", self.onDebugChanged)

        currentResolution = f"{settingsManager.get('WINDOW_WIDTH')}x{settingsManager.get('WINDOW_HEIGHT')}"
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
            onSelect=lambda value: self.addToast(Toast("In order to apply resolution setting, restart the game", type="warning")),
        )
        self.resolutionDropdown.setDisabled(settingsManager.get("FULLSCREEN"))
        currentY += 60

        self.fullscreenCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settingsManager.get("FULLSCREEN"),
            onToggle=lambda value: [self.handleFullscreenToggle(value), self.addToast(Toast("In order to apply fullscreen setting, restart the game", type="warning"))]
        )
        currentY += 40

        self.validPlacementCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settingsManager.get("SHOW_VALID_PLACEMENTS", True),
            onToggle=lambda value: self.handleValidPlacementToggle(value)
        )
        currentY += 40

        self.debugCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settingsManager.get("DEBUG"),
            onToggle=lambda value: [self.handleDebugToggle(value), self.addToast(Toast("In order to apply debug setting, restart the game", type="warning"))]
        )
        currentY += 40

        self.logToConsoleCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settingsManager.get("LOG_TO_CONSOLE", True),
            onToggle=lambda value: [self.handleLogToConsoleToggle(value), self.addToast(Toast("In order to apply log to console setting, restart the game", type="warning"))]
        )
        self.logToConsoleCheckbox.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        self.aiTurnDelayField = InputField(
            rect=(xCenter, currentY, 80, 40),
            font=self.inputFont,
            initialText=str(settingsManager.get("AI_TURN_DELAY", 1.0)),
            onTextChange=None,
            numeric=True,
            minValue=0.0,
            maxValue=10.0
        )
        self.aiTurnDelayField.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 60

        self.aiSimulationCheckbox = Checkbox(
            rect=(xCenter, currentY, 20, 20),
            checked=settingsManager.get("AI_USE_SIMULATION", False),
            onToggle=lambda value: self.handleAISimulationToggle(value)
        )
        self.aiSimulationCheckbox.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        self.aiStrategicCandidatesField = InputField(
            rect=(xCenter, currentY, 80, 40),
            font=self.inputFont,
            initialText=str(settingsManager.get("AI_STRATEGIC_CANDIDATES", 3)),
            onTextChange=None,
            numeric=True,
            minValue=-1,
            maxValue=20
        )
        self.aiStrategicCandidatesField.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 60

        self.aiThinkingSpeedField = InputField(
            rect=(xCenter, currentY, 80, 40),
            font=self.inputFont,
            initialText=str(settingsManager.get("AI_THINKING_SPEED", 0.5)),
            onTextChange=None,
            numeric=True,
            minValue=-1,
            maxValue=2.0
        )
        self.aiThinkingSpeedField.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 60

        self.fpsSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=30, maxValue=144,
            value=settingsManager.get("FPS", 60),
            onChange=None
        )
        self.fpsSlider.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        self.gridSizeSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=10, maxValue=50,
            value=settingsManager.get("GRID_SIZE", 20),
            onChange=None
        )
        self.gridSizeSlider.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        self.tileSizeSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=50, maxValue=150,
            value=settingsManager.get("TILE_SIZE"),
            onChange=None
        )
        self.tileSizeSlider.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        self.figureSizeSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=10, maxValue=50,
            value=settingsManager.get("FIGURE_SIZE"),
            onChange=None
        )
        self.figureSizeSlider.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        currentTileSize = settingsManager.get("TILE_SIZE")
        currentSidebarWidth = settingsManager.get("SIDEBAR_WIDTH")
        minSidebarWidth = currentTileSize + 20
        self.sidebarWidthSlider = Slider(
            rect=(xCenter, currentY, 180, 20),
            font=self.dropdownFont,
            minValue=minSidebarWidth,
            maxValue=400,
            value=max(currentSidebarWidth, minSidebarWidth),
            onChange=None
        )
        self.sidebarWidthSlider.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 40

        self.gameLogMaxEntriesField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont,
            initialText=str(settingsManager.get("GAME_LOG_MAX_ENTRIES", 2000)),
            onTextChange=lambda value: self.addToast(Toast("In order to apply game log max entries setting, restart the game", type="warning")),
            numeric=True,
            minValue=100,
            maxValue=50000
        )
        self.gameLogMaxEntriesField.setDisabled(not settingsManager.get("DEBUG"))
        currentY += 60

        self.applyButton = Button(
            (xCenter, currentY, 200, 60),
            "Apply",
            self.buttonFont
        )
        currentY += 80

        self.backButton = Button(
            (xCenter, currentY, 200, 60),
            "Back",
            self.buttonFont
        )

    def onTileSizeChanged(self, newTileSize):
        newMinSidebarWidth = newTileSize + 20
        self.sidebarWidthSlider.setMinValue(newMinSidebarWidth)
        
        currentSidebarWidth = self.sidebarWidthSlider.getValue()
        if currentSidebarWidth < newMinSidebarWidth:
            self.sidebarWidthSlider.setValue(newMinSidebarWidth)
            self.addToast(Toast(f"Sidebar width adjusted to minimum ({newMinSidebarWidth}px)", type="info"))
        

    def onFullscreenChanged(self, key, old_value, new_value):
        self.resolutionDropdown.setDisabled(new_value)

    def onDebugChanged(self, key, old_value, new_value):
        from utils.loggingConfig import updateLoggingLevel
        updateLoggingLevel()
        
        self.fpsSlider.setDisabled(not new_value)
        self.gridSizeSlider.setDisabled(not new_value)
        self.sidebarWidthSlider.setDisabled(not new_value)
        self.tileSizeSlider.setDisabled(not new_value)
        self.figureSizeSlider.setDisabled(not new_value)
        self.gameLogMaxEntriesField.setDisabled(not new_value)
        self.aiTurnDelayField.setDisabled(not new_value)
        self.aiSimulationCheckbox.setDisabled(not new_value)
        self.aiStrategicCandidatesField.setDisabled(not new_value)
        self.aiThinkingSpeedField.setDisabled(not new_value)
        self.logToConsoleCheckbox.setDisabled(not new_value)

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
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
            self.logToConsoleCheckbox.handleEvent(event, yOffset=self.scrollOffset)
            self.validPlacementCheckbox.handleEvent(event, yOffset=self.scrollOffset)
            self.aiSimulationCheckbox.handleEvent(event, yOffset=self.scrollOffset)
            fpsWasDragging = self.fpsSlider.dragging
            gridWasDragging = self.gridSizeSlider.dragging
            tileWasDragging = self.tileSizeSlider.dragging
            figureWasDragging = self.figureSizeSlider.dragging
            sidebarWasDragging = self.sidebarWidthSlider.dragging
            self.fpsSlider.handleEvent(event, yOffset=self.scrollOffset)
            self.gridSizeSlider.handleEvent(event, yOffset=self.scrollOffset)
            self.tileSizeSlider.handleEvent(event, yOffset=self.scrollOffset)
            self.figureSizeSlider.handleEvent(event, yOffset=self.scrollOffset)
            self.sidebarWidthSlider.handleEvent(event, yOffset=self.scrollOffset)
            if event.type == pygame.MOUSEBUTTONUP:
                if fpsWasDragging:
                    self.addToast(Toast("In order to apply FPS setting, restart the game", type="warning"))
                if gridWasDragging:
                    self.addToast(Toast("In order to apply grid size setting, restart the game", type="warning"))
                if tileWasDragging:
                    self.addToast(Toast("In order to apply tile size setting, restart the game", type="warning"))
                if figureWasDragging:
                    self.addToast(Toast("In order to apply figure size setting, restart the game", type="warning"))
                if sidebarWasDragging:
                    self.addToast(Toast("In order to apply sidebar width setting, restart the game", type="warning"))
            self.gameLogMaxEntriesField.handleEvent(event, yOffset=self.scrollOffset)
            self.aiTurnDelayField.handleEvent(event, yOffset=self.scrollOffset)
            self.aiStrategicCandidatesField.handleEvent(event, yOffset=self.scrollOffset)
            self.aiThinkingSpeedField.handleEvent(event, yOffset=self.scrollOffset)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.MENU)
                elif self.applyButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.applySettings()

    def handleDebugToggle(self, value):
        settingsManager.set("DEBUG", value, temporary=True)

    def handleAITurnDelayToggle(self, value):
        settingsManager.set("AI_TURN_DELAY_ENABLED", value, temporary=True)

    def handleAISimulationToggle(self, value):
        settingsManager.set("AI_USE_SIMULATION", value, temporary=True)

    def handleLogToConsoleToggle(self, value):
        settingsManager.set("LOG_TO_CONSOLE", value, temporary=True)

    def handleValidPlacementToggle(self, value):
        settingsManager.set("SHOW_VALID_PLACEMENTS", value, temporary=True)

    def applySettings(self):
        changes = {}
        
        selected_resolution = self.resolutionDropdown.getSelected()
        if selected_resolution:
            width, height = map(int, selected_resolution.split("x"))
            changes["WINDOW_WIDTH"] = width
            changes["WINDOW_HEIGHT"] = height

        changes["FULLSCREEN"] = self.fullscreenCheckbox.isChecked()
        changes["DEBUG"] = self.debugCheckbox.isChecked()
        if not self.logToConsoleCheckbox.isDisabled():
            changes["LOG_TO_CONSOLE"] = self.logToConsoleCheckbox.isChecked()
        if not self.validPlacementCheckbox.isDisabled():
            changes["SHOW_VALID_PLACEMENTS"] = self.validPlacementCheckbox.isChecked()
        if not self.aiSimulationCheckbox.isDisabled():
            changes["AI_USE_SIMULATION"] = self.aiSimulationCheckbox.isChecked()
        if not self.aiTurnDelayField.isDisabled():
            try:
                delay = float(self.aiTurnDelayField.getText())
                if 0.0 <= delay <= 10.0:
                    changes["AI_TURN_DELAY"] = delay
                else:
                    self.addToast(Toast("AI turn delay must be between 0 and 10 seconds", type="error"))
                    return
            except ValueError:
                self.addToast(Toast("Invalid AI turn delay value", type="error"))
                return
        
        if not self.fpsSlider.isDisabled():
            changes["FPS"] = self.fpsSlider.getValue()
        
        if not self.gridSizeSlider.isDisabled():
            changes["GRID_SIZE"] = self.gridSizeSlider.getValue()
        
        if not self.tileSizeSlider.isDisabled():
            changes["TILE_SIZE"] = self.tileSizeSlider.getValue()
        
        if not self.figureSizeSlider.isDisabled():
            changes["FIGURE_SIZE"] = self.figureSizeSlider.getValue()
        
        if not self.sidebarWidthSlider.isDisabled():
            changes["SIDEBAR_WIDTH"] = self.sidebarWidthSlider.getValue()
        
        if not self.gameLogMaxEntriesField.isDisabled():
            try:
                logMaxEntries = int(self.gameLogMaxEntriesField.getText())
                if 100 <= logMaxEntries <= 50000:
                    changes["GAME_LOG_MAX_ENTRIES"] = logMaxEntries
                else:
                    self.addToast(Toast("Game log max entries must be between 100 and 50000", type="error"))
                    return
            except ValueError:
                self.addToast(Toast("Invalid game log max entries value", type="error"))
                return

        if not self.aiStrategicCandidatesField.isDisabled():
            try:
                candidates = int(self.aiStrategicCandidatesField.getText())
                if candidates == -1 or (1 <= candidates <= 20):
                    changes["AI_STRATEGIC_CANDIDATES"] = candidates
                else:
                    self.addToast(Toast("AI strategic candidates must be -1 (all) or between 1 and 20", type="error"))
                    return
            except ValueError:
                self.addToast(Toast("Invalid AI strategic candidates value", type="error"))
                return

        if not self.aiThinkingSpeedField.isDisabled():
            try:
                thinkingSpeed = float(self.aiThinkingSpeedField.getText())
                if -1 <= thinkingSpeed <= 2.0:
                    changes["AI_THINKING_SPEED"] = thinkingSpeed
                else:
                    self.addToast(Toast("AI thinking speed must be between -1 and 2.0 seconds", type="error"))
                    return
            except ValueError:
                self.addToast(Toast("Invalid AI thinking speed value", type="error"))
                return

        success = True
        for key, value in changes.items():
            if not settingsManager.set(key, value, temporary=False):
                success = False
                
        current_debug = settingsManager.get("DEBUG")
        checkbox_debug = self.debugCheckbox.isChecked()
        if current_debug != checkbox_debug:
            settingsManager.set("DEBUG", checkbox_debug, temporary=False)

        if success:
            self.addToast(Toast("Settings successfully saved", type="success"))
            #self.addToast(Toast("Restart the game to apply changes", type="warning"))
            
            if "GAME_LOG_MAX_ENTRIES" in changes:
                from utils.loggingConfig import gameLogInstance
                if gameLogInstance:
                    gameLogInstance.updateMaxEntries()
        else:
            self.addToast(Toast("Failed to save some settings", type="error"))

    def handleFullscreenToggle(self, value):
        self.resolutionDropdown.setDisabled(value)

    def draw(self) -> None:
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

        labelColor = (120, 120, 120) if self.logToConsoleCheckbox.isDisabled() else (255, 255, 255)
        logToConsoleLabel = labelFont.render("Log to console:", True, labelColor)
        logToConsoleLabelRect = logToConsoleLabel.get_rect(
            right=self.logToConsoleCheckbox.rect.left - 10,
            centery=self.logToConsoleCheckbox.rect.centery + offsetY
        )
        self.screen.blit(logToConsoleLabel, logToConsoleLabelRect)
        self.logToConsoleCheckbox.draw(self.screen, yOffset=offsetY)

        labelColor = (120, 120, 120) if self.validPlacementCheckbox.isDisabled() else (255, 255, 255)
        validPlacementsLabel = labelFont.render("Show valid card placements:", True, labelColor)
        validPlacementsLabelRect = validPlacementsLabel.get_rect(
            right=self.validPlacementCheckbox.rect.left - 10,
            centery=self.validPlacementCheckbox.rect.centery + offsetY
        )
        self.screen.blit(validPlacementsLabel, validPlacementsLabelRect)

        labelColor = (120, 120, 120) if self.aiTurnDelayField.isDisabled() else (255, 255, 255)
        aiDelayLabel = labelFont.render("AI turn delay (s):", True, labelColor)
        aiDelayLabelRect = aiDelayLabel.get_rect(
            right=self.aiTurnDelayField.rect.left - 10,
            centery=self.aiTurnDelayField.rect.centery + offsetY
        )
        self.screen.blit(aiDelayLabel, aiDelayLabelRect)
        self.aiTurnDelayField.draw(self.screen, yOffset=offsetY)

        labelColor = (120, 120, 120) if self.fpsSlider.isDisabled() else (255, 255, 255)
        fpsLabel = labelFont.render("FPS:", True, labelColor)
        fpsLabelRect = fpsLabel.get_rect(
            right=self.fpsSlider.rect.left - 10,
            centery=self.fpsSlider.rect.centery + offsetY
        )
        self.screen.blit(fpsLabel, fpsLabelRect)

        labelColor = (120, 120, 120) if self.gridSizeSlider.isDisabled() else (255, 255, 255)
        gridLabel = labelFont.render("Grid size:", True, labelColor)
        gridLabelRect = gridLabel.get_rect(
            right=self.gridSizeSlider.rect.left - 10,
            centery=self.gridSizeSlider.rect.centery + offsetY
        )
        self.screen.blit(gridLabel, gridLabelRect)

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

        labelColor = (120, 120, 120) if self.gameLogMaxEntriesField.isDisabled() else (255, 255, 255)
        logLabel = labelFont.render("Game log max entries:", True, labelColor)
        logLabelRect = logLabel.get_rect(
            right=self.gameLogMaxEntriesField.rect.left - 10,
            centery=self.gameLogMaxEntriesField.rect.centery + offsetY
        )
        self.screen.blit(logLabel, logLabelRect)

        self.fullscreenCheckbox.draw(self.screen, yOffset=offsetY)
        self.debugCheckbox.draw(self.screen, yOffset=offsetY)
        self.logToConsoleCheckbox.draw(self.screen, yOffset=offsetY)
        self.validPlacementCheckbox.draw(self.screen, yOffset=self.scrollOffset)
        self.fpsSlider.draw(self.screen, yOffset=offsetY)
        self.gridSizeSlider.draw(self.screen, yOffset=offsetY)
        self.tileSizeSlider.draw(self.screen, yOffset=offsetY)
        self.figureSizeSlider.draw(self.screen, yOffset=offsetY)
        self.sidebarWidthSlider.draw(self.screen, yOffset=offsetY)
        self.gameLogMaxEntriesField.draw(self.screen, yOffset=offsetY)
        self.aiTurnDelayField.draw(self.screen, yOffset=offsetY)

        labelColor = (120, 120, 120) if self.aiSimulationCheckbox.isDisabled() else (255, 255, 255)
        aiSimulationLabel = labelFont.render("AI simulation:", True, labelColor)
        aiSimulationLabelRect = aiSimulationLabel.get_rect(
            right=self.aiSimulationCheckbox.rect.left - 10,
            centery=self.aiSimulationCheckbox.rect.centery + offsetY
        )
        self.screen.blit(aiSimulationLabel, aiSimulationLabelRect)
        self.aiSimulationCheckbox.draw(self.screen, yOffset=offsetY)

        labelColor = (120, 120, 120) if self.aiStrategicCandidatesField.isDisabled() else (255, 255, 255)
        aiCandidatesLabel = labelFont.render("AI strategic candidates:", True, labelColor)
        aiCandidatesLabelRect = aiCandidatesLabel.get_rect(
            right=self.aiStrategicCandidatesField.rect.left - 10,
            centery=self.aiStrategicCandidatesField.rect.centery + offsetY
        )
        self.screen.blit(aiCandidatesLabel, aiCandidatesLabelRect)
        self.aiStrategicCandidatesField.draw(self.screen, yOffset=offsetY)

        labelColor = (120, 120, 120) if self.aiThinkingSpeedField.isDisabled() else (255, 255, 255)
        thinkingSpeedLabel = labelFont.render("AI Thinking Speed (s):", True, labelColor)
        thinkingSpeedLabelRect = thinkingSpeedLabel.get_rect(
            right=self.aiThinkingSpeedField.rect.left - 10,
            centery=self.aiThinkingSpeedField.rect.centery + offsetY
        )
        self.screen.blit(thinkingSpeedLabel, thinkingSpeedLabelRect)
        self.aiThinkingSpeedField.draw(self.screen, yOffset=offsetY)

        self.applyButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        self.resolutionDropdown.draw(self.screen, yOffset=offsetY)

        self.maxScroll = max(self.screen.get_height(), self.backButton.rect.bottom + 80)
        
        self.toastManager.draw(self.screen)
        
        pygame.display.flip()

    def addToast(self, toast):
        self.toastManager.addToast(toast)