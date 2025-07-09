import pygame
import time

class InputField:
    def __init__(self, rect, font, placeholder="", text="", textColor=(0, 0, 0), bgColor=(255, 255, 255), borderColor=(0, 0, 0), onTextChange=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = text
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
        
        self.onTextChange = onTextChange

    def handleEvent(self, event):
        if self.disabled or self.readOnly:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if self.active and event.type == pygame.KEYDOWN:
            oldText = self.text

            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode

            # Notify change
            if self.onTextChange and self.text != oldText:
                self.onTextChange(self.text)

            # Adjust scroll if needed
            textWidth = self.font.size(self.text)[0]
            visibleWidth = self.rect.width - 10

            if textWidth > visibleWidth:
                self.scrollOffset = textWidth - visibleWidth
            else:
                self.scrollOffset = 0
                
    def draw(self, surface):
        now = time.time()
        if now - self.lastBlink > self.blinkInterval:
            self.cursorVisible = not self.cursorVisible
            self.lastBlink = now

        bgColor = (200, 200, 200) if self.disabled else self.bgColor
        borderColor = (100, 100, 100) if self.disabled else self.borderColor
        textColor = (150, 150, 150) if self.disabled else (self.textColor if self.text or self.active else (150, 150, 150))

        pygame.draw.rect(surface, bgColor, self.rect)
        pygame.draw.rect(surface, borderColor, self.rect, 2)

        displayText = self.text if self.text or self.active else self.placeholder
        textSurface = self.font.render(displayText, True, textColor)
        textWidth = textSurface.get_width()

        clampedWidth = max(0, min(self.rect.width - 10, textSurface.get_width() - self.scrollOffset))
        visibleRect = pygame.Rect(self.scrollOffset, 0, clampedWidth, textSurface.get_height())
        surface.blit(textSurface.subsurface(visibleRect), (self.rect.x + 5, self.rect.y + (self.rect.height - textSurface.get_height()) // 2))
        
        if self.active and not self.disabled and self.cursorVisible:
            cursorX = self.rect.x + 5 + self.font.size(self.text)[0] - self.scrollOffset
            cursorY = self.rect.y + 5
            cursorHeight = self.rect.height - 10
            pygame.draw.line(surface, textColor, (cursorX, cursorY), (cursorX, cursorY + cursorHeight), 2)

    def getText(self):
        return self.text

    def setText(self, value):
        self.text = value
        self.scrollOffset = 0

    def setDisabled(self, value: bool):
        self.disabled = value
        if value:
            self.active = False
            
    def setReadOnly(self, value: bool):
        self.readOnly = value
