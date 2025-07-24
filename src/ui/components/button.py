import pygame
import typing

class Button:
    """A clickable button UI component."""
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, callback: typing.Optional[typing.Callable] = None, disabled: bool = False) -> None:
        """Initialize the button."""
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.bgColor = (200, 200, 200)
        self.textColor = (0, 0, 0)
        self.disabled = disabled
        self.callback = callback
        self.updateRender()

    def updateRender(self):
        """Update the rendered text for the button."""
        color = (150, 150, 150) if self.disabled else self.textColor
        self.renderedText = self.font.render(self.text, True, color)
        self.textRect = self.renderedText.get_rect(center=self.rect.center)

    def draw(self, screen: pygame.Surface, yOffset: int = 0) -> None:
        """Draw the button on the given screen, offset vertically by yOffset."""
        drawRect = self.rect.move(0, yOffset)
        textRect = self.renderedText.get_rect(center=drawRect.center)
        bg = (180, 180, 180) if self.disabled else self.bgColor
        pygame.draw.rect(screen, bg, drawRect)
        screen.blit(self.renderedText, textRect)

    def handleEvent(self, event: pygame.event.Event) -> None:
        """Handle a pygame event for the button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.isClicked(event.pos):
                if self.callback:
                    self.callback()

    def isClicked(self, pos: tuple[int, int], yOffset: int = 0) -> bool:
        clickRect = self.rect.move(0, yOffset)
        return not self.disabled and clickRect.collidepoint(pos)

    def setDisabled(self, disabled: bool) -> None:
        self.disabled = disabled
        self.updateRender()
