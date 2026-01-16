import pygame
from typing import Tuple, Optional

from ui.theme import get_theme


class ProgressBar:
    """
    A progress bar UI component for displaying progress values.
    
    Attributes:
        rect: The rectangle defining the position and size of the progress bar
        font: The font used for rendering text
        min_value: Minimum value of the progress range
        max_value: Maximum value of the progress range
        value: Current progress value
        background_color: Color of the background
        progress_color: Color of the progress fill
        border_color: Color of the border
        show_text: Whether to display the percentage text
        text_color: Color of the text
    """

    def __init__(self,
                 rect: Tuple[int, int, int, int],
                 font: pygame.font.Font | None,
                 min_value: float = 0.0,
                 max_value: float = 1.0,
                 value: float = 0.0,
                 background_color: Tuple[int, int, int] | None = None,
                 progress_color: Tuple[int, int, int] | None = None,
                 border_color: Tuple[int, int, int] | None = None,
                 show_text: bool = True,
                 text_color: Tuple[int, int, int] | None = None):
        """
        Initialize the progress bar.
        
        Args:
            rect: (x, y, width, height) tuple defining position and size
            font: Font for rendering text
            min_value: Minimum value of the progress range
            max_value: Maximum value of the progress range
            value: Current progress value
            background_color: Color of the background
            progress_color: Color of the progress fill
            border_color: Color of the border
            show_text: Whether to display the percentage text
            text_color: Color of the text
        """
        theme = get_theme()
        self.rect = pygame.Rect(rect)
        self.font = font or theme.font("small")
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min_value, min(max_value, value))
        self.background_color = background_color or theme.color("progress_bg")
        self.progress_color = progress_color or theme.color("progress_fg")
        self.border_color = border_color or theme.color("progress_border")
        self.show_text = show_text
        self.text_color = text_color or theme.color("progress_text")

    def set_value(self, value: float) -> None:
        """
        Set the current progress value.
        
        Args:
            value: New progress value (will be clamped to min/max range)
        """
        self.value = max(self.min_value, min(self.max_value, value))

    def get_value(self) -> float:
        """
        Get the current progress value.
        
        Returns:
            Current progress value
        """
        return self.value

    def get_progress(self) -> float:
        """
        Get the progress as a percentage (0.0 to 1.0).
        
        Returns:
            Progress percentage as float between 0.0 and 1.0
        """
        if self.max_value == self.min_value:
            return 0.0
        return (self.value - self.min_value) / (self.max_value -
                                                self.min_value)

    def set_progress(self, progress: float) -> None:
        """
        Set the progress as a percentage (0.0 to 1.0).
        
        Args:
            progress: Progress percentage as float between 0.0 and 1.0
        """
        progress = max(0.0, min(1.0, progress))
        self.value = self.min_value + progress * (self.max_value -
                                                  self.min_value)

    def draw(self, screen: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the progress bar on the screen.
        
        Args:
            screen: The pygame surface to draw on
            y_offset: Vertical offset for scrolling
        """
        x, y = self.rect.x, self.rect.y + y_offset

        pygame.draw.rect(screen, self.background_color,
                         (x, y, self.rect.width, self.rect.height))

        progress = self.get_progress()
        if progress > 0:
            progress_width = int(self.rect.width * progress)
            if progress_width > 0:
                pygame.draw.rect(screen, self.progress_color,
                                 (x, y, progress_width, self.rect.height))

        pygame.draw.rect(screen, self.border_color,
                         (x, y, self.rect.width, self.rect.height), 2)

        if self.show_text:
            progress_text = f"{int(progress * 100)}%"
            text_surface = self.font.render(progress_text, True,
                                            self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = x + self.rect.width // 2
            text_rect.centery = y + self.rect.height // 2
            screen.blit(text_surface, text_rect)
