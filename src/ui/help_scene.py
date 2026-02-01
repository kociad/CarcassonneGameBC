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
        self.sections = [
            ("Objective", [
                "Score more points than your opponents by placing cards,",
                "completing structures, and wisely placing your figures.",
                "The game ends when the deck runs out of cards.",
            ]),
            ("Starting a New Game", [
                "Select New Game from the main menu.",
                "Set player names and choose which players are controlled by AI.",
                "Select AI difficulty and card sets.",
                "Press Start Game.",
                "The starting card is placed automatically in the center of the"
                " board.",
            ]),
            ("Turn Structure", [
                "Players take turns clockwise. Each turn has two phases.",
                "Phase 1: Place a Card",
                "Draw one card and place it so all touching edges match.",
                "You may rotate the card before placing it.",
                "If multiple positions are valid, choose any of them.",
                "If no valid placement is available, press SPACE to discard.",
                "Phase 2: Place a Figure (Optional)",
                "The figure must be placed on the card you just played.",
                "The selected region must not already contain another figure.",
                "Only one figure may be placed per turn.",
                "You may skip this phase by pressing SPACE.",
                "Figures remain until the structure is completed.",
            ]),
            ("Scoring", [
                "Points are awarded automatically when a structure is completed.",
                "Completed structures return all figures to their owners.",
                "Unfinished structures are scored at the end of the game.",
                "Current scores are always visible in the sidebar.",
            ]),
            ("Controls", [
                "Mouse: place cards and figures.",
                "Right Mouse Button: rotate card.",
                "WASD / Arrow Keys: move the camera.",
                "SPACE: skip figure placement or discard card.",
                "TAB: show or hide the game log.",
                "ESC: return to the main menu.",
            ]),
            ("User Interface", [
                "Game Board: main playing area.",
                "Sidebar: current card, remaining deck, player list and scores.",
                "Valid Placement Highlight: shows legal card positions.",
                "Toast Messages: short feedback and warning messages.",
                "Game Log: history of important game events.",
            ]),
            ("End of the Game", [
                "The game ends when the deck is empty.",
                "Final scoring applies to all unfinished structures.",
                "Final scores and player ranking are displayed.",
            ]),
            ("Network Play (Local Network Only)", [
                "Network games are supported only on the same local network.",
                "Online play over the internet is not supported.",
            ]),
            ("Hosting a Game", [
                "Open New Game and set Network Mode to Host.",
                "Configure players and game options.",
                "The game shows your local IP address.",
                "Share the IP address and port with other players.",
                "Wait until all players are connected.",
                "Press Start Game to begin.",
                "Only the host can start the game.",
            ]),
            ("Joining a Game", [
                "Open New Game and set Network Mode to Client.",
                "Enter the host’s IP address and port.",
                "Press Start Game.",
                "Wait in the lobby until the host starts the game.",
            ]),
            ("Lobby", [
                "Before the game starts, all players wait in a lobby.",
                "The lobby displays connected players, waiting players, and AI.",
                "The game can only start once all required players connect.",
            ]),
        ]

        self.section_headers_layout: list[tuple[str, int]] = []
        self.section_body_layout: list[tuple[str, int]] = []

        self.rules_button = Button(pygame.Rect(0, 0, 0, 60), "Wiki",
                                   self.button_font)
        self.back_button = Button(pygame.Rect(0, 0, 0, 60), "Back",
                                  self.button_font)

        self._layout_controls()

    def _get_line_style(self, line: str) -> tuple[pygame.font.Font, tuple]:
        return self.controls_font, theme.THEME_TEXT_COLOR_LIGHT

    def _set_text_rect(self, line: str, font: pygame.font.Font, y: int,
                       padding: int) -> tuple[int, int]:
        _, line_height = font.size(line)
        return y, y + line_height + padding

    def _set_component_center(self, component, center_x: int, y: int,
                              padding: int) -> int:
        width, height = component.rect.size
        component.rect = pygame.Rect(0, 0, width, height)
        component.rect.center = (center_x, y + height // 2)
        return y + height + padding

    def _get_content_bounds(self) -> tuple[int, int]:
        screen_width = self.screen.get_width()
        max_width = min(
            int(screen_width * 0.7),
            theme.THEME_HELP_MAX_WIDTH,
        )
        content_left = (screen_width - max_width) // 2
        content_right = content_left + max_width
        return content_left, content_right

    def _layout_controls(self) -> None:
        section_gap = theme.THEME_LAYOUT_SECTION_GAP
        line_gap = theme.THEME_LAYOUT_LINE_GAP
        button_center_x = self.screen.get_width() // 2
        self.header_height = self._get_scene_header_height(
            self.font.get_height()
        )
        current_y = self.header_height + section_gap

        self.section_headers_layout.clear()
        self.section_body_layout.clear()
        for index, (section_title, section_lines) in enumerate(self.sections):
            if index > 0:
                current_y += section_gap
            self.section_headers_layout.append((section_title, current_y))
            current_y += self.text_font.get_height() + line_gap
            for line in section_lines:
                line_y, current_y = self._set_text_rect(
                    line, self.controls_font, current_y, line_gap)
                self.section_body_layout.append((line, line_y))

        current_y = self._set_component_center(
            self.rules_button, button_center_x, current_y, section_gap)
        self._set_component_center(
            self.back_button, button_center_x, current_y, section_gap)

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
        content_left, _ = self._get_content_bounds()

        for section_title, header_y in self.section_headers_layout:
            section_label = self.text_font.render(
                section_title, True, theme.THEME_SECTION_HEADER_COLOR)
            section_label_rect = section_label.get_rect()
            section_label_rect.center = (
                self.screen.get_width() // 2,
                header_y + offset_y + section_label_rect.height // 2,
            )
            self.screen.blit(section_label, section_label_rect)

        for line, line_y in self.section_body_layout:
            font, color = self._get_line_style(line)
            text_surface = font.render(line, True, color)
            draw_rect = text_surface.get_rect()
            draw_rect.left = content_left
            draw_rect.y = line_y + offset_y
            if draw_rect.bottom > 0 and draw_rect.top < self.screen.get_height(
            ):
                self.screen.blit(text_surface, draw_rect)

        self.rules_button.draw(self.screen, y_offset=offset_y)
        self.back_button.draw(self.screen, y_offset=offset_y)
        self._draw_scene_header(title_text)
        self.max_scroll = max(
            self.screen.get_height(),
            self.back_button.rect.bottom + theme.THEME_LAYOUT_SECTION_GAP * 2,
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
