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
    def __init__(self, screen, switchSceneCallback):
        super().__init__(screen, switchSceneCallback)
        
        # Reload settings from file to get clean state (clear runtime overrides from previous game)
        settingsManager.reloadFromFile()
        
        self.switchSceneCallback = switchSceneCallback
        
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        
        #self.toastQueue = []
        #self.activeToast = None
        self.toastManager = ToastManager(maxToasts=5)
        
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

        # Store original default player names
        self.originalPlayerNames = settingsManager.get("PLAYERS", []).copy()
        
        # SINGLE SOURCE OF TRUTH - all player data lives here
        self.players = []
        for i in range(6):
            if i < len(self.originalPlayerNames):
                name = self.originalPlayerNames[i]
            else:
                name = f"Player {i + 1}"
            
            enabled = i < 2  # Start with 2 players enabled
            self.players.append(PlayerConfiguration(name, False, enabled))
        
        # Network settings
        networkMode = settingsManager.get("NETWORK_MODE", "local")
        hostIP = settingsManager.get("HOST_IP", "0.0.0.0")
        port = str(settingsManager.get("HOST_PORT", 222))
        self.localIP = socket.gethostbyname(socket.gethostname())
        self.networkMode = networkMode

        # Layout anchor
        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 80
        
        # Initialize buttons
        self.addPlayerButton = Button("+", (self.screen.get_width() // 2 + 180, currentY + 60, 40, 40), self.buttonFont)
        self.removePlayerButton = Button("−", (self.screen.get_width() // 2 + 230, currentY + 60, 40, 40), self.buttonFont)

        self.playerListY = currentY

        # Network dropdown
        self.networkModes = ["local", "host", "client"]
        defaultIndex = self.networkModes.index(networkMode)
        self.networkModeDropdown = Dropdown(
            rect=(xCenter, currentY + (6 * 50) + 20, 200, 40),
            font=self.dropdownFont,
            options=self.networkModes,
            defaultIndex=defaultIndex,
            onSelect=self.handleNetworkModeChange
        )

        self.buildPlayerFields()
        currentY += (6 * 50) + 20 + 60

        # Host IP
        self.hostIPField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont
        )
        self.hostIPField.setText(hostIP)
        currentY += 60

        # Port
        self.portField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont
        )
        self.portField.setText(port)
        currentY += 80

        # Start and Back buttons
        self.startButton = Button("Start Game", (xCenter, currentY, 200, 60), self.buttonFont)
        currentY += 80
        self.backButton = Button("Back", (xCenter, currentY, 200, 60), self.buttonFont)
        
        # Initial state
        self.handleNetworkModeChange(networkMode)
        
    def getEnabledPlayersCount(self):
        """Get count of enabled players"""
        return sum(1 for player in self.players if player.enabled)
        
    def buildPlayerFields(self):
        """Build UI fields based on current player data (single source of truth)"""
        self.playerFields = []

        for i, player in enumerate(self.players):
            y = self.playerListY + (i * 50 if i == 0 else 60 + (i - 1) * 50)

            # Create text change handler that updates our single source of truth
            def makeTextChangeHandler(index):
                def handler(newText):
                    # Update the single source of truth
                    self.players[index].setName(newText)
                    # Update AI checkbox if needed
                    if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                        aiCheckbox = self.playerFields[index][1]
                        if aiCheckbox:
                            aiCheckbox.setChecked(self.players[index].isAI)
                return handler

            # Create input field and set its value from our single source of truth
            nameField = InputField(
                rect=(self.screen.get_width() // 2 - 100, y, 200, 40),
                font=self.inputFont,
                onTextChange=makeTextChangeHandler(i)
            )
            
            # Set field state based on network mode and player configuration
            if self.networkMode == "client" and i > 0:
                nameField.setText("")
                nameField.setDisabled(True)
            else:
                nameField.setText(player.getDisplayName())
                nameField.setDisabled(not player.enabled)
                if i > 0 and self.networkMode == "host":
                    nameField.setReadOnly(True)

            # AI checkbox logic
            aiCheckbox = None
            if i != 0:  # First player is never AI
                canToggleAI = (self.networkMode == "local")
                aiCheckbox = Checkbox(
                    rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                    checked=player.isAI,
                    onToggle=(lambda value, index=i: self.togglePlayerAI(index, value)) if canToggleAI else None
                )
                aiCheckbox.setDisabled(not player.enabled or not canToggleAI)

            self.playerFields.append((nameField, aiCheckbox))
            
    def togglePlayerAI(self, index, value):
        """Toggle AI status for a player"""
        # Update single source of truth
        self.players[index].setAI(value)
        
        # Update UI to reflect the change
        nameField = self.playerFields[index][0]
        nameField.setText(self.players[index].getDisplayName())
        
    def handleNetworkModeChange(self, mode):
        """Handle network mode change"""
        self.networkMode = mode
        isLocal = mode == "local"

        # Clear AI settings for non-local modes (network players are human)
        if not isLocal:
            for i, player in enumerate(self.players):
                if i > 0:  # Skip first player (always human)
                    player.setAI(False)

        if mode == "host":
            hostValue = self.localIP
        elif isLocal:
            hostValue = None
        else:
            hostValue = settingsManager.get("HOST_IP", "0.0.0.0")

        self.hostIPField.setText(hostValue or "")
        self.hostIPField.setDisabled(isLocal)
        self.portField.setDisabled(isLocal)
        
        # Rebuild UI based on new mode
        self.buildPlayerFields()
        
    def addPlayerField(self):
        """Add a new player"""
        enabledCount = self.getEnabledPlayersCount()
        if enabledCount >= 6:
            self.addToast(Toast("Maximum 6 players allowed", type="warning"))
            return

        # Find first disabled player and enable them
        for player in self.players:
            if not player.enabled:
                player.enabled = True
                break
                
        self.buildPlayerFields()
        
    def removePlayerField(self):
        """Remove a player"""
        enabledCount = self.getEnabledPlayersCount()
        if enabledCount <= 2:
            self.addToast(Toast("At least 2 players required", type="warning"))
            return
            
        # Find last enabled player and disable them
        for i in reversed(range(len(self.players))):
            if self.players[i].enabled:
                self.players[i].enabled = False
                # Reset to default name when disabled
                if i < len(self.originalPlayerNames):
                    self.players[i].name = self.originalPlayerNames[i]
                else:
                    self.players[i].name = f"Player {i + 1}"
                self.players[i].isAI = False
                break
                
        self.buildPlayerFields()
        
    def applySettingsAndStart(self):
        """Apply settings and start the game"""
        # Get enabled player names from our single source of truth
        playerNames = []
        for player in self.players:
            if player.enabled:
                playerNames.append(player.getDisplayName())
        # Update settings using SettingsManager
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
        # Dynamically choose the correct callback based on current network mode
        networkMode = self.networkModeDropdown.getSelected()
        if networkMode == "local":
            self.switchScene("startGame", playerNames)
        else:
            self.switchScene("startLobby", playerNames)

    def handleEvents(self, events):
        self.applyScroll(events)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)

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
                    
    def draw(self):
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset

        titleText = self.font.render("Game Setup", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY + offsetY))
        self.screen.blit(titleText, titleRect)

        labelFont = self.dropdownFont

        netLabel = labelFont.render("Network mode:", True, (255, 255, 255))
        netLabelRect = netLabel.get_rect(
            right=self.networkModeDropdown.rect.left - 10,
            centery=self.networkModeDropdown.rect.centery + offsetY
        )
        self.screen.blit(netLabel, netLabelRect)

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

        self.hostIPField.draw(self.screen, yOffset=offsetY)
        self.portField.draw(self.screen, yOffset=offsetY)
        self.addPlayerButton.draw(self.screen, yOffset=offsetY)
        self.removePlayerButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        self.startButton.draw(self.screen, yOffset=offsetY)
        self.networkModeDropdown.draw(self.screen, yOffset=offsetY)

        self.maxScroll = max(self.screen.get_height(), self.backButton.rect.bottom + 80)
        
        self.toastManager.draw(self.screen)
        
        pygame.display.flip()
        
    def addToast(self, toast):
        self.toastManager.addToast(toast)