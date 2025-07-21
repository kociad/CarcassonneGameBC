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

    def handleEvent(self, event, yOffset=0):
        shiftedRect = self.rect.move(0, yOffset)
        handleRect = self._handleRect(yOffset)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handleRect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            relX = min(max(event.pos[0], shiftedRect.left), shiftedRect.right)
            ratio = (relX - shiftedRect.left) / shiftedRect.width
            newValue = int(self.minValue + ratio * (self.maxValue - self.minValue))

            if newValue != self.value:
                self.value = newValue
                if newValue != self.lastReportedValue:
                    self.lastReportedValue = newValue
                    if self.onChange:
                        self.onChange(newValue)

    def _handleRect(self, yOffset=0):
        handleX = self.rect.left + ((self.value - self.minValue) / (self.maxValue - self.minValue)) * self.rect.width
        handleY = self.rect.centery + yOffset
        return pygame.Rect(
            handleX - self.handleRadius,
            handleY - self.handleRadius,
            self.handleRadius * 2,
            self.handleRadius * 2
        )

    def draw(self, surface, yOffset=0):
        shiftedRect = self.rect.move(0, yOffset)

        # Bar background
        pygame.draw.rect(surface, self.bgColor, shiftedRect)
        pygame.draw.rect(surface, self.borderColor, shiftedRect, 1)

        # Filled portion
        fillWidth = ((self.value - self.minValue) / (self.maxValue - self.minValue)) * shiftedRect.width
        pygame.draw.rect(surface, self.fgColor, pygame.Rect(shiftedRect.left, shiftedRect.top, fillWidth, shiftedRect.height))

        # Handle
        handleRect = self._handleRect(yOffset)
        pygame.draw.circle(surface, self.handleColor, handleRect.center, self.handleRadius)
        pygame.draw.circle(surface, self.borderColor, handleRect.center, self.handleRadius, 1)

        # Value text
        textSurface = self.font.render(str(self.value), True, self.textColor)
        textRect = textSurface.get_rect(midbottom=(handleRect.centerx, shiftedRect.top - 8))
        surface.blit(textSurface, textRect)

    def getValue(self):
        return self.value

    def setValue(self, val):
        self.value = max(self.minValue, min(self.maxValue, val))
        self.lastReportedValue = self.value
        
    def setMinValue(self, newMinValue):
        """Update minimum value of slider"""
        self.minValue = newMinValue
        # Ensure current value is still valid
        if self.value < self.minValue:
            self.value = self.minValue

    def setValue(self, newValue):
        """Set slider value"""
        self.value = max(self.minValue, min(self.maxValue, newValue))
