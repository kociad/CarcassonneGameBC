import pygame

class Dropdown:
    def __init__(self, rect, font, options, onSelect=None, defaultIndex=0,
                 textColor=(0, 0, 0), bgColor=(255, 255, 255), borderColor=(0, 0, 0), highlightColor=(200, 200, 200)):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.options = options
        self.selectedIndex = defaultIndex
        self.expanded = False
        self.onSelect = onSelect
        self.disabled = False

        self.textColor = textColor
        self.bgColor = bgColor
        self.borderColor = borderColor
        self.highlightColor = highlightColor
        
    def handleEvent(self, event):
        if self.disabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            elif self.expanded:
                for i, option in enumerate(self.options):
                    optionRect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + (i + 1) * self.rect.height,
                        self.rect.width,
                        self.rect.height
                    )
                    if optionRect.collidepoint(event.pos):
                        self.selectedIndex = i
                        self.expanded = False
                        if self.onSelect:
                            self.onSelect(self.getSelected())
                        return True
                self.expanded = False
        return False
        
    def draw(self, surface):
        fullHeight = self.rect.height + (len(self.options) * self.rect.height if self.expanded else 0)
        drawSurface = pygame.Surface((self.rect.width, fullHeight), pygame.SRCALPHA)

        alpha = 150 if self.disabled else 255
        bg = (*self.bgColor, alpha)
        border = (*self.borderColor, alpha)
        textCol = (*((150, 150, 150) if self.disabled else self.textColor), alpha)
        highlight = (*self.highlightColor, alpha)

        localRect = pygame.Rect(0, 0, self.rect.width, self.rect.height)

        pygame.draw.rect(drawSurface, bg, localRect)
        pygame.draw.rect(drawSurface, border, localRect, 2)

        selectedText = self.font.render(self.options[self.selectedIndex], True, textCol)
        drawSurface.blit(selectedText, (5, (self.rect.height - selectedText.get_height()) // 2))

        if self.expanded:
            for i, option in enumerate(self.options):
                optionRect = pygame.Rect(0, (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(drawSurface, highlight if i == self.selectedIndex else bg, optionRect)
                pygame.draw.rect(drawSurface, border, optionRect, 1)

                optionText = self.font.render(option, True, textCol)
                drawSurface.blit(optionText, (5, optionRect.y + (self.rect.height - optionText.get_height()) // 2))

        surface.blit(drawSurface, self.rect.topleft)
        
    def getSelected(self):
        return self.options[self.selectedIndex]
        
    def setSelected(self, index):
        if 0 <= index < len(self.options):
            self.selectedIndex = index
            
    def setDisabled(self, value: bool):
        self.disabled = value
        return self
