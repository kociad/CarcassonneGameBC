import pygame

class Slider:
    def __init__(self, rect, font, minValue=0, maxValue=100, value=50, onChange=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.minValue = minValue
        self.maxValue = maxValue
        self.value = value
        self.onChange = onChange
        self.lastReportedValue = value

        self.handleRadius = 10
        self.dragging = False

        self.bgColor = (200, 200, 200)
        self.fgColor = (100, 100, 255)
        self.handleColor = (255, 255, 255)
        self.borderColor = (0, 0, 0)
        self.textColor = (255, 255, 255)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._handleRect().collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            relX = min(max(event.pos[0], self.rect.left), self.rect.right)
            ratio = (relX - self.rect.left) / self.rect.width
            newValue = int(self.minValue + ratio * (self.maxValue - self.minValue))

            if newValue != self.value:
                self.value = newValue

                if newValue != self.lastReportedValue:
                    self.lastReportedValue = newValue
                    if self.onChange:
                        self.onChange(newValue)

    def _handleRect(self):
        handleX = self.rect.left + ((self.value - self.minValue) / (self.maxValue - self.minValue)) * self.rect.width
        return pygame.Rect(
            handleX - self.handleRadius, self.rect.centery - self.handleRadius,
            self.handleRadius * 2, self.handleRadius * 2
        )

    def draw(self, surface):
        # Bar background
        pygame.draw.rect(surface, self.bgColor, self.rect)
        pygame.draw.rect(surface, self.borderColor, self.rect, 1)

        # Filled portion
        fillWidth = ((self.value - self.minValue) / (self.maxValue - self.minValue)) * self.rect.width
        pygame.draw.rect(surface, self.fgColor, pygame.Rect(self.rect.left, self.rect.top, fillWidth, self.rect.height))

        # Handle
        handleRect = self._handleRect()
        pygame.draw.circle(surface, self.handleColor, handleRect.center, self.handleRadius)
        pygame.draw.circle(surface, self.borderColor, handleRect.center, self.handleRadius, 1)

        # Value text
        textSurface = self.font.render(str(self.value), True, self.textColor)
        textRect = textSurface.get_rect(midbottom=(handleRect.centerx, self.rect.top - 8))
        surface.blit(textSurface, textRect)

    def getValue(self):
        return self.value

    def setValue(self, val):
        self.value = max(self.minValue, min(self.maxValue, val))
        self.lastReportedValue = self.value  # prevent false positive change right after set