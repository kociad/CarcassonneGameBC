import pygame
import webbrowser
import typing
from ui.scene import Scene
from ui.components.button import Button
from game_state import GameState
from ui import theme


class HelpScene(Scene):
    """Scene displaying help and controls for the game."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)
        self.font = theme.get_font("title", theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.text_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.controls_font = theme.get_font(
            "label", theme.THEME_FONT_SIZE_HELP_CONTROLS
        )
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self.header_height = 0
        self.controls_label_y = 0
        self.rules_label_y = 0

        self.controls_lines = [
            "Use WASD or the Arrow Keys to move around the board.",
            "Left-click to place a tile.",
            "Right-click to rotate a tile.",
            "Press Space to discard an unplaceable tile or skip meeple placement.",
            "Press Esc to return to the main menu.",
            "Press Tab to toggle the game log.",
            "Use the mouse wheel to scroll menus and the sidebar.",
        ]
        self.rules_lines = [
            "Phase 1: place the drawn tile on the board.",
            "Phase 2: you may place a meeple on the tile.",
            "Tiles must be placed next to existing tiles.",
            "Terrain types must match along touching edges.",
            "You can only discard when no valid placement exists.",
            "Meeples can only be placed on unoccupied features.",
            "Completed features score points immediately.",
        ]

        self.controls_layout: list[tuple[str, pygame.Rect]] = []
        self.rules_layout: list[tuple[str, pygame.Rect]] = []

        self.rules_button = Button(pygame.Rect(0, 0, 0, 60), "Wiki",
                                   self.button_font)
        self.back_button = Button(pygame.Rect(0, 0, 0, 60), "Back",
                                  self.button_font)

        self._layout_controls()

    def _get_line_style(self, line: str) -> tuple[pygame.font.Font, tuple]:
        return self.controls_font, theme.THEME_TEXT_COLOR_LIGHT

    def _set_text_rect(self, line: str, font: pygame.font.Font, x: int, y: int,
                       padding: int) -> tuple[pygame.Rect, int]:
        line_width, line_height = font.size(line)
        line_rect = pygame.Rect(0, y, line_width, line_height)
        line_rect.centerx = x
        return line_rect, y + line_height + padding

    def _set_component_center(self, component, center_x: int, y: int,
                              padding: int) -> int:
        width, height = component.rect.size
        component.rect = pygame.Rect(0, 0, width, height)
        component.rect.center = (center_x, y + height // 2)
        return y + height + padding

    def _layout_controls(self) -> None:
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        x_center = self.screen.get_width() // 2
        button_center_x = self.screen.get_width() // 2
        self.header_height = self._get_scene_header_height(
            self.font.get_height()
        )
        current_y = self.header_height + theme.THEME_LAYOUT_VERTICAL_GAP

        self.controls_label_y = current_y
        current_y += self.text_font.get_height() + padding

        self.controls_layout.clear()
        for line in self.controls_lines:
            line_rect, current_y = self._set_text_rect(
                line, self.controls_font, x_center, current_y, padding)
            self.controls_layout.append((line, line_rect))

        self.rules_label_y = current_y
        current_y += self.text_font.get_height() + padding

        self.rules_layout.clear()
        for line in self.rules_lines:
            line_rect, current_y = self._set_text_rect(
                line, self.controls_font, x_center, current_y, padding)
            self.rules_layout.append((line, line_rect))

        current_y = self._set_component_center(
            self.rules_button, button_center_x, current_y, padding)
        self._set_component_center(
            self.back_button, button_center_x, current_y, padding)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the help scene."""
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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
        title_text = self.font.render("How to Play", True,
                                      theme.THEME_TEXT_COLOR_LIGHT)
        offset_y = self.scroll_offset

        controls_label = self.text_font.render(
            "Game Controls", True, theme.THEME_SECTION_HEADER_COLOR)
        controls_label_rect = controls_label.get_rect()
        controls_label_rect.centerx = self.screen.get_width() // 2
        controls_label_rect.y = self.controls_label_y + offset_y
        self.screen.blit(controls_label, controls_label_rect)

        rules_label = self.text_font.render(
            "Game Rules", True, theme.THEME_SECTION_HEADER_COLOR)
        rules_label_rect = rules_label.get_rect()
        rules_label_rect.centerx = self.screen.get_width() // 2
        rules_label_rect.y = self.rules_label_y + offset_y
        self.screen.blit(rules_label, rules_label_rect)

        for line, line_rect in self.controls_layout:
            font, color = self._get_line_style(line)
            text_surface = font.render(line, True, color)
            draw_rect = line_rect.move(0, offset_y)
            if draw_rect.bottom > 0 and draw_rect.top < self.screen.get_height(
            ):
                self.screen.blit(text_surface, draw_rect)

        for line, line_rect in self.rules_layout:
            font, color = self._get_line_style(line)
            text_surface = font.render(line, True, color)
            draw_rect = line_rect.move(0, offset_y)
            if draw_rect.bottom > 0 and draw_rect.top < self.screen.get_height(
            ):
                self.screen.blit(text_surface, draw_rect)

        self.rules_button.draw(self.screen, y_offset=offset_y)
        self.back_button.draw(self.screen, y_offset=offset_y)
        self._draw_scene_header(title_text)
        self.max_scroll = max(
            self.screen.get_height(),
            self.back_button.rect.bottom + theme.THEME_LAYOUT_VERTICAL_GAP * 2,
        )

    def refresh_theme(self) -> None:
        """Refresh fonts and component styling after theme changes."""
        super().refresh_theme()
        self.font = theme.get_font("title", theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.text_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.controls_font = theme.get_font(
            "label", theme.THEME_FONT_SIZE_HELP_CONTROLS
        )
        self.rules_button.set_font(self.button_font)
        self.rules_button.apply_theme()
        self.back_button.set_font(self.button_font)
        self.back_button.apply_theme()
        self._layout_controls()
