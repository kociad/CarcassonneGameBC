import pygame

class Checkbox:
    def __init__(self, rect, checked=False, onToggle=None,
                 boxColor=(255, 255, 255), checkColor=(0, 200, 0),
                 borderColor=(255, 255, 255), disabledColor=(100, 100, 100)):
        self.rect = pygame.Rect(rect)
        self.checked = checked
        self.onToggle = onToggle

        self.boxColor = boxColor
        self.checkColor = checkColor
        self.borderColor = borderColor
        self.disabledColor = disabledColor

        self.disabled = False

    def handleEvent(self, event, yOffset=0):
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

    def draw(self, surface, yOffset=0):
        shiftedRect = self.rect.move(0, yOffset)
        borderColor = self.disabledColor if self.disabled else self.borderColor
        pygame.draw.rect(surface, borderColor, shiftedRect, 2)

        if self.checked:
            fillColor = self.disabledColor if self.disabled else self.checkColor
            inner = shiftedRect.inflate(-6, -6)
            pygame.draw.rect(surface, fillColor, inner)

    def isChecked(self):
        return self.checked

    def setChecked(self, state):
        self.checked = bool(state)

    def setDisabled(self, disabled):
        self.disabled = disabled
