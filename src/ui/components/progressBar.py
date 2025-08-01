import pygame
from typing import Tuple, Optional


class ProgressBar:
    """
    A progress bar UI component for displaying progress values.
    
    Attributes:
        rect: The rectangle defining the position and size of the progress bar
        font: The font used for rendering text
        minValue: Minimum value of the progress range
        maxValue: Maximum value of the progress range
        value: Current progress value
        backgroundColor: Color of the background
        progressColor: Color of the progress fill
        borderColor: Color of the border
        showText: Whether to display the percentage text
        textColor: Color of the text
    """

    def __init__(self,
                 rect: Tuple[int, int, int, int],
                 font: pygame.font.Font,
                 minValue: float = 0.0,
                 maxValue: float = 1.0,
                 value: float = 0.0,
                 backgroundColor: Tuple[int, int, int] = (80, 80, 80),
                 progressColor: Tuple[int, int, int] = (100, 255, 100),
                 borderColor: Tuple[int, int, int] = (150, 150, 150),
                 showText: bool = True,
                 textColor: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize the progress bar.
        
        Args:
            rect: (x, y, width, height) tuple defining position and size
            font: Font for rendering text
            minValue: Minimum value of the progress range
            maxValue: Maximum value of the progress range
            value: Current progress value
            backgroundColor: Color of the background
            progressColor: Color of the progress fill
            borderColor: Color of the border
            showText: Whether to display the percentage text
            textColor: Color of the text
        """
        self.rect = pygame.Rect(rect)
        self.font = font
        self.minValue = minValue
        self.maxValue = maxValue
        self.value = max(minValue, min(maxValue, value))
        self.backgroundColor = backgroundColor
        self.progressColor = progressColor
        self.borderColor = borderColor
        self.showText = showText
        self.textColor = textColor

    def setValue(self, value: float) -> None:
        """
        Set the current progress value.
        
        Args:
            value: New progress value (will be clamped to min/max range)
        """
        self.value = max(self.minValue, min(self.maxValue, value))

    def getValue(self) -> float:
        """
        Get the current progress value.
        
        Returns:
            Current progress value
        """
        return self.value

    def getProgress(self) -> float:
        """
        Get the progress as a percentage (0.0 to 1.0).
        
        Returns:
            Progress percentage as float between 0.0 and 1.0
        """
        if self.maxValue == self.minValue:
            return 0.0
        return (self.value - self.minValue) / (self.maxValue - self.minValue)

    def setProgress(self, progress: float) -> None:
        """
        Set the progress as a percentage (0.0 to 1.0).
        
        Args:
            progress: Progress percentage as float between 0.0 and 1.0
        """
        progress = max(0.0, min(1.0, progress))
        self.value = self.minValue + progress * (self.maxValue - self.minValue)

    def draw(self, screen: pygame.Surface, yOffset: int = 0) -> None:
        """
        Draw the progress bar on the screen.
        
        Args:
            screen: The pygame surface to draw on
            yOffset: Vertical offset for scrolling
        """
        x, y = self.rect.x, self.rect.y + yOffset

        pygame.draw.rect(screen, self.backgroundColor,
                         (x, y, self.rect.width, self.rect.height))

        progress = self.getProgress()
        if progress > 0:
            progressWidth = int(self.rect.width * progress)
            if progressWidth > 0:
                pygame.draw.rect(screen, self.progressColor,
                                 (x, y, progressWidth, self.rect.height))

        pygame.draw.rect(screen, self.borderColor,
                         (x, y, self.rect.width, self.rect.height), 2)

        if self.showText:
            progressText = f"{int(progress * 100)}%"
            textSurface = self.font.render(progressText, True, self.textColor)
            textRect = textSurface.get_rect()
            textRect.centerx = x + self.rect.width // 2
            textRect.centery = y + self.rect.height // 2
            screen.blit(textSurface, textRect)
