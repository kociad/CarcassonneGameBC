import pygame
from ui.scene import Scene
from ui.components.button import Button
from ui.components.toast import Toast, ToastManager
from gameState import GameState
from utils.settingsManager import settingsManager

class LobbyScene(Scene):
    def __init__(self, screen, switchSceneCallback, startGameCallback, getGameSession, network, gameLog):
        super().__init__(screen, switchSceneCallback)
        self.startGameCallback = startGameCallback
        self.getGameSession = getGameSession
        self.network = network
        self.gameLog = gameLog
        self.font = pygame.font.Font(None, 80)
        self.buttonFont = pygame.font.Font(None, 48)
        self.toastManager = ToastManager(maxToasts=5)
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30
        self.isHost = (getattr(self.network, 'networkMode', 'local') == 'host')
        self.networkMode = getattr(self.network, 'networkMode', 'local')
        self.startButton = Button("Start Game", (screen.get_width() // 2 - 100, screen.get_height() - 120, 200, 60), self.buttonFont)
        self.waitingForHost = False
        self.originalPlayerNames = settingsManager.get("PLAYERS", [])
        # If local mode, skip lobby
        if self.networkMode == "local":
            self.switchScene(GameState.GAME)
            return
        self.updatePlayerStatus()

    def updatePlayerStatus(self):
        session = self.getGameSession()
        self.players = session.getPlayers() if session else []
        # Build status for each original player slot
        self.statusList = []
        for i, orig_name in enumerate(self.originalPlayerNames):
            # Find player by index
            player = next((p for p in self.players if p.getIndex() == i), None)
            if player is not None and player.getIsAI():
                # AI always connected
                status = "AI"
                color = (120, 120, 120)
                name = player.getName()
            elif player is not None and player.isHuman:
                status = "Connected"
                color = (0, 200, 0)
                name = player.getName()
            else:
                status = "Waiting..."
                color = (200, 200, 0)
                name = orig_name
            self.statusList.append({"name": name, "status": status, "color": color})
        # Host: count all human players, check if all are connected
        self.requiredHumans = sum(1 for s in self.statusList if s["status"] != "AI")
        self.connectedHumans = sum(1 for s in self.statusList if s["status"] == "Connected")
        self.allConnected = (self.connectedHumans == self.requiredHumans)
        self.startButton.setDisabled(not (self.isHost and self.allConnected))

    def handleEvents(self, events):
        self.applyScroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.isHost and self.startButton.isClicked(event.pos, yOffset=self.scrollOffset):
                    if self.allConnected:
                        self.startGameCallback([p.getName() for p in self.players])
                    else:
                        self.toastManager.addToast(Toast("Not all players are connected!", type="warning"))
        self.updatePlayerStatus()

    def update(self):
        self.updatePlayerStatus()

    def draw(self):
        # Use dark gray background matching other menu scenes
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        titleText = self.font.render("Lobby", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2, 60 + offsetY))
        self.screen.blit(titleText, titleRect)
        labelFont = pygame.font.Font(None, 48)
        y = 160 + offsetY
        dot_radius = 16
        if self.isHost:
            for i, status in enumerate(self.statusList):
                name = status["name"]
                stat = status["status"]
                color = status["color"]
                # Draw status dot
                dot_x = self.screen.get_width() // 2 - 220
                dot_y = y + 24
                pygame.draw.circle(self.screen, color, (dot_x, dot_y), dot_radius)
                # Draw name
                nameSurf = labelFont.render(f"{name}", True, (255, 255, 255))
                self.screen.blit(nameSurf, (self.screen.get_width() // 2 - 180, y))
                # Draw status text
                statusSurf = labelFont.render(stat, True, color)
                self.screen.blit(statusSurf, (self.screen.get_width() // 2 + 100, y))
                y += 60
            self.startButton.draw(self.screen, yOffset=offsetY)
        else:
            waitFont = pygame.font.Font(None, 36)
            waitText = waitFont.render("Waiting for host to start the game...", True, (255, 255, 255))
            waitRect = waitText.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 40 + offsetY))
            self.screen.blit(waitText, waitRect)
        self.toastManager.draw(self.screen)
        if self.gameLog:
            self.gameLog.draw(self.screen)
        pygame.display.flip() 