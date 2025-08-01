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

FORBIDDEN_WORDS = [
    "ai",
    "easy",
    "normal", 
    "hard",
    "expert"
]

def getLocalIP():
    """
    Get the local IP address using multiple methods.
    Falls back to default IP from settings if all methods fail.
    """
    defaultIP = settingsManager.get("HOST_IP", "0.0.0.0")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localIP = s.getsockname()[0]
        s.close()
        return localIP
    except Exception:
        pass
    
    try:
        hostname = socket.gethostname()
        localIP = socket.gethostbyname(hostname)
        if localIP != "127.0.0.1" and not localIP.startswith("127."):
            return localIP
    except Exception:
        pass
    
    try:
        for interface in socket.getaddrinfo(socket.gethostname(), None):
            ip = interface[4][0]
            if ip != "127.0.0.1" and not ip.startswith("127."):
                return ip
    except Exception:
        pass
    
    return defaultIP

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
            if self.name.startswith("AI_EASY_"):
                self.name = self.name[8:]
            elif self.name.startswith("AI_HARD_"):
                self.name = self.name[8:]
            elif self.name.startswith("AI_EXPERT_"):
                self.name = self.name[10:]
            elif self.name.startswith("AI_NORMAL_"):
                self.name = self.name[10:]
            elif self.name.startswith("AI_"):
                self.name = self.name[3:]
            
    def getDisplayName(self):
        """Get name for display purposes"""
        return self.name
        
    def copy(self):
        """Create a copy of this configuration"""
        return PlayerConfiguration(self.name, self.isAI, self.enabled)

