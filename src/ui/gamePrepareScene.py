import pygame
import socket
from ui.scene import Scene
from ui.components.button import Button
from ui.components.inputField import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast
from ui.components.checkbox import Checkbox
from gameState import GameState
import settings

class GamePrepareScene(Scene):
    def __init__(self, screen, switchSceneCallback, startGameCallback):
        super().__init__(screen, switchSceneCallback)
        self.startGameCallback = startGameCallback
        
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        self.toastQueue = []
        self.activeToast = None
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

        # Fetch settings (session default)
        #playerName = settings.PLAYER
        playerNames = settings.PLAYERS
        networkMode = settings.NETWORK_MODE
        hostIP = settings.HOST_IP
        port = str(settings.HOST_PORT)
        self.localIP = socket.gethostbyname(socket.gethostname())
        self.networkMode = networkMode
        
        self.enabledPlayers = 2

        # Layout anchor
        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 80

        """
        # Player name
        self.playerNameField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont
        )
        self.playerNameField.setText(playerName)
        self.playerNameY = currentY
        currentY += 60
        """
        
        # Initialize buttons after player field creation
        self.addPlayerButton = Button("+", (self.screen.get_width() // 2 + 180, currentY + 60, 40, 40), self.buttonFont)
        self.removePlayerButton = Button("−", (self.screen.get_width() // 2 + 230, currentY + 60, 40, 40), self.buttonFont)

        # Player list
        self.players = [("", False) for _ in range(6)]
        for i in range(self.enabledPlayers):
            if i < len(settings.PLAYERS):
                self.players[i] = (settings.PLAYERS[i], False)
                
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

        self.rebuildPlayerFields()
        currentY += (6 * 50) + 20 + 60
        
        """
        self.networkModeDropdown = Dropdown(
            rect=(xCenter, currentY, 200, 40),
            font=self.dropdownFont,
            options=self.networkModes,
            defaultIndex=defaultIndex,
            onSelect=self.handleNetworkModeChange
        )
        currentY += 60
        """

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

        if not self.activeToast and self.toastQueue:
            self.activeToast = self.toastQueue.pop(0)
            self.activeToast.start()
        if self.activeToast:
            self.activeToast.draw(self.screen)

        self.maxScroll = max(self.screen.get_height(), self.backButton.rect.bottom + 80)
        pygame.display.flip()
        
    def rebuildPlayerFields(self):
        self.playerFields = []
        mode = self.networkMode

        for i in range(6):
            y = self.playerListY + (i * 50 if i == 0 else 60 + (i - 1) * 50)

            # Default name only for active players
            if i < self.enabledPlayers:
                defaultName = settings.PLAYERS[i] if i < len(settings.PLAYERS) else f"Player {i + 1}"
            else:
                defaultName = ""

            # onTextChange handler for AI prefix removal
            def makeTextChangeHandler(index):
                def handler(newText):
                    aiCheckbox = self.playerFields[index][1]
                    if aiCheckbox and aiCheckbox.isChecked() and not newText.startswith("AI_"):
                        aiCheckbox.setChecked(False)
                        self.players[index] = (newText, False)
                return handler

            nameField = InputField(
                rect=(self.screen.get_width() // 2 - 100, y, 200, 40),
                font=self.inputFont,
                onTextChange=makeTextChangeHandler(i)
            )
            nameField.setText("" if (mode == "client" and i > 0) else defaultName)

            # Enable logic
            if i >= self.enabledPlayers or (mode == "client" and i > 0):
                nameField.setDisabled(True)
            elif i == 0:
                nameField.setDisabled(False)  # always editable
            elif mode == "host":
                nameField.setDisabled(False)
                nameField.setReadOnly(True)  # visually enabled but not editable
            else:
                nameField.setDisabled(False)

            # AI checkbox logic
            aiCheckbox = None
            if i != 0:
                canToggleAI = (mode == "local")
                aiCheckbox = Checkbox(
                    rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                    checked=self.players[i][1],
                    onToggle=(lambda value, index=i: self.toggleAI(index, value)) if canToggleAI else None
                )
                aiCheckbox.setDisabled(i >= self.enabledPlayers or not canToggleAI)

            self.playerFields.append((nameField, aiCheckbox))
            
    def toggleAI(self, index, value):
        name = self.playerFields[index][0].getText()

        if value and not name.startswith("AI_"):
            name = f"AI_{name}"
        elif not value and name.startswith("AI_"):
            name = name[3:]

        self.players[index] = (name, value)
        self.playerFields[index][0].setText(name)
        
    def handleNetworkModeChange(self, mode):
        self.networkMode = mode
        isLocal = mode == "local"

        if mode == "host":
            hostValue = self.localIP
            for i in range(self.enabledPlayers):
                if i < len(settings.PLAYERS):
                    self.players[i] = (settings.PLAYERS[i], False)
                else:
                    self.players[i] = (f"Player {i + 1}", False)
            self.rebuildPlayerFields()

        elif isLocal:
            hostValue = None
        else:
            hostValue = settings.HOST_IP

        self.hostIPField.setText(hostValue or "")
        self.hostIPField.setDisabled(isLocal)
        self.portField.setDisabled(isLocal)

        if mode != "host":
            self.rebuildPlayerFields()
        
    def applySettingsAndStart(self):
        #settings.PLAYER = self.playerNameField.getText()
        settings.PLAYERS = [field.getText() for field, _ in self.playerFields[:self.enabledPlayers]]
        #settings.PLAYER_INDEX = settings.PLAYERS.index(settings.PLAYER)
        settings.NETWORK_MODE = self.networkModeDropdown.getSelected()
        settings.HOST_IP = self.hostIPField.getText()

        if self.networkModeDropdown.getSelected() != "local":
            try:
                port = int(self.portField.getText())
                if not (1024 <= port <= 65535):
                    raise ValueError
                settings.HOST_PORT = port
            except ValueError:
                self.addToast(Toast("Invalid port number", type="error"))
        self.startGameCallback(settings.PLAYERS)
                
    def addPlayerField(self):
        if self.enabledPlayers >= 6:
            self.addToast(Toast("Maximum 6 players allowed", type="warning"))
            return

        index = self.enabledPlayers

        # Prefill name from settings.PLAYERS if available
        if index < len(settings.PLAYERS):
            name = settings.PLAYERS[index]
        else:
            name = f"Player {index + 1}"

        self.players[index] = (name, False)
        self.enabledPlayers += 1
        self.rebuildPlayerFields()
        
    def removePlayerField(self):
        if self.enabledPlayers <= 2:
            self.addToast(Toast("At least 2 players required", type="warning"))
            return
        self.enabledPlayers -= 1
        self.players[self.enabledPlayers] = ("", False)
        self.rebuildPlayerFields()
        
    def addToast(self, toast):
        if self.activeToast and self.activeToast.message == toast.message:
            return
        if any(t.message == toast.message for t in self.toastQueue):
            return
        self.toastQueue.append(toast)
