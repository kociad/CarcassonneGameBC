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
        self.bgColor = (200, 200, 200)
        self.textColor = (0, 0, 0)
        self.disabled = disabled
        self.callback = callback
        self._updateRender()

    def _updateRender(self) -> None:
        """Update the rendered text for the button."""
        color = (150, 150, 150) if self.disabled else self.textColor
        self.renderedText = self.font.render(self.text, True, color)
        self.textRect = self.renderedText.get_rect(center=self.rect.center)

    def draw(self, screen: pygame.Surface, yOffset: int = 0) -> None:
        """
        Draw the button on the given screen.
        
        Args:
            screen: Surface to draw on
            yOffset: Vertical offset for drawing
        """
        drawRect = self.rect.move(0, yOffset)
        textRect = self.renderedText.get_rect(center=drawRect.center)
        bg = (180, 180, 180) if self.disabled else self.bgColor
        pygame.draw.rect(screen, bg, drawRect)
        screen.blit(self.renderedText, textRect)

    def handleEvent(self, event: pygame.event.Event) -> None:
        """
        Handle a pygame event for the button.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._isClicked(event.pos):
                if self.callback:
                    self.callback()

    def _isClicked(self, pos: tuple[int, int], yOffset: int = 0) -> bool:
        """
        Check if the button was clicked at the given position.
        
        Args:
            pos: Position to check
            yOffset: Vertical offset for click detection
            
        Returns:
            True if button was clicked, False otherwise
        """
        clickRect = self.rect.move(0, yOffset)
        return not self.disabled and clickRect.collidepoint(pos)

    def setDisabled(self, disabled: bool) -> None:
        """
        Set whether the button is disabled.
        
        Args:
            disabled: Whether to disable the button
        """
        self.disabled = disabled
        self._updateRender()
