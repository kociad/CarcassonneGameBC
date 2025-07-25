import pygame
import socket
from ui.scene import Scene
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast, ToastManager
from ui.components.checkbox import Checkbox
from gameState import GameState
from utils.settingsManager import settingsManager
import typing
import settings

class PlayerConfiguration:
    """Single source of truth for player data"""
    def __init__(self, name="", isAI=False, enabled=True):
        self.name = name
        self.isAI = isAI
        self.enabled = enabled
        
    def setName(self, name):
        """Update name and handle AI prefix logic"""
        if self.isAI and not name.startswith("AI_"):
            self.isAI = False
        self.name = name
        
    def setAI(self, isAI):
        """Update AI status and handle name prefix"""
        self.isAI = isAI
        if isAI and not self.name.startswith("AI_"):
            self.name = f"AI_{self.name}"
        elif not isAI and self.name.startswith("AI_"):
            self.name = self.name[3:]
            
    def getDisplayName(self):
        """Get name for display purposes"""
        return self.name
        
    def copy(self):
        """Create a copy of this configuration"""
        return PlayerConfiguration(self.name, self.isAI, self.enabled)

class GamePrepareScene(Scene):
    """
    Scene for preparing the game: player setup, network mode, and game settings.
    """
    def __init__(self, screen: pygame.Surface, switchSceneCallback: typing.Callable) -> None:
        """Initialize the GamePrepareScene with UI components and default settings."""
        super().__init__(screen, switchSceneCallback)
        settingsManager.reloadFromFile()
        self.switchSceneCallback = switchSceneCallback
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        self.toastManager = ToastManager(maxToasts=5)
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30
        self.originalPlayerNames = settingsManager.get("PLAYERS", []).copy()
        self.players = []
        for i in range(6):
            if i < len(self.originalPlayerNames):
                name = self.originalPlayerNames[i]
            else:
                name = f"Player {i + 1}"
            enabled = i < 2
            self.players.append(PlayerConfiguration(name, False, enabled))
        networkMode = settingsManager.get("NETWORK_MODE", "local")
        hostIP = settingsManager.get("HOST_IP", "0.0.0.0")
        port = str(settingsManager.get("HOST_PORT", 222))
        self.localIP = socket.gethostbyname(socket.gethostname())
        self.networkMode = networkMode
        xCenter = screen.get_width() // 2 - 100
        currentY = 60
        self.titleY = currentY
        currentY += 80
        self.addPlayerButton = Button(
            (self.screen.get_width() // 2 + 180, currentY + 60, 40, 40),
            "+",
            self.buttonFont
        )
        self.removePlayerButton = Button(
            (self.screen.get_width() // 2 + 230, currentY + 60, 40, 40),
            "−",
            self.buttonFont
        )
        self.playerListY = currentY
        self.aiDifficulties = ["easy", "medium", "hard"]
        self.aiDifficultyDropdownY = self.playerListY + (6 * 50) + 30
        self.aiDifficultyDropdown = Dropdown(
            rect=(xCenter, self.aiDifficultyDropdownY, 200, 40),
            font=self.dropdownFont,
            options=[d.capitalize() for d in self.aiDifficulties],
            defaultIndex=1,
            onSelect=self.handleAIDifficultyChange
        )
        self.buildPlayerFields()
        currentY = self.aiDifficultyDropdownY + 60
        self.networkModes = ["local", "host", "client"]
        defaultIndex = self.networkModes.index(networkMode)
        self.networkModeDropdown = Dropdown(
            rect=(xCenter, currentY, 200, 40),
            font=self.dropdownFont,
            options=self.networkModes,
            defaultIndex=defaultIndex,
            onSelect=self.handleNetworkModeChange
        )
        currentY += 60
        self.hostIPField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont
        )
        self.hostIPField.setText(hostIP)
        currentY += 60
        self.portField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont
        )
        self.portField.setText(port)
        currentY += 80
        self.startButton = Button(
            (xCenter, currentY, 200, 60),
            "Start Game",
            self.buttonFont
        )
        currentY += 80
        self.backButton = Button(
            (xCenter, currentY, 200, 60),
            "Back",
            self.buttonFont
        )
        self.handleNetworkModeChange(networkMode)
    
    def getEnabledPlayersCount(self):
        """Get count of enabled players"""
        return sum(1 for player in self.players if player.enabled)
        
    def buildPlayerFields(self) -> None:
        """Build UI fields based on current player data (single source of truth)"""
        forbiddenWords = ["ai", "easy", "medium", "hard"]
        self.playerFields = []
        aiDifficulty = self.aiDifficulties[self.aiDifficultyDropdown.selectedIndex].upper()
        for i, player in enumerate(self.players):
            y = self.playerListY + (i * 50 if i == 0 else 60 + (i - 1) * 50)
            def makeTextChangeHandler(index):
                def handler(newText):
                    lowerName = newText.lower()
                    if any(word in lowerName for word in forbiddenWords):
                        if index < len(self.originalPlayerNames):
                            defaultName = self.originalPlayerNames[index]
                        else:
                            defaultName = f"Player {index + 1}"
                        self.players[index].setName(defaultName)
                        self.players[index].setAI(False)
                        if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                            nameField = self.playerFields[index][0]
                            nameField.setText(defaultName)
                        if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                            aiCheckbox = self.playerFields[index][1]
                            if aiCheckbox:
                                aiCheckbox.setChecked(False)
                        self.addToast(Toast("Forbidden word in name! Name reset.", type="error"))
                        return
                    self.players[index].setName(newText)
                    self.players[index].setAI(False)
                    if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                        aiCheckbox = self.playerFields[index][1]
                        if aiCheckbox:
                            aiCheckbox.setChecked(False)
                return handler
            nameField = InputField(
                rect=(self.screen.get_width() // 2 - 100, y, 200, 40),
                font=self.inputFont,
                onTextChange=makeTextChangeHandler(i)
            )
            if self.networkMode == "client" and i > 0:
                nameField.setText("")
                nameField.setDisabled(True)
            else:
                name = player.getDisplayName()
                if player.enabled and player.isAI:
                    if "[" in name:
                        name = name.split("[")[0].strip()
                    name = f"{name} [{aiDifficulty}]"
                    player.name = name
                nameField.setText(name)
                nameField.setDisabled(not player.enabled)
                if i > 0 and self.networkMode == "host":
                    nameField.setReadOnly(True)
            aiCheckbox = None
            if i == 0:
                canToggleAI = settings.DEBUG
                aiCheckbox = Checkbox(
                    rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                    checked=player.isAI,
                    onToggle=(lambda value, index=i: self.togglePlayerAI(index, value)) if canToggleAI else None
                )
                aiCheckbox.setDisabled(not player.enabled or not canToggleAI)
            elif i != 0:
                canToggleAI = (self.networkMode == "local")
                aiCheckbox = Checkbox(
                    rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                    checked=player.isAI,
                    onToggle=(lambda value, index=i: self.togglePlayerAI(index, value)) if canToggleAI else None
                )
                aiCheckbox.setDisabled(not player.enabled or not canToggleAI)
            self.playerFields.append((nameField, aiCheckbox))
        # Always show AI difficulty dropdown, but only enable if any AI and local mode
        anyAI = any(p.enabled and p.isAI for p in self.players)
        self.aiDifficultyDropdown.setDisabled(not (anyAI and self.networkMode == "local"))
            
    def togglePlayerAI(self, index: int, value: bool) -> None:
        """Toggle AI status for a player"""
        self.players[index].setAI(value)
        if value:
            aiDifficulty = self.aiDifficulties[self.aiDifficultyDropdown.selectedIndex].upper()
            name = self.players[index].getDisplayName()
            if "[" in name:
                name = name.split("[")[0].strip()
            self.players[index].name = f"{name} [{aiDifficulty}]"
        else:
            name = self.players[index].getDisplayName()
            if "[" in name:
                name = name.split("[")[0].strip()
            self.players[index].name = name
        self.buildPlayerFields()
        
    def handleNetworkModeChange(self, mode: str) -> None:
        """Handle network mode change"""
        self.networkMode = mode
        isLocal = mode == "local"
        if not isLocal:
            for i, player in enumerate(self.players):
                if i > 0:
                    player.setAI(False)
            for player in self.players:
                name = player.getDisplayName()
                if "[" in name:
                    name = name.split("[")[0].strip()
                player.name = name
        if mode == "host":
            hostValue = self.localIP
        elif isLocal:
            hostValue = None
        else:
            hostValue = settingsManager.get("HOST_IP", "0.0.0.0")
        self.hostIPField.setText(hostValue or "")
        self.hostIPField.setDisabled(isLocal)
        self.portField.setDisabled(isLocal)
        self.buildPlayerFields()
        
    def handleAIDifficultyChange(self, _selected=None):
        """Update all enabled AI player names to match the selected difficulty."""
        aiDifficulty = self.aiDifficulties[self.aiDifficultyDropdown.selectedIndex].upper()
        for player in self.players:
            if player.enabled and player.isAI:
                name = player.getDisplayName()
                if "[" in name:
                    name = name.split("[")[0].strip()
                player.name = f"{name} [{aiDifficulty}]"
        self.buildPlayerFields()
        
    def addPlayerField(self) -> None:
        """Add a new player"""
        enabledCount = self.getEnabledPlayersCount()
        if enabledCount >= 6:
            self.addToast(Toast("Maximum 6 players allowed", type="warning"))
            return
        for player in self.players:
            if not player.enabled:
                player.enabled = True
                break
        self.buildPlayerFields()
        
    def removePlayerField(self) -> None:
        """Remove a player"""
        enabledCount = self.getEnabledPlayersCount()
        if enabledCount <= 2:
            self.addToast(Toast("At least 2 players required", type="warning"))
            return
        for i in reversed(range(len(self.players))):
            if self.players[i].enabled:
                self.players[i].enabled = False
                if i < len(self.originalPlayerNames):
                    self.players[i].name = self.originalPlayerNames[i]
                else:
                    self.players[i].name = f"Player {i + 1}"
                self.players[i].isAI = False
                break
        self.buildPlayerFields()
        
    def applySettingsAndStart(self) -> None:
        """Apply settings and start the game"""
        playerNames = []
        for player in self.players:
            if player.enabled:
                playerNames.append(player.getDisplayName())
        settingsManager.set("PLAYERS", playerNames, temporary=True)
        settingsManager.set("NETWORK_MODE", self.networkModeDropdown.getSelected(), temporary=True)
        settingsManager.set("HOST_IP", self.hostIPField.getText(), temporary=True)
        if self.networkModeDropdown.getSelected() != "local":
            try:
                port = int(self.portField.getText())
                if not (1024 <= port <= 65535):
                    raise ValueError
                settingsManager.set("HOST_PORT", port, temporary=True)
            except ValueError:
                self.addToast(Toast("Invalid port number", type="error"))
                return
        networkMode = self.networkModeDropdown.getSelected()
        if networkMode == "local":
            self.switchScene("startGame", playerNames)
        else:
            self.switchScene("startLobby", playerNames)

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        """Handle all pygame events for the game preparation scene"""
        self.applyScroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)
            if self.aiDifficultyDropdown.handleEvent(event, yOffset=self.scrollOffset):
                continue
            if self.networkModeDropdown.handleEvent(event, yOffset=self.scrollOffset):
                continue
            self.hostIPField.handleEvent(event, yOffset=self.scrollOffset)
            self.portField.handleEvent(event, yOffset=self.scrollOffset)
            for nameField, aiCheckbox in self.playerFields:
                nameField.handleEvent(event, yOffset=self.scrollOffset)
                if aiCheckbox:
                    aiCheckbox.handleEvent(event, yOffset=self.scrollOffset)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.switchScene(GameState.MENU)
                elif self.startButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.applySettingsAndStart()
                elif self.addPlayerButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.addPlayerField()
                elif self.removePlayerButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    self.removePlayerField()
                    
    def draw(self) -> None:
        """Draw the game preparation scene UI."""
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        titleText = self.font.render("Game Setup", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY + offsetY))
        self.screen.blit(titleText, titleRect)
        labelFont = self.dropdownFont
        for i, (nameField, aiCheckbox) in enumerate(self.playerFields):
            labelText = "Your name:" if i == 0 else f"Player {i + 1}:"
            pLabel = labelFont.render(labelText, True, (255, 255, 255))
            pLabelRect = pLabel.get_rect(
                right=nameField.rect.left - 10,
                centery=nameField.rect.centery + offsetY
            )
            self.screen.blit(pLabel, pLabelRect)
            nameField.draw(self.screen, yOffset=offsetY)
            if aiCheckbox:
                aiCheckbox.draw(self.screen, yOffset=offsetY)
                aiLabel = labelFont.render("AI", True, (255, 255, 255))
                aiLabelRect = aiLabel.get_rect(
                    midleft=(aiCheckbox.rect.right + 8, aiCheckbox.rect.centery + offsetY)
                )
                self.screen.blit(aiLabel, aiLabelRect)
        ipLabel = labelFont.render("Host IP:", True, (255, 255, 255))
        ipLabelRect = ipLabel.get_rect(
            right=self.hostIPField.rect.left - 10,
            centery=self.hostIPField.rect.centery + offsetY
        )
        self.screen.blit(ipLabel, ipLabelRect)
        portLabel = labelFont.render("Port:", True, (255, 255, 255))
        portLabelRect = portLabel.get_rect(
            right=self.portField.rect.left - 10,
            centery=self.portField.rect.centery + offsetY
        )
        self.screen.blit(portLabel, portLabelRect)
        self.hostIPField.draw(self.screen, yOffset=offsetY)
        self.portField.draw(self.screen, yOffset=offsetY)
        self.addPlayerButton.draw(self.screen, yOffset=offsetY)
        self.removePlayerButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        self.startButton.draw(self.screen, yOffset=offsetY)
        netLabel = labelFont.render("Network mode:", True, (255, 255, 255))
        netLabelRect = netLabel.get_rect(
            right=self.networkModeDropdown.rect.left - 10,
            centery=self.networkModeDropdown.rect.centery + offsetY
        )
        self.screen.blit(netLabel, netLabelRect)
        self.networkModeDropdown.draw(self.screen, yOffset=offsetY)
        aiDiffLabel = labelFont.render("AI Difficulty:", True, (255, 255, 255))
        aiDiffLabelRect = aiDiffLabel.get_rect(
            right=self.aiDifficultyDropdown.rect.left - 10,
            centery=self.aiDifficultyDropdown.rect.centery + offsetY
        )
        self.screen.blit(aiDiffLabel, aiDiffLabelRect)
        self.aiDifficultyDropdown.draw(self.screen, yOffset=offsetY)
        self.toastManager.draw(self.screen)
        self.maxScroll = max(self.screen.get_height(), self.backButton.rect.bottom + 80)
        pygame.display.flip()
        
    def addToast(self, toast):
        """Add a toast notification to the scene"""
        self.toastManager.addToast(toast)