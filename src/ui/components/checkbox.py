import pygame

class Checkbox:
    def __init__(self, rect, checked=False, onToggle=None,
                 boxColor=(255, 255, 255), checkColor=(0, 200, 0), borderColor=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.checked = checked
        self.onToggle = onToggle
        
        self.boxColor = boxColor
        self.checkColor = checkColor
        self.borderColor = borderColor
        
    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.onToggle:
                    self.onToggle(self.checked)
                return True
        return False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.borderColor, self.rect, 2)

        if self.checked:
            inner = self.rect.inflate(-6, -6)
            pygame.draw.rect(surface, self.checkColor, inner)
            
    def isChecked(self):
        return self.checked
        
    def setChecked(self, state):
        self.checked = bool(state)