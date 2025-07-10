import pygame

class Button:
    def __init__(self, text, rect, font, bgColor=(200, 200, 200), textColor=(0, 0, 0), disabled=False):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.bgColor = bgColor
        self.textColor = textColor
        self.disabled = disabled

        self.updateRender()

    def updateRender(self):
        color = (150, 150, 150) if self.disabled else self.textColor
        self.renderedText = self.font.render(self.text, True, color)
        self.textRect = self.renderedText.get_rect(center=self.rect.center)

    def draw(self, surface, yOffset=0):
        drawRect = self.rect.move(0, yOffset)
        textRect = self.renderedText.get_rect(center=drawRect.center)
        bg = (180, 180, 180) if self.disabled else self.bgColor
        pygame.draw.rect(surface, bg, drawRect)
        surface.blit(self.renderedText, textRect)

    def isClicked(self, mousePos, yOffset=0):
        clickRect = self.rect.move(0, yOffset)
        return not self.disabled and clickRect.collidepoint(mousePos)

    def setDisabled(self, state: bool):
        self.disabled = state
        self.updateRender()
