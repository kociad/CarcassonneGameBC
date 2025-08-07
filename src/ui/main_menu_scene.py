import pygame
import webbrowser
from ui.scene import Scene
from ui.components.button import Button
from game_state import GameState
from utils.settings_manager import settings_manager
import logging
import typing

logger = logging.getLogger(__name__)


class MainMenuScene(Scene):
    """Scene for the main menu of the game."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable,
                 get_game_session: typing.Callable,
                 cleanup_previous_game: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)
        self.font = pygame.font.Font(None, 100)
        self.button_font = pygame.font.Font(None, 48)
        self.dialog_font = pygame.font.Font(None, 36)
        self.get_game_session = get_game_session
        self.cleanup_callback = cleanup_previous_game
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self.show_confirm_dialog = False
        center_x = screen.get_width() // 2 - 100
        center_y = screen.get_height() // 2
        self.continue_button = Button((center_x, center_y - 80, 200, 60),
                                      "Continue",
                                      self.button_font,
                                      None,
                                      disabled=(self.get_game_session()
                                                is None))
        self.start_button = Button((center_x, center_y, 200, 60), "New Game",
                                   self.button_font)
        self.how_to_play_button = Button((center_x, center_y + 80, 200, 60),
                                         "How to play", self.button_font)
        self.settings_button = Button((center_x, center_y + 160, 200, 60),
                                      "Settings", self.button_font)
        self.quit_button = Button((center_x, center_y + 240, 200, 60), "Quit",
                                  self.button_font)
        dialog_center_x = screen.get_width() // 2
        dialog_center_y = screen.get_height() // 2
        self.confirm_yes_button = Button(
            (dialog_center_x - 120, dialog_center_y + 40, 100, 40), "Yes",
            self.dialog_font)
        self.confirm_no_button = Button(
            (dialog_center_x + 20, dialog_center_y + 40, 100, 40), "No",
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
                    if self.confirm_yes_button._is_clicked(event.pos):
                        self.show_confirm_dialog = False
                        logger.info(
                            "Starting new game - cleaning up previous session")
                        self.cleanup_previous_game()
                        self.switch_scene(GameState.PREPARE)
                    elif self.confirm_no_button._is_clicked(event.pos):
                        self.show_confirm_dialog = False
            return
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

    def draw_confirm_dialog(self) -> None:
        """Draw the confirmation dialog overlay."""
        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        dialog_width = 580
        dialog_height = 180
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width,
                                  dialog_height)
        pygame.draw.rect(self.screen, (60, 60, 60), dialog_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), dialog_rect, 2)
        message_text = self.dialog_font.render(
            "Starting a new game will end the current game.", True,
            (255, 255, 255))
        message_rect = message_text.get_rect(center=(self.screen.get_width() //
                                                     2, dialog_y + 35))
        self.screen.blit(message_text, message_rect)
        confirm_text = self.dialog_font.render("Do you want to continue?",
                                               True, (255, 255, 255))
        confirm_rect = confirm_text.get_rect(center=(self.screen.get_width() //
                                                     2, dialog_y + 70))
        self.screen.blit(confirm_text, confirm_rect)
        self.confirm_yes_button.draw(self.screen)
        self.confirm_no_button.draw(self.screen)

    def draw(self) -> None:
        """Draw the main menu scene."""
        self.screen.fill((30, 30, 30))
        offset_y = self.scroll_offset
        title_text = self.font.render("Carcassonne", True, (255, 255, 255))
        title_rect = title_text.get_rect(
            center=(self.screen.get_width() // 2,
                    self.screen.get_height() // 3 - 60 + offset_y))
        self.screen.blit(title_text, title_rect)
        self.continue_button.disabled = self.get_game_session() is None
        self.continue_button.draw(self.screen, y_offset=offset_y)
        self.start_button.draw(self.screen, y_offset=offset_y)
        self.settings_button.draw(self.screen, y_offset=offset_y)
        self.quit_button.draw(self.screen, y_offset=offset_y)
        self.how_to_play_button.draw(self.screen, y_offset=offset_y)
        self.max_scroll = max(self.screen.get_height(),
                              self.quit_button.rect.bottom + 100)
        if self.show_confirm_dialog:
            self.draw_confirm_dialog()
        pygame.display.flip()
