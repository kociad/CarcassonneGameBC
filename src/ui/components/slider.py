import pygame
from ui.components.inputField import InputField
from ui.components.toast import Toast
import typing


class Slider:
    """A slider UI component for selecting a numeric value."""

    def __init__(self,
                 rect: pygame.Rect,
                 font,
                 min_value: float,
                 max_value: float,
                 initial_value: float = None,
                 value: float = None,
                 on_change: typing.Callable = None) -> None:
        """
        Initialize the slider.
        
        Args:
            rect: Rectangle defining slider position and size
            font: Font to use for rendering
            min_value: Minimum value of the slider
            max_value: Maximum value of the slider
            initial_value: Initial value (alternative to value)
            value: Initial value
            on_change: Function to call when value changes
        """
        self.rect = pygame.Rect(rect)
        self.font = font
        self.min_value = min_value
        self.max_value = max_value
        self.value = value if value is not None else (
            initial_value if initial_value is not None else min_value)
        self.on_change = on_change
        self.last_reported_value = self.value
        self.disabled = False
        self.handle_radius = 10
        self.dragging = False
        self.bg_color = (200, 200, 200)
        self.fg_color = (100, 100, 255)
        self.handle_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.disabled_bg_color = (100, 100, 100)
        self.disabled_fg_color = (60, 60, 60)
        self.disabled_handle_color = (150, 150, 150)
        self.disabled_border_color = (80, 80, 80)
        self.toast_queue = []
        self.active_toast = None
        input_field_width = 60
        input_field_height = self.rect.height
        input_x = self.rect.right + 10
        input_y = self.rect.y
        self.input_field = InputField(
            rect=(input_x, input_y, input_field_width, input_field_height),
            font=font,
            initial_text=str(self.value),
            on_text_change=None,
            numeric=True,
            min_value=min_value,
        )

    def _validate_and_apply_input(self) -> None:
        """Validate input field value and apply if valid."""
        input_text = self.input_field.get_text().strip()
        if not input_text:
            self.input_field.set_text(str(self.value))
            return
        try:
            new_value = int(input_text)
            if new_value < self.min_value:
                self._show_toast(f"Value must be at least {self.min_value}",
                                 "error")
                self.input_field.set_text(str(self.value))
            elif new_value > self.max_value:
                self._show_toast(f"Value must be at most {self.max_value}",
                                 "error")
                self.input_field.set_text(str(self.value))
            else:
                if new_value != self.value:
                    self.value = new_value
                    if new_value != self.last_reported_value:
                        self.last_reported_value = new_value
                        if self.on_change:
                            self.on_change(new_value)
        except ValueError:
            self.input_field.set_text(str(self.value))

    def _show_toast(self, message: str, toast_type: str = "info") -> None:
        """
        Show toast notification.
        
        Args:
            message: Message to display
            toast_type: Type of toast notification
        """
        if self.active_toast and self.active_toast.message == message:
            return
        if any(t.message == message for t in self.toast_queue):
            return
        toast = Toast(message, type=toast_type)
        self.toast_queue.append(toast)

    def set_disabled(self, disabled: bool) -> None:
        """
        Enable or disable the slider.
        
        Args:
            disabled: Whether to disable the slider
        """
        self.disabled = disabled
        self.input_field.set_disabled(disabled)
        if disabled:
            self.dragging = False

    def is_disabled(self) -> bool:
        """Check if the slider is disabled."""
        return self.disabled

    def handle_event(self,
                     event: pygame.event.Event,
                     y_offset: int = 0) -> None:
        """
        Handle a pygame event for the slider.
        
        Args:
            event: Pygame event to handle
            y_offset: Vertical offset for event detection
        """
        was_active = self.input_field.active
        self.input_field.handle_event(event, y_offset=y_offset)
        if was_active and not self.input_field.active:
            self._validate_and_apply_input()
        if (self.input_field.active and event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN):
            self._validate_and_apply_input()
        if self.disabled:
            return
        shifted_rect = self.rect.move(0, y_offset)
        handle_rect = self._handle_rect(y_offset)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
            elif shifted_rect.collidepoint(event.pos):
                rel_x = min(max(event.pos[0], shifted_rect.left),
                            shifted_rect.right)
                ratio = (rel_x - shifted_rect.left) / shifted_rect.width
                new_value = int(self.min_value + ratio *
                                (self.max_value - self.min_value))
                if new_value != self.value:
                    self.value = new_value
                    self.input_field.set_text(str(new_value))
                    if new_value != self.last_reported_value:
                        self.last_reported_value = new_value
                        if self.on_change:
                            self.on_change(new_value)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = min(max(event.pos[0], shifted_rect.left),
                        shifted_rect.right)
            ratio = (rel_x - shifted_rect.left) / shifted_rect.width
            new_value = int(self.min_value + ratio *
                            (self.max_value - self.min_value))
            if new_value != self.value:
                self.value = new_value
                self.input_field.set_text(str(new_value))
                if new_value != self.last_reported_value:
                    self.last_reported_value = new_value
                    if self.on_change:
                        self.on_change(new_value)

    def _handle_rect(self, y_offset: int = 0) -> pygame.Rect:
        """
        Get the rectangle for the slider handle.
        
        Args:
            y_offset: Vertical offset
            
        Returns:
            Rectangle for the slider handle
        """
        handle_x = self.rect.left + (
            (self.value - self.min_value) /
            (self.max_value - self.min_value)) * self.rect.width
        handle_y = self.rect.centery + y_offset
        return pygame.Rect(handle_x - self.handle_radius,
                           handle_y - self.handle_radius,
                           self.handle_radius * 2, self.handle_radius * 2)

    def draw(self, surface: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the slider on the given surface.
        
        Args:
            surface: Surface to draw on
            y_offset: Vertical offset for drawing
        """
        shifted_rect = self.rect.move(0, y_offset)
        if self.disabled:
            bg_color = self.disabled_bg_color
            fg_color = self.disabled_fg_color
            handle_color = self.disabled_handle_color
            border_color = self.disabled_border_color
        else:
            bg_color = self.bg_color
            fg_color = self.fg_color
            handle_color = self.handle_color
            border_color = self.border_color
        pygame.draw.rect(surface, bg_color, shifted_rect)
        pygame.draw.rect(surface, border_color, shifted_rect, 1)
        fill_width = ((self.value - self.min_value) /
                      (self.max_value - self.min_value)) * shifted_rect.width
        pygame.draw.rect(
            surface, fg_color,
            pygame.Rect(shifted_rect.left, shifted_rect.top, fill_width,
                        shifted_rect.height))
        handle_rect = self._handle_rect(y_offset)
        pygame.draw.circle(surface, handle_color, handle_rect.center,
                           self.handle_radius)
        pygame.draw.circle(surface, border_color, handle_rect.center,
                           self.handle_radius, 1)
        self.input_field.draw(surface, y_offset=y_offset)
        if not self.active_toast and self.toast_queue:
            self.active_toast = self.toast_queue.pop(0)
            self.active_toast.start()
        if self.active_toast:
            self.active_toast.draw(surface)
            if self.active_toast.is_expired():
                self.active_toast = None

    def get_value(self) -> float:
        """Get the current value of the slider."""
        return self.value

    def set_value(self, new_value: float) -> None:
        """
        Set the slider value.
        
        Args:
            new_value: New value to set
        """
        self.value = max(self.min_value, min(self.max_value, new_value))
        self.last_reported_value = self.value
        self.input_field.set_text(str(self.value))

    def set_min_value(self, new_min_value: float) -> None:
        """
        Update the minimum value of the slider.
        
        Args:
            new_min_value: New minimum value
        """
        self.min_value = new_min_value
        self.input_field.min_value = new_min_value
        if self.value < self.min_value:
            self.value = self.min_value
            self.last_reported_value = self.value
