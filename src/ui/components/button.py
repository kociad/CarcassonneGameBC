import pygame
import typing

from ui import theme


class Button:
    """A clickable button UI component."""

    def __init__(self,
                 rect: pygame.Rect,
                 text: str,
                 font: pygame.font.Font,
                 callback: typing.Optional[typing.Callable] = None,
                 disabled: bool = False,
                 bg_color: tuple[int, int, int] = theme.THEME_BUTTON_BG_COLOR,
                 hover_bg_color: tuple[int, int, int] = (
                     theme.THEME_BUTTON_HOVER_BG_COLOR),
                 pressed_bg_color: tuple[int, int, int] = (
                     theme.THEME_BUTTON_PRESSED_BG_COLOR)
                 ) -> None:
        """
        Initialize the button.
        
        Args:
            rect: Rectangle defining button position and size
            text: Text to display on the button
            font: Font to use for rendering text
            callback: Function to call when button is clicked
            disabled: Whether the button is disabled
            bg_color: Background color for normal state
            hover_bg_color: Background color when hovered
            pressed_bg_color: Background color when pressed
        """
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.bg_color = bg_color
        self.hover_bg_color = hover_bg_color
        self.pressed_bg_color = pressed_bg_color
        self.text_color = theme.THEME_BUTTON_TEXT_COLOR
        self.disabled = disabled
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False
        self._update_render()

    def _update_render(self) -> None:
        """Update the rendered text for the button."""
        color = (theme.THEME_BUTTON_TEXT_DISABLED_COLOR if self.disabled
                 else self.text_color)
        self.rendered_text = self.font.render(self.text, True, color)
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)

    def set_font(self, font: pygame.font.Font) -> None:
        """Update the font used by the button."""
        self.font = font
        self._update_render()

    def apply_theme(self) -> None:
        """Refresh colors from the current theme."""
        self.bg_color = theme.THEME_BUTTON_BG_COLOR
        self.hover_bg_color = theme.THEME_BUTTON_HOVER_BG_COLOR
        self.pressed_bg_color = theme.THEME_BUTTON_PRESSED_BG_COLOR
        self.text_color = theme.THEME_BUTTON_TEXT_COLOR
        self._update_render()

    def draw(self, screen: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the button on the given screen.
        
        Args:
            screen: Surface to draw on
            y_offset: Vertical offset for drawing
        """
        draw_rect = self.rect.move(0, y_offset)
        text_rect = self.rendered_text.get_rect(center=draw_rect.center)
        if self.disabled:
            bg = theme.THEME_BUTTON_DISABLED_BG_COLOR
        elif self.is_pressed:
            bg = self.pressed_bg_color
        elif self.is_hovered:
            bg = self.hover_bg_color
        else:
            bg = self.bg_color
        pygame.draw.rect(screen, bg, draw_rect)
        screen.blit(self.rendered_text, text_rect)

    def handle_event(self,
                     event: pygame.event.Event,
                     y_offset: int = 0) -> None:
        """
        Handle a pygame event for the button.
        
        Args:
            event: Pygame event to handle
            y_offset: Vertical offset for click detection
        """
        if self.disabled:
            self.is_hovered = False
            self.is_pressed = False
            return

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self._is_clicked(event.pos, y_offset=y_offset)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_pressed = self._is_clicked(event.pos, y_offset=y_offset)
            if self.is_pressed and self.callback:
                self.callback()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False

    def _is_clicked(self, pos: tuple[int, int], y_offset: int = 0) -> bool:
        """
        Check if the button was clicked at the given position.
        
        Args:
            pos: Position to check
            y_offset: Vertical offset for click detection
            
        Returns:
            True if button was clicked, False otherwise
        """
        click_rect = self.rect.move(0, y_offset)
        return not self.disabled and click_rect.collidepoint(pos)

    def set_disabled(self, disabled: bool) -> None:
        """
        Set whether the button is disabled.
        
        Args:
            disabled: Whether to disable the button
        """
        self.disabled = disabled
        if disabled:
            self.is_hovered = False
            self.is_pressed = False
        self._update_render()
