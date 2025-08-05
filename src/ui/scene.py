import pygame
import typing
from ui.components.toast import Toast


class Scene:
    """Base class for all scenes in the UI."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        self.screen = screen
        self.switch_scene = switch_scene_callback
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the scene."""
        raise NotImplementedError

    def update(self) -> None:
        """Update the scene state."""
        pass

    def draw(self) -> None:
        """Draw the scene."""
        raise NotImplementedError

    def show_notification(self, notification_type: str, message: str) -> None:
        """
        Show notification toast - available to all scenes that have a toastManager
        """
        if hasattr(self, 'toastManager'):
            toast_type_map = {
                "error": "error",
                "warning": "warning",
                "info": "info",
                "success": "success"
            }

            toast_type = toast_type_map.get(notification_type, "info")
            toast = Toast(message, type=toast_type, duration=3)

            self.toast_manager.add_toast(toast)

    def _apply_scroll(self, events: list[pygame.event.Event]) -> None:
        """Apply scroll events to the scene."""
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset += event.y * self.scroll_speed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.scroll_offset -= self.scroll_speed
                elif event.key == pygame.K_UP:
                    self.scroll_offset += self.scroll_speed
        self.scroll_offset = max(
            min(0, self.scroll_offset),
            min(0,
                self.screen.get_height() - self.max_scroll))

    def _get_scroll_offset(self) -> int:
        """Return the current scroll offset."""
        return self.scroll_offset
