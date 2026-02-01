import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from game_state import GameState
from utils.settings_manager import settings_manager
from ui import theme
import logging
import typing

from ui.utils.draw import draw_rect_alpha

logger = logging.getLogger(__name__)


class MainMenuScene(Scene):
    """Scene for the main menu of the game."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable,
                 get_game_session: typing.Callable,
                 cleanup_previous_game: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)
        self.font = theme.get_font(
            "title", theme.THEME_FONT_SIZE_MAIN_MENU_TITLE
        )
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.dialog_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.get_game_session = get_game_session
        self.cleanup_callback = cleanup_previous_game
        self.show_confirm_dialog = False
        self.header_height = 0
        self._title_text = "Carcassonne"
        self._title_surface: pygame.Surface | None = None
        self._cached_title_text: str | None = None
        self._dialog_text_surfaces: dict[tuple[str, tuple[int, int, int]],
                                         pygame.Surface] = {}
        continue_rect = pygame.Rect(0, 0, 0, 60)
        self.continue_button = Button(continue_rect, "Continue",
                                      self.button_font,
                                      None,
                                      disabled=(self.get_game_session()
                                                is None))
        start_rect = pygame.Rect(0, 0, 0, 60)
        self.start_button = Button(start_rect, "New game", self.button_font)
        how_to_play_rect = pygame.Rect(0, 0, 0, 60)
        self.how_to_play_button = Button(how_to_play_rect, "How to play",
                                         self.button_font)
        settings_rect = pygame.Rect(0, 0, 0, 60)
        self.settings_button = Button(settings_rect, "Settings",
                                      self.button_font)
        quit_rect = pygame.Rect(0, 0, 0, 60)
        self.quit_button = Button(quit_rect, "Quit", self.button_font)
        self._layout_buttons()
        dialog_center_x = screen.get_width() // 2
        dialog_center_y = screen.get_height() // 2
        confirm_yes_rect = pygame.Rect(0, 0, 0, 40)
        confirm_yes_rect.center = (dialog_center_x - 70, dialog_center_y + 60)
        self.confirm_yes_button = Button(confirm_yes_rect, "Yes",
                                         self.dialog_font)
        confirm_no_rect = pygame.Rect(0, 0, 0, 40)
        confirm_no_rect.center = (dialog_center_x + 70, dialog_center_y + 60)
        self.confirm_no_button = Button(confirm_no_rect, "No",
                                        self.dialog_font)

    def cleanup_previous_game(self):
        """Clean up resources from previous game session."""
        try:
            logger.debug("Cleaning up previous game resources...")
            if hasattr(self, 'cleanup_callback') and self.cleanup_callback:
                self.cleanup_callback()
        except Exception as e:
            from utils.logging_config import log_error
            log_error("Error during previous game cleanup from menu", e)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle events for the main menu scene."""
        if self.show_confirm_dialog:
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_confirm_dialog = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.confirm_yes_button.handle_event(event)
                    self.confirm_no_button.handle_event(event)
                    if self.confirm_yes_button._is_clicked(event.pos):
                        self.show_confirm_dialog = False
                        logger.info(
                            "Starting new game - cleaning up previous session")
                        self.cleanup_previous_game()
                        self.switch_scene(GameState.PREPARE)
                    elif self.confirm_no_button._is_clicked(event.pos):
                        self.show_confirm_dialog = False
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                    self.confirm_yes_button.handle_event(event)
                    self.confirm_no_button.handle_event(event)
            return
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.continue_button.handle_event(event,
                                                  y_offset=self.scroll_offset)
                self.start_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                self.settings_button.handle_event(event,
                                                  y_offset=self.scroll_offset)
                self.quit_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.how_to_play_button.handle_event(
                    event, y_offset=self.scroll_offset)
                if self.continue_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset
                ) and not self.continue_button.disabled:
                    session = self.get_game_session()
                    network_mode = getattr(session, 'network_mode', 'local')
                    if hasattr(session,
                               'lobby_completed') and network_mode in (
                                   "host",
                                   "client") and not session.lobby_completed:
                        self.switch_scene(GameState.LOBBY)
                    else:
                        self.switch_scene(GameState.GAME)
                elif self.start_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    if self.get_game_session():
                        self.show_confirm_dialog = True
                    else:
                        logger.info("Starting new game")
                        self.switch_scene(GameState.PREPARE)
                elif self.settings_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    self.switch_scene(GameState.SETTINGS)
                elif self.quit_button._is_clicked(event.pos,
                                                  y_offset=self.scroll_offset):
                    pygame.quit()
                    exit()
                elif self.how_to_play_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    self.switch_scene(GameState.HELP)
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                self.continue_button.handle_event(event,
                                                  y_offset=self.scroll_offset)
                self.start_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                self.settings_button.handle_event(event,
                                                  y_offset=self.scroll_offset)
                self.quit_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.how_to_play_button.handle_event(
                    event, y_offset=self.scroll_offset)

    def draw_confirm_dialog(self) -> None:
        """Draw the confirmation dialog overlay."""
        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()),
            pygame.SRCALPHA,
        )
        overlay.fill(theme.THEME_MENU_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))
        dialog_width = 580
        dialog_height = 180
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width,
                                  dialog_height)
        draw_rect_alpha(
            self.screen,
            theme.THEME_MENU_DIALOG_BG_COLOR,
            dialog_rect,
        )
        draw_rect_alpha(
            self.screen,
            theme.THEME_MENU_DIALOG_BORDER_COLOR,
            dialog_rect,
            2,
        )
        dialog_color = theme.THEME_MENU_DIALOG_TEXT_COLOR
        message_text = self._dialog_text_surfaces.get(
            ("Starting a new game will end the current game.", dialog_color)
        )
        if message_text is None:
            message_text = self.dialog_font.render(
                "Starting a new game will end the current game.", True,
                dialog_color)
            self._dialog_text_surfaces[
                ("Starting a new game will end the current game.", dialog_color)
            ] = message_text
        message_rect = message_text.get_rect(center=(self.screen.get_width() //
                                                     2, dialog_y + 35))
        self.screen.blit(message_text, message_rect)
        confirm_text = self._dialog_text_surfaces.get(
            ("Do you want to continue?", dialog_color)
        )
        if confirm_text is None:
            confirm_text = self.dialog_font.render(
                "Do you want to continue?", True, dialog_color)
            self._dialog_text_surfaces[
                ("Do you want to continue?", dialog_color)
            ] = confirm_text
        confirm_rect = confirm_text.get_rect(center=(self.screen.get_width() //
                                                     2, dialog_y + 70))
        self.screen.blit(confirm_text, confirm_rect)
        self.confirm_yes_button.draw(self.screen)
        self.confirm_no_button.draw(self.screen)

    def draw(self) -> None:
        """Draw the main menu scene."""
        self._draw_background(
            background_color=theme.THEME_MAIN_MENU_BACKGROUND_COLOR,
            image_name=theme.THEME_MAIN_MENU_BACKGROUND_IMAGE,
            scale_mode=theme.THEME_MAIN_MENU_BACKGROUND_SCALE_MODE,
            tint_color=theme.THEME_MAIN_MENU_BACKGROUND_TINT_COLOR,
            blur_radius=theme.THEME_MAIN_MENU_BACKGROUND_BLUR_RADIUS,
        )
        offset_y = self.scroll_offset
        if (self._title_surface is None
                or self._cached_title_text != self._title_text):
            self._title_surface = self.font.render(
                self._title_text, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            self._cached_title_text = self._title_text
        self.continue_button.disabled = self.get_game_session() is None
        self.continue_button.draw(self.screen, y_offset=offset_y)
        self.start_button.draw(self.screen, y_offset=offset_y)
        self.settings_button.draw(self.screen, y_offset=offset_y)
        self.quit_button.draw(self.screen, y_offset=offset_y)
        self.how_to_play_button.draw(self.screen, y_offset=offset_y)
        self.max_scroll = max(
            self.screen.get_height(),
            self.quit_button.rect.bottom + theme.THEME_LAYOUT_VERTICAL_GAP * 2,
        )
        if self.show_confirm_dialog:
            self.draw_confirm_dialog()
        self._draw_scene_header(self._title_surface)

    def _layout_buttons(self) -> None:
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        center_x = self.screen.get_width() // 2
        buttons = [
            self.continue_button,
            self.start_button,
            self.how_to_play_button,
            self.settings_button,
            self.quit_button,
        ]
        self.header_height = self._get_scene_header_height(
            self.font.get_height()
        )
        total_height = sum(button.rect.height for button in buttons)
        total_height += padding * (len(buttons) - 1)
        available_height = self.screen.get_height() - self.header_height - padding
        current_y = self.header_height + padding + max(
            0, (available_height - total_height) // 2
        )
        for button in buttons:
            width, height = button.rect.size
            button.rect = pygame.Rect(0, 0, width, height)
            button.rect.centerx = center_x
            button.rect.y = current_y
            current_y += height + padding

    def refresh_theme(self, theme_name: str | None = None) -> None:
        """Refresh fonts and component styling after theme changes."""
        super().refresh_theme(theme_name)
        self.font = theme.get_font(
            "title", theme.THEME_FONT_SIZE_MAIN_MENU_TITLE
        )
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.dialog_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self._title_surface = None
        self._cached_title_text = None
        self._dialog_text_surfaces.clear()
        buttons = [
            self.continue_button,
            self.start_button,
            self.how_to_play_button,
            self.settings_button,
            self.quit_button,
        ]
        for button in buttons:
            button.set_font(self.button_font)
            button.apply_theme()
        self.confirm_yes_button.set_font(self.dialog_font)
        self.confirm_yes_button.apply_theme()
        self.confirm_no_button.set_font(self.dialog_font)
        self.confirm_no_button.apply_theme()
        self._layout_buttons()
