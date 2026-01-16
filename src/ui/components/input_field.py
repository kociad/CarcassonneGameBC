import pygame
import time
import typing

from ui import theme


class InputField:
    """A text input field UI component."""

    _instances: typing.ClassVar[list['InputField']] = []

    def __init__(self,
                 rect: pygame.Rect,
                 font: pygame.font.Font,
                 placeholder: str = "",
                 text: str = "",
                 initial_text: str = "",
                 text_color: tuple = theme.THEME_INPUT_TEXT_COLOR,
                 bg_color: tuple = theme.THEME_INPUT_BG_COLOR,
                 border_color: tuple = theme.THEME_INPUT_BORDER_COLOR,
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
        self.hovered = False
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
        self.selection_start: typing.Optional[int] = None
        self.selection_end: typing.Optional[int] = None
        InputField._instances.append(self)

    def _has_selection(self) -> bool:
        return (self.selection_start is not None
                and self.selection_end is not None
                and self.selection_start != self.selection_end)

    def _get_selection_range(self) -> tuple[int, int]:
        if not self._has_selection():
            return (self.cursor_pos, self.cursor_pos)
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        return (start, end)

    def _clear_selection(self) -> None:
        self.selection_start = None
        self.selection_end = None

    def _delete_selection(self) -> bool:
        if not self._has_selection():
            return False
        start, end = self._get_selection_range()
        self.text = self.text[:start] + self.text[end:]
        self.cursor_pos = start
        self._clear_selection()
        return True

    @staticmethod
    def _ensure_scrap_ready() -> bool:
        try:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
        except pygame.error:
            return False
        return pygame.scrap.get_init()

    def _copy_to_clipboard(self, text: str) -> None:
        if not text:
            return
        if not self._ensure_scrap_ready():
            return
        try:
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))
        except pygame.error:
            return

    def _get_clipboard_text(self) -> str:
        if not self._ensure_scrap_ready():
            return ""
        try:
            data = pygame.scrap.get(pygame.SCRAP_TEXT)
        except pygame.error:
            return ""
        if not data:
            return ""
        if isinstance(data, bytes):
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                return data.decode('latin1', errors='ignore')
        return str(data)

    def _filter_numeric_insert(self, insert_text: str,
                               base_text: str,
                               insert_pos: int) -> str:
        allowed: list[str] = []
        has_minus = '-' in base_text
        has_dot = '.' in base_text
        has_comma = ',' in base_text
        for ch in insert_text:
            if ch.isdigit():
                allowed.append(ch)
                continue
            if ch == '-' and not has_minus and insert_pos == 0 and not allowed:
                allowed.append(ch)
                has_minus = True
                continue
            if ch == '.' and not has_dot:
                allowed.append(ch)
                has_dot = True
                continue
            if ch == ',' and not has_comma:
                allowed.append(ch)
                has_comma = True
        return "".join(allowed)

    def _insert_text(self, insert_text: str) -> bool:
        if not insert_text:
            return False
        base_text = self.text
        insert_pos = self.cursor_pos
        if self._has_selection():
            start, end = self._get_selection_range()
            base_text = self.text[:start] + self.text[end:]
            insert_pos = start
        if self.numeric:
            insert_text = self._filter_numeric_insert(insert_text,
                                                     base_text, insert_pos)
        if not insert_text:
            return False
        if self._has_selection():
            self._delete_selection()
        self.text = self.text[:self.cursor_pos] + insert_text + self.text[
            self.cursor_pos:]
        self.cursor_pos += len(insert_text)
        return True

    def _ensure_cursor_visible(self) -> None:
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

    def handle_event(self,
                     event: pygame.event.Event,
                     y_offset: int = 0) -> None:
        """
        Handle a pygame event for the input field.
        
        Args:
            event: Pygame event to handle
            y_offset: Vertical offset for event detection
        """
        shifted_rect = self.rect.move(0, y_offset)
        if self.disabled:
            self.hovered = False
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = shifted_rect.collidepoint(event.pos)
            any_hovered = any(
                field.hovered or field.active for field in InputField._instances)
            if any_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = shifted_rect.collidepoint(event.pos)
            if self.active:
                self._clear_selection()
            any_hovered = any(
                field.hovered or field.active for field in InputField._instances)
            if any_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if self.active and event.type == pygame.KEYDOWN:
            old_text = self.text
            has_ctrl = bool(event.mod & pygame.KMOD_CTRL)
            if has_ctrl and event.key == pygame.K_c:
                if self._has_selection():
                    start, end = self._get_selection_range()
                    self._copy_to_clipboard(self.text[start:end])
                else:
                    self._copy_to_clipboard(self.text)
            elif has_ctrl and event.key == pygame.K_x:
                if not self.read_only:
                    if self._has_selection():
                        start, end = self._get_selection_range()
                        self._copy_to_clipboard(self.text[start:end])
                    else:
                        self._copy_to_clipboard(self.text)
                    if self.text:
                        if not self._delete_selection():
                            self.text = ""
                            self.cursor_pos = 0
                        self._clear_selection()
            elif has_ctrl and event.key == pygame.K_v:
                if not self.read_only:
                    clipboard_text = self._get_clipboard_text()
                    if clipboard_text:
                        changed = self._insert_text(clipboard_text)
                        if changed:
                            self._clear_selection()
            elif has_ctrl and event.key == pygame.K_a:
                if self.text:
                    self.selection_start = 0
                    self.selection_end = len(self.text)
                    self.cursor_pos = len(self.text)
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                self._clear_selection()
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                self._clear_selection()
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                self._clear_selection()
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                self._clear_selection()
            elif event.key == pygame.K_BACKSPACE:
                if not self.read_only:
                    if not self._delete_selection():
                        if self.cursor_pos > 0:
                            self.text = self.text[:self.cursor_pos -
                                                  1] + self.text[self.cursor_pos:]
                            self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if not self.read_only:
                    if not self._delete_selection():
                        if self.cursor_pos < len(self.text):
                            self.text = self.text[:self.cursor_pos] + self.text[
                                self.cursor_pos + 1:]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if not self.read_only:
                    if event.unicode and event.unicode.isprintable():
                        self._insert_text(event.unicode)
            self.cursor_pos = max(0, min(self.cursor_pos, len(self.text)))
            if self.on_text_change and self.text != old_text:
                self.on_text_change(self.text)
            self._ensure_cursor_visible()

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
        bg_color = (theme.THEME_INPUT_DISABLED_BG_COLOR if self.disabled
                    else self.bg_color)
        if self.disabled:
            border_color = theme.THEME_INPUT_DISABLED_BORDER_COLOR
        else:
            if self.active or self.hovered:
                border_color = tuple(
                    min(255, channel + 40) for channel in self.border_color)
            else:
                border_color = self.border_color
        text_color = (theme.THEME_INPUT_DISABLED_TEXT_COLOR if self.disabled
                      else (self.text_color if self.text or self.active
                            else theme.THEME_INPUT_PLACEHOLDER_COLOR))
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
        if self._has_selection() and self.text:
            selection_start, selection_end = self._get_selection_range()
            start_x = self.font.size(self.text[:selection_start])[0]
            end_x = self.font.size(self.text[:selection_end])[0]
            start_x -= self.scroll_offset
            end_x -= self.scroll_offset
            visible_width = self.rect.width - 10
            highlight_start = max(0, start_x)
            highlight_end = min(visible_width, end_x)
            if highlight_end > highlight_start:
                selection_color = tuple(
                    min(255, channel + 60) for channel in self.bg_color)
                highlight_surface = pygame.Surface(
                    (highlight_end - highlight_start, text_surface.get_height()),
                    pygame.SRCALPHA)
                highlight_surface.fill((*selection_color, 140))
                surface.blit(highlight_surface,
                             (draw_rect.x + 5 + highlight_start,
                              draw_rect.y +
                              (draw_rect.height - text_surface.get_height()) //
                              2))
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
        self._clear_selection()

    def set_disabled(self, value: bool) -> None:
        """
        Enable or disable the input field.
        
        Args:
            value: Whether to disable the input field
        """
        self.disabled = value
        if value:
            self.active = False
            self._clear_selection()

    def set_font(self, font: pygame.font.Font) -> None:
        """Update the font used by the input field."""
        self.font = font
        self.scroll_offset = 0

    def apply_theme(self) -> None:
        """Refresh colors from the current theme."""
        self.text_color = theme.THEME_INPUT_TEXT_COLOR
        self.bg_color = theme.THEME_INPUT_BG_COLOR
        self.border_color = theme.THEME_INPUT_BORDER_COLOR

    def set_read_only(self, value: bool) -> None:
        """
        Set the input field to read-only mode.
        
        Args:
            value: Whether to make the field read-only
        """
        self.read_only = value
        if value:
            self._clear_selection()

    def is_disabled(self) -> bool:
        """Check if the input field is disabled."""
        return self.disabled
