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

        self.textColor = textColor
        self.bgColor = bgColor
        self.borderColor = borderColor
        self.highlightColor = highlightColor

    def handleEvent(self, event):
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
        # Draw main box
        pygame.draw.rect(surface, self.bgColor, self.rect)
        pygame.draw.rect(surface, self.borderColor, self.rect, 2)

        selectedText = self.font.render(self.options[self.selectedIndex], True, self.textColor)
        surface.blit(selectedText, (self.rect.x + 5, self.rect.y + (self.rect.height - selectedText.get_height()) // 2))

        # Draw dropdown
        if self.expanded:
            for i, option in enumerate(self.options):
                optionRect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(surface, self.highlightColor if i == self.selectedIndex else self.bgColor, optionRect)
                pygame.draw.rect(surface, self.borderColor, optionRect, 1)

                optionText = self.font.render(option, True, self.textColor)
                surface.blit(optionText, (optionRect.x + 5, optionRect.y + (optionRect.height - optionText.get_height()) // 2))

    def getSelected(self):
        return self.options[self.selectedIndex]

    def setSelected(self, index):
        if 0 <= index < len(self.options):
            self.selectedIndex = index
