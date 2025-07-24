import pygame
import typing

class Checkbox:
    """A checkbox UI component."""
    def __init__(self, rect: pygame.Rect, checked: bool = False, onToggle: typing.Optional[typing.Callable] = None,
                 boxColor: tuple = (255, 255, 255), checkColor: tuple = (0, 200, 0),
                 borderColor: tuple = (255, 255, 255), disabledColor: tuple = (100, 100, 100)) -> None:
        """Initialize the checkbox."""
        self.rect = pygame.Rect(rect)
        self.checked = checked
        self.onToggle = onToggle
        self.boxColor = boxColor
        self.checkColor = checkColor
        self.borderColor = borderColor
        self.disabledColor = disabledColor
        self.disabled = False

    def handleEvent(self, event: pygame.event.Event, yOffset: int = 0) -> bool:
        """Handle a pygame event for the checkbox."""
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shiftedRect = self.rect.move(0, yOffset)
            if shiftedRect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.onToggle:
                    self.onToggle(self.checked)
                return True
        return False

    def draw(self, surface: pygame.Surface, yOffset: int = 0) -> None:
        """Draw the checkbox on the given surface, offset vertically by yOffset."""
        shiftedRect = self.rect.move(0, yOffset)
        borderColor = self.disabledColor if self.disabled else self.borderColor
        pygame.draw.rect(surface, borderColor, shiftedRect, 2)
        if self.checked:
            fillColor = self.disabledColor if self.disabled else self.checkColor
            inner = shiftedRect.inflate(-6, -6)
            pygame.draw.rect(surface, fillColor, inner)

    def isChecked(self) -> bool:
        """Return True if the checkbox is checked."""
        return self.checked

    def setChecked(self, state: bool) -> None:
        """Set the checked state of the checkbox."""
        self.checked = bool(state)

    def setDisabled(self, disabled: bool) -> None:
        """Enable or disable the checkbox."""
        self.disabled = bool(disabled)
