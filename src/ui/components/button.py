import pygame
import typing


class Button:
    """A clickable button UI component."""

    def __init__(self,
                 rect: pygame.Rect,
                 text: str,
                 font: pygame.font.Font,
                 callback: typing.Optional[typing.Callable] = None,
                 disabled: bool = False) -> None:
        """
        Initialize the button.
        
        Args:
            rect: Rectangle defining button position and size
            text: Text to display on the button
            font: Font to use for rendering text
            callback: Function to call when button is clicked
            disabled: Whether the button is disabled
        """
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.bg_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.disabled = disabled
        self.callback = callback
        self._update_render()

    def _update_render(self) -> None:
        """Update the rendered text for the button."""
        color = (150, 150, 150) if self.disabled else self.text_color
        self.rendered_text = self.font.render(self.text, True, color)
        self.text_rect = self.rendered_text.get_rect(center=self.rect.center)

    def draw(self, screen: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the button on the given screen.
        
        Args:
            screen: Surface to draw on
            y_offset: Vertical offset for drawing
        """
        draw_rect = self.rect.move(0, y_offset)
        text_rect = self.rendered_text.get_rect(center=draw_rect.center)
        bg = (180, 180, 180) if self.disabled else self.bg_color
        pygame.draw.rect(screen, bg, draw_rect)
        screen.blit(self.rendered_text, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a pygame event for the button.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._is_clicked(event.pos):
                if self.callback:
                    self.callback()

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
        self._update_render()
