import pygame
import typing


class Dropdown:
    """A dropdown selection UI component."""

    def __init__(
        self,
        rect: pygame.Rect,
        font: pygame.font.Font,
        options: list[str],
        on_select: typing.Optional[typing.Callable] = None,
        default_index: int = 0,
        text_color: tuple = (0, 0, 0),
        bg_color: tuple = (255, 255, 255),
        border_color: tuple = (0, 0, 0),
        highlight_color: tuple = (200, 200, 200)
    ) -> None:
        """
        Initialize the dropdown.
        
        Args:
            rect: Rectangle defining dropdown position and size
            font: Font to use for rendering
            options: List of options to choose from
            on_select: Function to call when an option is selected
            default_index: Index of the default selected option
            text_color: Color of the text
            bg_color: Background color
            border_color: Border color
            highlight_color: Color for highlighting selected option
        """
        self.rect = pygame.Rect(rect)
        self.font = font
        self.options = options
        self.selected_index = default_index
        self.expanded = False
        self.on_select = on_select
        self.disabled = False
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.highlight_color = highlight_color

    def handle_event(self,
                     event: pygame.event.Event,
                     y_offset: int = 0) -> bool:
        """
        Handle a pygame event for the dropdown.
        
        Args:
            event: Pygame event to handle
            y_offset: Vertical offset for event detection
            
        Returns:
            True if event was handled, False otherwise
        """
        if self.disabled:
            return False
        shifted_rect = self.rect.move(0, y_offset)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if shifted_rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            elif self.expanded:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(
                        shifted_rect.x,
                        shifted_rect.y + (i + 1) * self.rect.height,
                        self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.expanded = False
                        if self.on_select:
                            self.on_select(self.get_selected())
                        return True
                self.expanded = False
        return False

    def draw(self, surface: pygame.Surface, y_offset: int = 0) -> None:
        """
        Draw the dropdown on the given surface.
        
        Args:
            surface: Surface to draw on
            y_offset: Vertical offset for drawing
        """
        draw_rect = self.rect.move(0, y_offset)
        full_height = self.rect.height + (len(self.options) * self.rect.height
                                          if self.expanded else 0)
        draw_surface = pygame.Surface((self.rect.width, full_height),
                                      pygame.SRCALPHA)
        alpha = 150 if self.disabled else 255
        bg = (*self.bg_color, alpha)
        border = (*self.border_color, alpha)
        text_col = (*((150, 150, 150) if self.disabled else self.text_color),
                    alpha)
        highlight = (*self.highlight_color, alpha)
        local_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        pygame.draw.rect(draw_surface, bg, local_rect)
        pygame.draw.rect(draw_surface, border, local_rect, 2)
        selected_text = self.font.render(self.options[self.selected_index],
                                         True, text_col)
        draw_surface.blit(
            selected_text,
            (5, (self.rect.height - selected_text.get_height()) // 2))
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(0, (i + 1) * self.rect.height,
                                          self.rect.width, self.rect.height)
                pygame.draw.rect(draw_surface,
                                 highlight if i == self.selected_index else bg,
                                 option_rect)
                pygame.draw.rect(draw_surface, border, option_rect, 1)
                option_text = self.font.render(option, True, text_col)
                draw_surface.blit(
                    option_text,
                    (5, option_rect.y +
                     (self.rect.height - option_text.get_height()) // 2))
        surface.blit(draw_surface, draw_rect.topleft)

    def get_selected(self) -> str:
        """Get the currently selected option."""
        return self.options[self.selected_index]

    def set_selected(self, index: int) -> None:
        """
        Set the selected option by index.
        
        Args:
            index: Index of the option to select
        """
        if 0 <= index < len(self.options):
            self.selected_index = index

    def set_disabled(self, value: bool) -> 'Dropdown':
        """
        Enable or disable the dropdown.
        
        Args:
            value: Whether to disable the dropdown
            
        Returns:
            Self for method chaining
        """
        self.disabled = value
        return self
