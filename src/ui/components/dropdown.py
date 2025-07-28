import pygame
import typing


class Dropdown:
    """A dropdown selection UI component."""

    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, options: list[str], onSelect: typing.Optional[typing.Callable] = None, defaultIndex: int = 0, textColor: tuple = (0, 0, 0), bgColor: tuple = (255, 255, 255), borderColor: tuple = (0, 0, 0), highlightColor: tuple = (200, 200, 200)) -> None:
        """
        Initialize the dropdown.
        
        Args:
            rect: Rectangle defining dropdown position and size
            font: Font to use for rendering
            options: List of options to choose from
            onSelect: Function to call when an option is selected
            defaultIndex: Index of the default selected option
            textColor: Color of the text
            bgColor: Background color
            borderColor: Border color
            highlightColor: Color for highlighting selected option
        """
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

    def handleEvent(self, event: pygame.event.Event, yOffset: int = 0) -> bool:
        """
        Handle a pygame event for the dropdown.
        
        Args:
            event: Pygame event to handle
            yOffset: Vertical offset for event detection
            
        Returns:
            True if event was handled, False otherwise
        """
        if self.disabled:
            return False
        shiftedRect = self.rect.move(0, yOffset)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if shiftedRect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            elif self.expanded:
                for i, option in enumerate(self.options):
                    optionRect = pygame.Rect(
                        shiftedRect.x,
                        shiftedRect.y + (i + 1) * self.rect.height,
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

    def draw(self, surface: pygame.Surface, yOffset: int = 0) -> None:
        """
        Draw the dropdown on the given surface.
        
        Args:
            surface: Surface to draw on
            yOffset: Vertical offset for drawing
        """
        drawRect = self.rect.move(0, yOffset)
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
        surface.blit(drawSurface, drawRect.topleft)

    def getSelected(self) -> str:
        """Get the currently selected option."""
        return self.options[self.selectedIndex]

    def setSelected(self, index: int) -> None:
        """
        Set the selected option by index.
        
        Args:
            index: Index of the option to select
        """
        if 0 <= index < len(self.options):
            self.selectedIndex = index

    def setDisabled(self, value: bool) -> 'Dropdown':
        """
        Enable or disable the dropdown.
        
        Args:
            value: Whether to disable the dropdown
            
        Returns:
            Self for method chaining
        """
        self.disabled = value
        return self
