import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from gameState import GameState
from utils.settingsManager import settingsManager
import logging
import typing

logger = logging.getLogger(__name__)


class MainMenuScene(Scene):
    """Scene for the main menu of the game."""

    def __init__(self, screen: pygame.Surface,
                 switchSceneCallback: typing.Callable,
                 getGameSession: typing.Callable,
                 cleanupPreviousGame: typing.Callable) -> None:
        super().__init__(screen, switchSceneCallback)
        self.font = pygame.font.Font(None, 100)
        self.buttonFont = pygame.font.Font(None, 48)
        self.dialogFont = pygame.font.Font(None, 36)
        self.getGameSession = getGameSession
        self.cleanupCallback = cleanupPreviousGame
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30
        self.showConfirmDialog = False
        centerX = screen.get_width() // 2 - 100
        centerY = screen.get_height() // 2
        self.continueButton = Button((centerX, centerY - 80, 200, 60),
                                     "Continue",
                                     self.buttonFont,
                                     None,
                                     disabled=(self.getGameSession() is None))
        self.startButton = Button((centerX, centerY, 200, 60), "New Game",
                                  self.buttonFont)
        self.howToPlayButton = Button((centerX, centerY + 80, 200, 60),
                                      "How to play", self.buttonFont)
        self.settingsButton = Button((centerX, centerY + 160, 200, 60),
                                     "Settings", self.buttonFont)
        self.quitButton = Button((centerX, centerY + 240, 200, 60), "Quit",
                                 self.buttonFont)
        dialogCenterX = screen.get_width() // 2
        dialogCenterY = screen.get_height() // 2
        self.confirmYesButton = Button(
            (dialogCenterX - 120, dialogCenterY + 40, 100, 40), "Yes",
            self.dialogFont)
        self.confirmNoButton = Button(
            (dialogCenterX + 20, dialogCenterY + 40, 100, 40), "No",
            self.dialogFont)

    def cleanupPreviousGame(self):
        """Clean up resources from previous game session."""
        try:
            logger.debug("Cleaning up previous game resources...")
            if hasattr(self, 'cleanupCallback') and self.cleanupCallback:
                self.cleanupCallback()
        except Exception as e:
            from utils.loggingConfig import logError
            logError("Error during previous game cleanup from menu", e)

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the main menu scene."""
        if self.showConfirmDialog:
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showConfirmDialog = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.confirmYesButton.isClicked(event.pos):
                        self.showConfirmDialog = False
                        logger.info(
                            "Starting new game - cleaning up previous session")
                        self.cleanupPreviousGame()
                        self.switchScene(GameState.PREPARE)
                    elif self.confirmNoButton.isClicked(event.pos):
                        self.showConfirmDialog = False
            return
        self.applyScroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.continueButton.isClicked(
                        event.pos, yOffset=self.scrollOffset
                ) and not self.continueButton.disabled:
                    session = self.getGameSession()
                    networkMode = getattr(session, 'networkMode', 'local')
                    if hasattr(session, 'lobbyCompleted') and networkMode in (
                            "host", "client") and not session.lobbyCompleted:
                        self.switchScene(GameState.LOBBY)
                    else:
                        self.switchScene(GameState.GAME)
                elif self.startButton.isClicked(event.pos,
                                                yOffset=self.scrollOffset):
                    if self.getGameSession():
                        self.showConfirmDialog = True
                    else:
                        logger.info("Starting new game")
                        self.switchScene(GameState.PREPARE)
                elif self.settingsButton.isClicked(event.pos,
                                                   yOffset=self.scrollOffset):
                    self.switchScene(GameState.SETTINGS)
                elif self.quitButton.isClicked(event.pos,
                                               yOffset=self.scrollOffset):
                    pygame.quit()
                    exit()
                elif self.howToPlayButton.isClicked(event.pos,
                                                    yOffset=self.scrollOffset):
                    self.switchScene(GameState.HELP)

    def drawConfirmDialog(self) -> None:
        """Draw the confirmation dialog overlay."""
        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        dialogWidth = 580
        dialogHeight = 180
        dialogX = (self.screen.get_width() - dialogWidth) // 2
        dialogY = (self.screen.get_height() - dialogHeight) // 2
        dialogRect = pygame.Rect(dialogX, dialogY, dialogWidth, dialogHeight)
        pygame.draw.rect(self.screen, (60, 60, 60), dialogRect)
        pygame.draw.rect(self.screen, (200, 200, 200), dialogRect, 2)
        messageText = self.dialogFont.render(
            "Starting a new game will end the current game.", True,
            (255, 255, 255))
        messageRect = messageText.get_rect(center=(self.screen.get_width() //
                                                   2, dialogY + 35))
        self.screen.blit(messageText, messageRect)
        confirmText = self.dialogFont.render("Do you want to continue?", True,
                                             (255, 255, 255))
        confirmRect = confirmText.get_rect(center=(self.screen.get_width() //
                                                   2, dialogY + 70))
        self.screen.blit(confirmText, confirmRect)
        self.confirmYesButton.draw(self.screen)
        self.confirmNoButton.draw(self.screen)

    def draw(self) -> None:
        """Draw the main menu scene."""
        self.screen.fill((30, 30, 30))
        offsetY = self.scrollOffset
        titleText = self.font.render("Carcassonne", True, (255, 255, 255))
        titleRect = titleText.get_rect(center=(self.screen.get_width() // 2,
                                               self.screen.get_height() // 3 -
                                               60 + offsetY))
        self.screen.blit(titleText, titleRect)
        self.continueButton.disabled = self.getGameSession() is None
        self.continueButton.draw(self.screen, yOffset=offsetY)
        self.startButton.draw(self.screen, yOffset=offsetY)
        self.settingsButton.draw(self.screen, yOffset=offsetY)
        self.quitButton.draw(self.screen, yOffset=offsetY)
        self.howToPlayButton.draw(self.screen, yOffset=offsetY)
        self.maxScroll = max(self.screen.get_height(),
                             self.quitButton.rect.bottom + 100)
        if self.showConfirmDialog:
            self.drawConfirmDialog()
        pygame.display.flip()
