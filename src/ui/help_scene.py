import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from game_state import GameState
from ui import theme
import typing


class HelpScene(Scene):
    """Scene displaying help and controls for the game."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)
        self.font = theme.get_font(theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.button_font = theme.get_font(theme.THEME_FONT_SIZE_BUTTON)
        self.text_font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
        self.controls_font = theme.get_font(theme.THEME_FONT_SIZE_HELP_CONTROLS)
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        center_x = screen.get_width() // 2 - 100
        current_y = 60
        self.title_y = current_y
        current_y += 80
        self.controls_start_y = current_y
        self.controls = [
            "GAME CONTROLS:", "",
            "WASD or ARROW KEYS - Move around the game board",
            "LMB (Left Mouse Button) - Place card",
            "RMB (Right Mouse Button) - Rotate card",
            "SPACEBAR - Discard card (only if unplaceable) or skip meeple",
            "ESC - Return to main menu", "TAB - Toggle the game log", "",
            "MOUSE WHEEL - Scroll in menus and sidebar", "", "GAME PHASES:",
            "", "Phase 1: Place the drawn card on the board",
            "Phase 2: Optionally place a meeple on the placed card", "",
            "RULES:", "", "Cards must be placed adjacent to existing cards",
            "Terrain types must match on adjacent edges",
            "You can only discard if no valid placement exists",
            "Meeples can only be placed on unoccupied structures",
            "Completed structures score points immediately"
        ]
        line_height = 30
        self.controls_height = len(self.controls) * line_height
        current_y += self.controls_height + 40
        self.rules_button = Button((center_x, current_y, 200, 60), "Wiki",
                                   self.button_font)
        current_y += 80
        self.back_button = Button((center_x, current_y, 200, 60), "Back",
                                  self.button_font)
        self.max_scroll = max(screen.get_height(), current_y + 100)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the help scene."""
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switch_scene(GameState.MENU)
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                self.back_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.rules_button.handle_event(event,
                                               y_offset=self.scroll_offset)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.back_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.rules_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                if self.back_button._is_clicked(event.pos,
                                                y_offset=self.scroll_offset):
                    self.switch_scene(GameState.MENU)
                elif self.rules_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    webbrowser.open("https://wikicarpedia.com/car/Base_game")

    def draw(self) -> None:
        """Draw the help scene."""
        self._draw_background(
            background_color=theme.THEME_HELP_BACKGROUND_COLOR,
            image_name=theme.THEME_HELP_BACKGROUND_IMAGE,
            scale_mode=theme.THEME_HELP_BACKGROUND_SCALE_MODE,
            tint_color=theme.THEME_HELP_BACKGROUND_TINT_COLOR,
            blur_radius=theme.THEME_HELP_BACKGROUND_BLUR_RADIUS,
        )
        offset_y = self.scroll_offset
        title_text = self.font.render("How to Play", True,
                                      theme.THEME_TEXT_COLOR_LIGHT)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2,
                                                 self.title_y + offset_y))
        self.screen.blit(title_text, title_rect)
        current_y = self.controls_start_y + offset_y
        line_height = 35
        for line in self.controls:
            if line == "":
                current_y += line_height // 2
                continue
            if line.endswith(":") and not line.startswith(" "):
                color = theme.THEME_SECTION_HEADER_COLOR
                font = self.text_font
            elif line.startswith("2"):
                color = theme.THEME_SUBSECTION_COLOR
                font = self.controls_font
            else:
                color = theme.THEME_TEXT_COLOR_LIGHT
                font = self.controls_font
            text_surface = font.render(line, True, color)
            if line.endswith(":") and not line.startswith(" "):
                text_rect = text_surface.get_rect(
                    center=(self.screen.get_width() // 2, current_y))
            else:
                text_rect = text_surface.get_rect(left=50, centery=current_y)
            if text_rect.bottom > 0 and text_rect.top < self.screen.get_height(
            ):
                self.screen.blit(text_surface, text_rect)
            current_y += line_height
        self.rules_button.draw(self.screen, y_offset=offset_y)
        self.back_button.draw(self.screen, y_offset=offset_y)
        pygame.display.flip()

    def refresh_theme(self) -> None:
        """Refresh fonts and component styling after theme changes."""
        super().refresh_theme()
        self.font = theme.get_font(theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.button_font = theme.get_font(theme.THEME_FONT_SIZE_BUTTON)
        self.text_font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
        self.controls_font = theme.get_font(theme.THEME_FONT_SIZE_HELP_CONTROLS)
        self.rules_button.set_font(self.button_font)
        self.rules_button.apply_theme()
        self.back_button.set_font(self.button_font)
        self.back_button.apply_theme()
