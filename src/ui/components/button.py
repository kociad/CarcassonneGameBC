import pygame

class Button:
    def __init__(self, text, rect, font, bgColor=(200, 200, 200), textColor=(0, 0, 0)):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.bgColor = bgColor
        self.textColor = textColor
        self.renderedText = self.font.render(self.text, True, self.textColor)
        self.textRect = self.renderedText.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bgColor, self.rect)
        surface.blit(self.renderedText, self.textRect)

    def isClicked(self, mousePos):
        return self.rect.collidepoint(mousePos)
