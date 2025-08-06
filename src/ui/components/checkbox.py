import pygame
import typing


class Checkbox:
    """A checkbox UI component."""

    def __init__(
        self,
        rect: pygame.Rect,
        checked: bool = False,
        on_toggle: typing.Optional[typing.Callable] = None,
        box_color: tuple = (255, 255, 255),
        check_color: tuple = (0, 200, 0),
        border_color: tuple = (255, 255, 255),
        disabled_color: tuple = (100, 100, 100)
    ) -> None:
        """
        Initialize the checkbox.
        
        Args:
            rect: Rectangle defining checkbox position and size
            checked: Initial checked state
            on_toggle: Function to call when checkbox is toggled
            box_color: Color of the checkbox box
            check_color: Color of the check mark
            border_color: Color of the border
            disabled_color: Color when disabled
        """
        self.rect = pygame.Rect(rect)
        self.checked = checked
        self.on_toggle = on_toggle
        self.box_color = box_color
        self.check_color = check_color
        self.border_color = border_color
        self.disabled_color = disabled_color
        self.disabled = False

    def handle_event(self,
                     event: pygame.event.Event,
                     y_offset: int = 0) -> bool:
        """
        Handle a pygame event for the checkbox.
        
        Args:
            event: Pygame event to handle
            y_offset: Vertical offset for event detection
            
        Returns:
            True if event was handled, False otherwise
        """
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shifted_rect = self.rect.move(0, y_offset)
            if shifted_rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)
                return True
        return False

    def draw(self, surface: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the checkbox on the given surface.
        
        Args:
            surface: Surface to draw on
            y_offset: Vertical offset for drawing
        """
        shifted_rect = self.rect.move(0, y_offset)
        border_color = self.disabled_color if self.disabled else self.border_color
        pygame.draw.rect(surface, border_color, shifted_rect, 2)
        if self.checked:
            fill_color = self.disabled_color if self.disabled else self.check_color
            inner = shifted_rect.inflate(-6, -6)
            pygame.draw.rect(surface, fill_color, inner)

    def is_checked(self) -> bool:
        """Check if the checkbox is checked."""
        return self.checked

    def set_checked(self, state: bool) -> None:
        """
        Set the checked state of the checkbox.
        
        Args:
            state: Whether the checkbox should be checked
        """
        self.checked = bool(state)

    def set_disabled(self, disabled: bool) -> None:
        """
        Enable or disable the checkbox.
        
        Args:
            disabled: Whether to disable the checkbox
        """
        self.disabled = bool(disabled)

    def is_disabled(self) -> bool:
        """Check if the checkbox is disabled."""
        return self.disabled
