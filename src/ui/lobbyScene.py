import pygame
from ui.scene import Scene
from ui.components.button import Button
from ui.components.toast import Toast, ToastManager
from gameState import GameState
from utils.settingsManager import settingsManager
import typing


class LobbyScene(Scene):
    """Scene for the game lobby, where players wait for all participants to connect before starting the game."""

    def __init__(self, screen: pygame.Surface,
                 switchSceneCallback: typing.Callable,
                 startGameCallback: typing.Callable,
                 getGameSession: typing.Callable, network: typing.Any,
                 gameLog: typing.Any) -> None:
        """Initialize the lobby scene with UI components and network state."""
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
        self.startButton = Button((screen.get_width() // 2 - 100,
                                   screen.get_height() - 120, 200, 60),
                                  "Start Game", self.buttonFont)
        self.waitingForHost = False
        self.originalPlayerNames = settingsManager.get("PLAYERS", [])
        if self.networkMode == "local":
            self.switchScene(GameState.GAME)
            return
        self.updatePlayerStatus()

    def updatePlayerStatus(self):
        """Update the connection status of all players in the lobby."""
        session = self.getGameSession()
        self.players = session.getPlayers() if session else []
        self.statusList = []
        for i, origName in enumerate(self.originalPlayerNames):
            player = next((p for p in self.players if p.getIndex() == i), None)
            if player is not None and player.getIsAI():
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
                name = origName
            self.statusList.append({
                "name": name,
                "status": status,
                "color": color
            })
        self.requiredHumans = sum(1 for s in self.statusList
                                  if s["status"] != "AI")
        self.connectedHumans = sum(1 for s in self.statusList
                                   if s["status"] == "Connected")
        self.allConnected = (self.connectedHumans == self.requiredHumans)
        self.startButton.setDisabled(not (self.isHost and self.allConnected))

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        """Handle user and network events in the lobby scene."""
        self.applyScroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switchScene(GameState.MENU)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.isHost and self.startButton.isClicked(
                        event.pos, yOffset=self.scrollOffset):
                    if self.allConnected:
                        session = self.getGameSession()
                        if hasattr(session, 'lobbyCompleted'):
                            session.lobbyCompleted = True
                        self.startGameCallback(
                            [p.getName() for p in self.players])
                    else:
                        self.toastManager.addToast(
                            Toast("Not all players are connected!",
                                  type="warning"))
        self.updatePlayerStatus()

    def update(self):
        """Update the lobby scene state."""
        self.updatePlayerStatus()

    def draw(self) -> None:
        """Draw the lobby scene, including player statuses and the start button."""
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        titleText = self.font.render("Lobby", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2,
                                               60 + offsetY))
        self.screen.blit(titleText, titleRect)
        labelFont = pygame.font.Font(None, 48)
        y = 160 + offsetY
        if self.isHost:
            for i, status in enumerate(self.statusList):
                name = status["name"]
                stat = status["status"]
                color = status["color"]
                nameSurf = labelFont.render(f"{name}", True, (255, 255, 255))
                statusSurf = labelFont.render(stat, True, color)
                spacing = 32
                totalWidth = nameSurf.get_width(
                ) + spacing + statusSurf.get_width()
                startX = (self.screen.get_width() - totalWidth) // 2
                self.screen.blit(nameSurf, (startX, y))
                self.screen.blit(statusSurf,
                                 (startX + nameSurf.get_width() + spacing, y))
                y += 60
            self.startButton.draw(self.screen, yOffset=offsetY)
        else:
            waitFont = pygame.font.Font(None, 36)
            waitText = waitFont.render("Waiting for host to start the game...",
                                       True, (255, 255, 255))
            waitRect = waitText.get_rect(
                center=(self.screen.get_width() // 2,
                        self.screen.get_height() // 2 + 40 + offsetY))
            self.screen.blit(waitText, waitRect)
        self.toastManager.draw(self.screen)
        if self.gameLog:
            self.gameLog.draw(self.screen)
        pygame.display.flip()
