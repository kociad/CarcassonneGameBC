import pygame
import time
import typing

class InputField:
    """A text input field UI component."""
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, placeholder: str = "", text: str = "", initialText: str = "", textColor: tuple = (0, 0, 0), bgColor: tuple = (255, 255, 255), borderColor: tuple = (0, 0, 0), onTextChange: typing.Optional[typing.Callable] = None, numeric: bool = False, minValue: typing.Optional[float] = None, maxValue: typing.Optional[float] = None) -> None:
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = initialText if initialText else text
        self.active = False
        self.disabled = False
        self.readOnly = False
        self.textColor = textColor
        self.bgColor = bgColor
        self.borderColor = borderColor
        self.scrollOffset = 0
        self.cursorVisible = True
        self.lastBlink = time.time()
        self.blinkInterval = 0.5
        self.numeric = numeric
        self.minValue = minValue
        self.maxValue = maxValue
        self.onTextChange = onTextChange
        self.cursorPosition = len(self.text)

    def handleEvent(self, event: pygame.event.Event, yOffset: int = 0) -> None:
        """Handle a pygame event for the input field."""
        if self.disabled or self.readOnly:
            return
        shiftedRect = self.rect.move(0, yOffset)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = shiftedRect.collidepoint(event.pos)
            if self.active:
                relX = event.pos[0] - shiftedRect.x - 5 + self.scrollOffset
                pos = 0
                for i in range(len(self.text) + 1):
                    width = self.font.size(self.text[:i])[0]
                    if width > relX:
                        break
                    pos = i
                self.cursorPosition = pos
        if self.active and event.type == pygame.KEYDOWN:
            oldText = self.text
            if event.key == pygame.K_BACKSPACE:
                if self.cursorPosition > 0:
                    self.text = self.text[:self.cursorPosition-1] + self.text[self.cursorPosition:]
                    self.cursorPosition -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursorPosition < len(self.text):
                    self.text = self.text[:self.cursorPosition] + self.text[self.cursorPosition+1:]
            elif event.key == pygame.K_LEFT:
                if self.cursorPosition > 0:
                    self.cursorPosition -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursorPosition < len(self.text):
                    self.cursorPosition += 1
            elif event.key == pygame.K_HOME:
                self.cursorPosition = 0
            elif event.key == pygame.K_END:
                self.cursorPosition = len(self.text)
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if self.numeric:
                    if event.unicode.isdigit() or (event.unicode == '-' and len(self.text) == 0):
                        self.text = self.text[:self.cursorPosition] + event.unicode + self.text[self.cursorPosition:]
                        self.cursorPosition += 1
                else:
                    if event.unicode and event.unicode.isprintable():
                        self.text = self.text[:self.cursorPosition] + event.unicode + self.text[self.cursorPosition:]
                        self.cursorPosition += 1
            self.cursorPosition = max(0, min(self.cursorPosition, len(self.text)))
            if self.onTextChange and self.text != oldText:
                self.onTextChange(self.text)
            cursorX = self.font.size(self.text[:self.cursorPosition])[0]
            visibleWidth = self.rect.width - 10
            if cursorX - self.scrollOffset > visibleWidth:
                self.scrollOffset = cursorX - visibleWidth
            elif cursorX - self.scrollOffset < 0:
                self.scrollOffset = cursorX
            textWidth = self.font.size(self.text)[0]
            if textWidth < visibleWidth:
                self.scrollOffset = 0

    def draw(self, surface: pygame.Surface, yOffset: int = 0) -> None:
        """Draw the input field on the given surface."""
        now = time.time()
        if now - self.lastBlink > self.blinkInterval:
            self.cursorVisible = not self.cursorVisible
            self.lastBlink = now
        drawRect = self.rect.move(0, yOffset)
        bgColor = (200, 200, 200) if self.disabled else self.bgColor
        borderColor = (100, 100, 100) if self.disabled else self.borderColor
        textColor = (150, 150, 150) if self.disabled else (self.textColor if self.text or self.active else (150, 150, 150))
        pygame.draw.rect(surface, bgColor, drawRect)
        pygame.draw.rect(surface, borderColor, drawRect, 2)
        displayText = self.text if self.text or self.active else self.placeholder
        textSurface = self.font.render(displayText, True, textColor)
        clampedWidth = max(0, min(self.rect.width - 10, textSurface.get_width() - self.scrollOffset))
        visibleRect = pygame.Rect(self.scrollOffset, 0, clampedWidth, textSurface.get_height())
        surface.blit(
            textSurface.subsurface(visibleRect),
            (drawRect.x + 5, drawRect.y + (drawRect.height - textSurface.get_height()) // 2)
        )
        if self.active and not self.disabled and self.cursorVisible:
            cursorX = self.font.size(self.text[:self.cursorPosition])[0] - self.scrollOffset
            cursorX = drawRect.x + 5 + cursorX
            cursorY = drawRect.y + 5
            cursorHeight = drawRect.height - 10
            pygame.draw.line(surface, textColor, (cursorX, cursorY), (cursorX, cursorY + cursorHeight), 2)

    def getText(self) -> str:
        """Return the current text value."""
        return self.text

    def setText(self, value: str) -> None:
        """Set the text value of the input field and reset cursor position."""
        self.text = str(value)
        self.cursorPosition = len(self.text)
        self.scrollOffset = 0

    def setDisabled(self, value: bool) -> None:
        """Enable or disable the input field."""
        self.disabled = value
        if value:
            self.active = False

    def setReadOnly(self, value: bool) -> None:
        """Set the input field to read-only mode."""
        self.readOnly = value

    def isDisabled(self) -> bool:
        """Return True if the input field is disabled."""
        return self.disabled