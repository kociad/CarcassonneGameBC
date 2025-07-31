import pygame
import typing
from ui.components.toast import Toast

class Scene:
    """Base class for all scenes in the UI."""
    def __init__(self, screen: pygame.Surface, switchSceneCallback: typing.Callable) -> None:
        self.screen = screen
        self.switchScene = switchSceneCallback
        self.scrollOffset = 0
        self.maxScroll = 0
        self.scrollSpeed = 30

    def handleEvents(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the scene."""
        raise NotImplementedError

    def update(self) -> None:
        """Update the scene state."""
        pass

    def draw(self) -> None:
        """Draw the scene."""
        raise NotImplementedError

    def showNotification(self, notificationType: str, message: str) -> None:
        """
        Show notification toast - available to all scenes that have a toastManager
        """
        if hasattr(self, 'toastManager'):
            toastTypeMap = {
                "error": "error",
                "warning": "warning",
                "info": "info",
                "success": "success"
            }

            toastType = toastTypeMap.get(notificationType, "info")
            toast = Toast(message, type=toastType, duration=3)

            self.toastManager.addToast(toast)

    def applyScroll(self, events: list[pygame.event.Event]) -> None:
        """Apply scroll events to the scene."""
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scrollOffset += event.y * self.scrollSpeed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.scrollOffset -= self.scrollSpeed
                elif event.key == pygame.K_UP:
                    self.scrollOffset += self.scrollSpeed
        self.scrollOffset = max(
            min(0, self.scrollOffset),
            min(0, self.screen.get_height() - self.maxScroll)
        )

    def getScrollOffset(self) -> int:
        """Return the current scroll offset."""
        return self.scrollOffset
