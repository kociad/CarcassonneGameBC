import pygame

class InputField:
    def __init__(self, rect, font, placeholder="", textColor=(0, 0, 0), bgColor=(255, 255, 255), borderColor=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.textColor = textColor
        self.bgColor = bgColor
        self.borderColor = borderColor

    def handleEvent(self, event):
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
        pygame.draw.rect(surface, self.bgColor, self.rect)
        pygame.draw.rect(surface, self.borderColor, self.rect, 2)

        displayText = self.text if self.text or self.active else self.placeholder
        color = self.textColor if self.text or self.active else (150, 150, 150)

        textSurface = self.font.render(displayText, True, color)
        surface.blit(textSurface, (self.rect.x + 5, self.rect.y + (self.rect.height - textSurface.get_height()) // 2))

    def getText(self):
        return self.text

    def setText(self, value):
        self.text = value