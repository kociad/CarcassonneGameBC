import pygame

class InputField:
    def __init__(self, rect, font, placeholder="", text="", textColor=(0, 0, 0), bgColor=(255, 255, 255), borderColor=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = text
        self.active = False
        self.disabled = False
        self.textColor = textColor
        self.bgColor = bgColor
        self.borderColor = borderColor

    def handleEvent(self, event):
        if self.disabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode
                
    def draw(self, surface):
        bgColor = (200, 200, 200) if self.disabled else self.bgColor
        borderColor = (100, 100, 100) if self.disabled else self.borderColor
        textColor = (150, 150, 150) if self.disabled else (self.textColor if self.text or self.active else (150, 150, 150))

        pygame.draw.rect(surface, bgColor, self.rect)
        pygame.draw.rect(surface, borderColor, self.rect, 2)

        displayText = self.text if self.text or self.active else self.placeholder
        textSurface = self.font.render(displayText, True, textColor)
        surface.blit(textSurface, (self.rect.x + 5, self.rect.y + (self.rect.height - textSurface.get_height()) // 2))
        
    def getText(self):
        return self.text

    def setText(self, value):
        self.text = value
        
    def setDisabled(self, value: bool):
        self.disabled = value
        if value:
            self.active = False