class GamePrepareScene(Scene):
    def __init__(self, screen: pygame.Surface, switchSceneCallback: typing.Callable) -> None:
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
        self.localIP = getLocalIP()
        self.networkMode = networkMode

        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 60
        
        self.playerLabelY = currentY
        currentY += 50
        
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
        currentY += (6 * 50) + 20 + 80

        self.gameLabelY = currentY
        currentY += 50

        self.aiDifficultyDropdown = Dropdown(
            rect=(xCenter, currentY, 200, 40),
            font=self.dropdownFont,
            options=["EASY", "NORMAL", "HARD", "EXPERT"],
            defaultIndex=1,
            onSelect=self.handleAIDifficultyChange
        )
        currentY += 80

        self.cardSetLabelY = currentY
        currentY += 50

        from models.cardSets.setLoader import getAvailableCardSets
        self.availableCardSets = getAvailableCardSets()
        self.selectedCardSets = ['baseGame']
        self.cardSetCheckboxes = []
        self.cardSetSectionY = currentY
        
        sortedCardSets = sorted(self.availableCardSets, key=lambda x: (x['name'] != 'baseGame', x['name']))
        
        for cardSet in sortedCardSets:
            isBaseGame = cardSet['name'] == 'baseGame'
            checkbox = Checkbox(
                rect=(xCenter, 0, 20, 20),
                checked=isBaseGame,
                onToggle=lambda checked, name=cardSet['name']: self.toggleCardSet(name, checked)
            )
            if isBaseGame:
                checkbox.setDisabled(True)
            self.cardSetCheckboxes.append((cardSet, checkbox))
        
        cardSetCount = len(self.availableCardSets)
        currentY += 30 * cardSetCount + 80

        self.networkLabelY = currentY
        currentY += 50

        self.hostIPField = InputField(
            rect=(xCenter, currentY + 20, 200, 40),
            font=self.inputFont
        )
        self.hostIPField.setText(hostIP)
        currentY += 80

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
        self.playerFields = []

        for i, player in enumerate(self.players):
            y = self.playerListY + (i * 50 if i == 0 else 60 + (i - 1) * 50)

            def makeTextChangeHandler(index):
                def handler(newText):
                    lowered = newText.lower()
                    forbidden_found = None
                    for word in FORBIDDEN_WORDS:
                        if word in lowered:
                            forbidden_found = word
                            break
                    if forbidden_found:
                        if index < len(self.originalPlayerNames):
                            default_name = self.originalPlayerNames[index]
                        else:
                            default_name = f"Player {index + 1}"
                        self.players[index].setName(default_name)
                        if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                            nameField = self.playerFields[index][0]
                            nameField.setText(default_name)
                        self.addToast(Toast(f"Forbidden word detected in name. Reset to default.", type="error"))
                        if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                            aiCheckbox = self.playerFields[index][1]
                            if aiCheckbox:
                                aiCheckbox.setChecked(self.players[index].isAI)
                        return
                    self.players[index].setName(newText)
                    if hasattr(self, 'playerFields') and len(self.playerFields) > index:
                        aiCheckbox = self.playerFields[index][1]
                        if aiCheckbox:
                            aiCheckbox.setChecked(self.players[index].isAI)
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
                nameField.setText(player.getDisplayName())
                nameField.setDisabled(not player.enabled)
                if i > 0 and self.networkMode == "host":
                    nameField.setReadOnly(True)

            aiCheckbox = None
            
            if i == 0:
                canToggleAI = settingsManager.get("DEBUG", False)
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
            
    def togglePlayerAI(self, index: int, value: bool) -> None:
        """Toggle AI status for a player"""
        self.players[index].setAI(value)
        
        nameField = self.playerFields[index][0]
        nameField.setText(self.players[index].getDisplayName())
        
        player = self.players[index]
        if value:
            currentDifficulty = self.aiDifficultyDropdown.getSelected()
            baseName = player.name
            if baseName.startswith("AI_EASY_"):
                baseName = baseName[8:]
            elif baseName.startswith("AI_HARD_"):
                baseName = baseName[8:]
            elif baseName.startswith("AI_EXPERT_"):
                baseName = baseName[10:]
            elif baseName.startswith("AI_NORMAL_"):
                baseName = baseName[10:]
            elif baseName.startswith("AI_"):
                baseName = baseName[3:]
            
            player.name = f"AI_{currentDifficulty}_{baseName}"
            nameField.setText(player.getDisplayName())
        
    def handleAIDifficultyChange(self, difficulty: str) -> None:
        """Handle AI difficulty change for all AI players"""
        for i, player in enumerate(self.players):
            if player.isAI:
                baseName = player.name
                if baseName.startswith("AI_EASY_"):
                    baseName = baseName[8:]
                elif baseName.startswith("AI_HARD_"):
                    baseName = baseName[8:]
                elif baseName.startswith("AI_EXPERT_"):
                    baseName = baseName[10:]
                elif baseName.startswith("AI_NORMAL_"):
                    baseName = baseName[10:]
                elif baseName.startswith("AI_"):
                    baseName = baseName[3:]
                
                player.name = f"AI_{difficulty}_{baseName}"
                
                if i < len(self.playerFields):
                    nameField = self.playerFields[i][0]
                    nameField.setText(player.getDisplayName())
        
    def handleNetworkModeChange(self, mode: str) -> None:
        """Handle network mode change"""
        self.networkMode = mode
        isLocal = mode == "local"

        if not isLocal:
            for i, player in enumerate(self.players):
                if i > 0:
                    baseName = player.name
                    if baseName.startswith("AI_EASY_"):
                        baseName = baseName[8:]
                    elif baseName.startswith("AI_HARD_"):
                        baseName = baseName[8:]
                    elif baseName.startswith("AI_EXPERT_"):
                        baseName = baseName[10:]
                    elif baseName.startswith("AI_NORMAL_"):
                        baseName = baseName[10:]
                    elif baseName.startswith("AI_"):
                        baseName = baseName[3:]
                    
                    player.name = baseName
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
        
        self.aiDifficultyDropdown.setDisabled(not isLocal)
        
        isClient = mode == "client"
        for cardSet, checkbox in self.cardSetCheckboxes:
            if cardSet['name'] != 'baseGame':
                checkbox.setDisabled(isClient)
        
        self.buildPlayerFields()
        
    def toggleCardSet(self, setName: str, checked: bool) -> None:
        """Handle card set selection toggle"""
        if checked and setName not in self.selectedCardSets:
            self.selectedCardSets.append(setName)
        elif not checked and setName in self.selectedCardSets:
            self.selectedCardSets.remove(setName)
        
        # Store selected card sets in settings
        settingsManager.set("SELECTED_CARD_SETS", self.selectedCardSets)
        
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
        
        selectedCardSets = []
        for cardSet, checkbox in self.cardSetCheckboxes:
            if checkbox.isChecked():
                selectedCardSets.append(cardSet['name'])
        settingsManager.set("SELECTED_CARD_SETS", selectedCardSets, temporary=True)
        
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

            if self.aiDifficultyDropdown.handleEvent(event, yOffset=self.scrollOffset):
                continue

            self.hostIPField.handleEvent(event, yOffset=self.scrollOffset)
            self.portField.handleEvent(event, yOffset=self.scrollOffset)

            for cardSet, checkbox in self.cardSetCheckboxes:
                if checkbox.handleEvent(event, yOffset=0):
                    continue

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
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset

        titleText = self.font.render("Game Setup", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY + offsetY))
        self.screen.blit(titleText, titleRect)

        playerLabel = self.dropdownFont.render("Player Settings", True, (255, 215, 0))
        playerLabelRect = playerLabel.get_rect()
        playerLabelRect.centerx = self.screen.get_width() // 2
        playerLabelRect.y = self.playerLabelY + offsetY
        self.screen.blit(playerLabel, playerLabelRect)

        gameLabel = self.dropdownFont.render("Game Settings", True, (255, 215, 0))
        gameLabelRect = gameLabel.get_rect()
        gameLabelRect.centerx = self.screen.get_width() // 2
        gameLabelRect.y = self.gameLabelY + offsetY
        self.screen.blit(gameLabel, gameLabelRect)

        cardSetLabel = self.dropdownFont.render("Card Sets", True, (255, 215, 0))
        cardSetLabelRect = cardSetLabel.get_rect()
        cardSetLabelRect.centerx = self.screen.get_width() // 2
        cardSetLabelRect.y = self.cardSetLabelY + offsetY
        self.screen.blit(cardSetLabel, cardSetLabelRect)

        networkLabel = self.dropdownFont.render("Network Settings", True, (255, 215, 0))
        networkLabelRect = networkLabel.get_rect()
        networkLabelRect.centerx = self.screen.get_width() // 2
        networkLabelRect.y = self.networkLabelY + offsetY
        self.screen.blit(networkLabel, networkLabelRect)

        labelFont = self.dropdownFont

        for i, (nameField, aiCheckbox) in enumerate(self.playerFields):
            labelText = "Your name:" if i == 0 else f"Player {i + 1}:"
            label = labelFont.render(labelText, True, (255, 255, 255))
            labelRect = label.get_rect(
                right=nameField.rect.left - 10,
                centery=nameField.rect.centery + offsetY
            )
            self.screen.blit(label, labelRect)
            nameField.draw(self.screen, yOffset=offsetY)
            aiCheckbox.draw(self.screen, yOffset=offsetY)

        netLabel = labelFont.render("Network mode:", True, (255, 255, 255))
        netLabelRect = netLabel.get_rect(
            right=self.networkModeDropdown.rect.left - 10,
            centery=self.networkModeDropdown.rect.centery + offsetY
        )
        self.screen.blit(netLabel, netLabelRect)

        aiLabel = labelFont.render("AI Difficulty:", True, (255, 255, 255))
        aiLabelRect = aiLabel.get_rect(
            right=self.aiDifficultyDropdown.rect.left - 10,
            centery=self.aiDifficultyDropdown.rect.centery + offsetY
        )
        self.screen.blit(aiLabel, aiLabelRect)

        for i, (cardSet, checkbox) in enumerate(self.cardSetCheckboxes):
            y = self.cardSetSectionY + 20 + i * 30 + offsetY
            checkbox.rect.x = self.aiDifficultyDropdown.rect.x
            checkbox.rect.y = y - 10
            checkbox.draw(self.screen, yOffset=0)
            cardSetText = labelFont.render(f"{cardSet['displayName']} ({cardSet['cardCount']} cards):", True, (255, 255, 255))
            cardSetRect = cardSetText.get_rect(
                right=checkbox.rect.left - 10,
                centery=checkbox.rect.centery
            )
            self.screen.blit(cardSetText, cardSetRect)

        ipLabel = labelFont.render("Host IP:", True, (255, 255, 255))
        ipLabelRect = ipLabel.get_rect(
            right=self.hostIPField.rect.left - 10,
            centery=self.hostIPField.rect.centery + offsetY
        )
        self.screen.blit(ipLabel, ipLabelRect)
        self.hostIPField.draw(self.screen, yOffset=offsetY)

        portLabel = labelFont.render("Port:", True, (255, 255, 255))
        portLabelRect = portLabel.get_rect(
            right=self.portField.rect.left - 10,
            centery=self.portField.rect.centery + offsetY
        )
        self.screen.blit(portLabel, portLabelRect)
        self.portField.draw(self.screen, yOffset=offsetY)

        self.aiDifficultyDropdown.draw(self.screen, yOffset=offsetY)
        self.networkModeDropdown.draw(self.screen, yOffset=offsetY)
        self.addPlayerButton.draw(self.screen, yOffset=offsetY)
        self.removePlayerButton.draw(self.screen, yOffset=offsetY)
        self.backButton.draw(self.screen, yOffset=offsetY)
        self.startButton.draw(self.screen, yOffset=offsetY)
        
        self.maxScroll = max(self.screen.get_height(), self.backButton.rect.bottom + 80)
        
        self.toastManager.draw(self.screen)
        
        pygame.display.flip()
        
    def addToast(self, toast):
        self.toastManager.addToast(toast)