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
    def __init__(self, screen, switchSceneCallback):
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.inputFont = pygame.font.Font(None, 36)
        self.dropdownFont = pygame.font.Font(None, 36)
        self.toastQueue = []
        self.activeToast = None

        # Fetch settings (session default)
        playerName = settings.PLAYER
        networkMode = settings.NETWORK_MODE
        hostIP = settings.HOST_IP
        port = str(settings.HOST_PORT)
        self.localIP = socket.gethostbyname(socket.gethostname())

        # Layout anchor
        xCenter = screen.get_width() // 2 - 100
        currentY = 60

        self.titleY = currentY
        currentY += 80

        # Player name
        self.playerNameField = InputField(
            rect=(xCenter, currentY, 200, 40),
            font=self.inputFont
        )
        self.playerNameField.setText(playerName)
        self.playerNameY = currentY
        currentY += 60

        # Player list
        self.players = [(playerName, False), ("Player 2", False)] + [("", False) for _ in range(4)]
        self.enabledPlayers = 2
        self.playerListY = currentY
        self.rebuildPlayerFields()
        currentY += (6 * 50) + 10
        
        # Initialize buttons after player field creation
        self.addPlayerButton = Button("+", (self.screen.get_width() // 2 + 170, self.playerNameY + 60, 40, 40), self.buttonFont)
        self.removePlayerButton = Button("−", (self.screen.get_width() // 2 + 220, self.playerNameY + 60, 40, 40), self.buttonFont)

        # Network dropdown
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
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            self.playerNameField.handleEvent(event)

            if self.playerFields:
                self.playerFields[0][0].setText(self.playerNameField.getText())
                self.players[0] = (self.playerNameField.getText(), self.players[0][1])
                
            self.networkModeDropdown.handleEvent(event)
            self.hostIPField.handleEvent(event)
            self.portField.handleEvent(event)

            for nameField, aiCheckbox in self.playerFields:
                nameField.handleEvent(event)
                aiCheckbox.handleEvent(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.isClicked(event.pos):
                    self.switchScene(GameState.MENU)
                elif self.startButton.isClicked(event.pos):
                    self.applySettingsAndStart()
                elif self.addPlayerButton.isClicked(event.pos):
                    self.addPlayerField()
                elif self.removePlayerButton.isClicked(event.pos):
                    self.removePlayerField()

    def draw(self):
        self.screen.fill((30, 30, 30))

        # Title
        titleText = self.font.render("Game Setup", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, self.titleY))
        self.screen.blit(titleText, titleRect)

        labelFont = self.dropdownFont

        # Labels
        labelFont = self.dropdownFont

        # Your Name label
        nameLabel = labelFont.render("Your name:", True, (255, 255, 255))
        nameLabelRect = nameLabel.get_rect(
            right=self.playerNameField.rect.left - 10,
            centery=self.playerNameField.rect.centery
        )
        self.screen.blit(nameLabel, nameLabelRect)

        # Network Mode label
        netLabel = labelFont.render("Network mode:", True, (255, 255, 255))
        netLabelRect = netLabel.get_rect(
            right=self.networkModeDropdown.rect.left - 10,
            centery=self.networkModeDropdown.rect.centery
        )
        self.screen.blit(netLabel, netLabelRect)

        # Host IP label
        ipLabel = labelFont.render("Host IP:", True, (255, 255, 255))
        ipLabelRect = ipLabel.get_rect(
            right=self.hostIPField.rect.left - 10,
            centery=self.hostIPField.rect.centery
        )
        self.screen.blit(ipLabel, ipLabelRect)

        # Port label
        portLabel = labelFont.render("Port:", True, (255, 255, 255))
        portLabelRect = portLabel.get_rect(
            right=self.portField.rect.left - 10,
            centery=self.portField.rect.centery
        )
        self.screen.blit(portLabel, portLabelRect)

        # Dynamically draw players
        btnY = None
        for i, (nameField, aiCheckbox) in enumerate(self.playerFields):
            pLabel = labelFont.render(f"Player {i + 1}:", True, (255, 255, 255))
            pLabelRect = pLabel.get_rect(
                right=nameField.rect.left - 10,
                centery=nameField.rect.centery
            )
            self.screen.blit(pLabel, pLabelRect)

            nameField.draw(self.screen)
            aiCheckbox.draw(self.screen)

            aiLabel = labelFont.render("AI", True, (255, 255, 255))
            aiLabelRect = aiLabel.get_rect(
                midleft=(aiCheckbox.rect.right + 8, aiCheckbox.rect.centery)
            )
            self.screen.blit(aiLabel, aiLabelRect)
            
        # Components
        self.playerNameField.draw(self.screen)
        self.hostIPField.draw(self.screen)
        self.portField.draw(self.screen)
        self.addPlayerButton.draw(self.screen)
        self.removePlayerButton.draw(self.screen)
        self.backButton.draw(self.screen)
        self.startButton.draw(self.screen)
        self.networkModeDropdown.draw(self.screen)

        # Toast queue
        if not self.activeToast and self.toastQueue:
            self.activeToast = self.toastQueue.pop(0)
            self.activeToast.start()

        if self.activeToast:
            self.activeToast.draw(self.screen)
            if self.activeToast.isExpired():
                self.activeToast = None

        pygame.display.flip()
        
    def rebuildPlayerFields(self):
        self.playerFields = []
        for i in range(6):
            y = self.playerListY + i * 50
            nameField = InputField(
                rect=(self.screen.get_width() // 2 - 100, y, 200, 40),
                font=self.inputFont
            )
            nameField.setText(self.players[i][0])
            nameField.setDisabled(i >= self.enabledPlayers)

            aiCheckbox = Checkbox(
                rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                checked=self.players[i][1],
                onToggle=lambda value, index=i: self.toggleAI(index, value)
            )
            aiCheckbox.setDisabled(i >= self.enabledPlayers)

            self.playerFields.append((nameField, aiCheckbox))
            
    def toggleAI(self, index, value):
        name, _ = self.players[index]
        if value and not name.startswith("AI_"):
            name = f"AI_{name}"
        elif not value and name.startswith("AI_"):
            name = name[3:]
        self.players[index] = (name, value)
        self.rebuildPlayerFields()

    def handleNetworkModeChange(self, mode):
        isLocal = mode == "local"
        self.hostIPField.setText(self.localIP if isLocal else settings.HOST_IP)
        self.hostIPField.setDisabled(isLocal)
        self.portField.setDisabled(isLocal)

    def applySettingsAndStart(self):
        settings.PLAYER = self.playerNameField.getText()
        settings.PLAYERS = [field.getText() for field, _ in self.playerFields[:self.enabledPlayers]]
        settings.PLAYER_INDEX = settings.PLAYERS.index(settings.PLAYER)
        settings.NETWORK_MODE = self.networkModeDropdown.getSelected()
        settings.HOST_IP = self.hostIPField.getText()

        try:
            port = int(self.portField.getText())
            if not (1024 <= port <= 65535):
                raise ValueError
            settings.HOST_PORT = port
            self.switchScene(GameState.GAME)
        except ValueError:
            self.addToast(Toast("Invalid port number", type="error"))

    def addPlayerField(self):
        if self.enabledPlayers >= 6:
            self.addToast(Toast("Maximum 6 players allowed", type="warning"))
            return
        index = self.enabledPlayers
        self.players[index] = (f"Player {index + 1}", False)
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
