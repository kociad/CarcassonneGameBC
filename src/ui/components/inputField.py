import pygame
import time
import typing


class InputField:
    """A text input field UI component."""

    def __init__(self,
                 rect: pygame.Rect,
                 font: pygame.font.Font,
                 placeholder: str = "",
                 text: str = "",
                 initial_text: str = "",
                 text_color: tuple = (0, 0, 0),
                 bg_color: tuple = (255, 255, 255),
                 border_color: tuple = (0, 0, 0),
                 on_text_change: typing.Optional[typing.Callable] = None,
                 numeric: bool = False,
                 min_value: typing.Optional[float] = None,
                 max_value: typing.Optional[float] = None) -> None:
        """
        Initialize the input field.
        
        Args:
            rect: Rectangle defining input field position and size
            font: Font to use for rendering text
            placeholder: Placeholder text to show when empty
            text: Initial text value
            initial_text: Alternative initial text value
            text_color: Color of the text
            bg_color: Background color
            border_color: Border color
            on_text_change: Function to call when text changes
            numeric: Whether to only allow numeric input
            min_value: Minimum value for numeric input
            max_value: Maximum value for numeric input
        """
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = initial_text if initial_text else text
        self.active = False
        self.disabled = False
        self.read_only = False
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.scroll_offset = 0
        self.cursor_visible = True
        self.last_blink = time.time()
        self.blink_interval = 0.5
        self.numeric = numeric
        self.min_value = min_value
        self.max_value = max_value
        self.on_text_change = on_text_change
        self.cursor_pos = len(self.text)

    def handle_event(self,
                     event: pygame.event.Event,
                     y_offset: int = 0) -> None:
        """
        Handle a pygame event for the input field.
        
        Args:
            event: Pygame event to handle
            y_offset: Vertical offset for event detection
        """
        if self.disabled or self.read_only:
            return
        shifted_rect = self.rect.move(0, y_offset)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = shifted_rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            old_text = self.text
            if event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos -
                                          1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[
                        self.cursor_pos + 1:]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if self.numeric:
                    if (event.unicode.isdigit()
                            or (event.unicode == '-' and len(self.text) == 0)
                            or (event.unicode == '.' and '.' not in self.text)
                            or
                        (event.unicode == ',' and ',' not in self.text)):
                        self.text = self.text[:self.
                                              cursor_pos] + event.unicode + self.text[
                                                  self.cursor_pos:]
                        self.cursor_pos += 1
                else:
                    if event.unicode and event.unicode.isprintable():
                        self.text = self.text[:self.
                                              cursor_pos] + event.unicode + self.text[
                                                  self.cursor_pos:]
                        self.cursor_pos += 1
            self.cursor_pos = max(0, min(self.cursor_pos, len(self.text)))
            if self.on_text_change and self.text != old_text:
                self.on_text_change(self.text)
            cursor_x = self.font.size(self.text[:self.cursor_pos])[0]
            visible_width = self.rect.width - 10
            if cursor_x - self.scroll_offset > visible_width:
                self.scroll_offset = cursor_x - visible_width
            elif cursor_x - self.scroll_offset < 0:
                self.scroll_offset = cursor_x
            text_width = self.font.size(self.text)[0]
            if text_width - self.scroll_offset < visible_width:
                self.scroll_offset = max(0, text_width - visible_width)
            self.scroll_offset = max(0, self.scroll_offset)

    def draw(self, surface: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the input field on the given surface.
        
        Args:
            surface: Surface to draw on
            y_offset: Vertical offset for drawing
        """
        now = time.time()
        if now - self.last_blink > self.blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_blink = now
        draw_rect = self.rect.move(0, y_offset)
        bg_color = (200, 200, 200) if self.disabled else self.bg_color
        border_color = (100, 100, 100) if self.disabled else self.border_color
        text_color = (150, 150, 150) if self.disabled else (
            self.text_color if self.text or self.active else (150, 150, 150))
        pygame.draw.rect(surface, bg_color, draw_rect)
        pygame.draw.rect(surface, border_color, draw_rect, 2)
        display_text = self.text if self.text or self.active else self.placeholder
        text_surface = self.font.render(display_text, True, text_color)
        clamped_width = max(
            0,
            min(self.rect.width - 10,
                text_surface.get_width() - self.scroll_offset))
        visible_rect = pygame.Rect(self.scroll_offset, 0, clamped_width,
                                   text_surface.get_height())
        surface.blit(text_surface.subsurface(visible_rect),
                     (draw_rect.x + 5, draw_rect.y +
                      (draw_rect.height - text_surface.get_height()) // 2))
        if self.active and not self.disabled and self.cursor_visible:
            cursor_x = draw_rect.x + 5 + self.font.size(
                self.text[:self.cursor_pos])[0] - self.scroll_offset
            cursor_y = draw_rect.y + 5
            cursor_height = draw_rect.height - 10
            pygame.draw.line(surface, text_color, (cursor_x, cursor_y),
                             (cursor_x, cursor_y + cursor_height), 2)

    def get_text(self) -> str:
        """Get the current text value."""
        return self.text

    def set_text(self, value: str) -> None:
        """
        Set the text value of the input field.
        
        Args:
            value: Text value to set
        """
        self.text = str(value)
        self.cursor_pos = len(self.text)
        self.scroll_offset = 0

    def set_disabled(self, value: bool) -> None:
        """
        Enable or disable the input field.
        
        Args:
            value: Whether to disable the input field
        """
        self.disabled = value
        if value:
            self.active = False

    def set_read_only(self, value: bool) -> None:
        """
        Set the input field to read-only mode.
        
        Args:
            value: Whether to make the field read-only
        """
        self.read_only = value

    def is_disabled(self) -> bool:
        """Check if the input field is disabled."""
        return self.disabled
