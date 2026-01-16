import pygame
from ui.scene import Scene
from ui.components.button import Button
from ui.components.toast import Toast, ToastManager
from game_state import GameState
from utils.settings_manager import settings_manager
from ui import theme
import typing


class LobbyScene(Scene):
    """Scene for the game lobby, where players wait for all participants to connect before starting the game."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable,
                 start_game_callback: typing.Callable,
                 get_game_session: typing.Callable, network: typing.Any,
                 game_log: typing.Any) -> None:
        """Initialize the lobby scene with UI components and network state."""
        super().__init__(screen, switch_scene_callback)
        self.start_game_callback = start_game_callback
        self.get_game_session = get_game_session
        self.network = network
        self.game_log = game_log
        self.font = theme.get_font(theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.button_font = theme.get_font(theme.THEME_FONT_SIZE_BUTTON)
        self.toast_manager = ToastManager(max_toasts=5)
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self.is_host = (getattr(self.network, 'network_mode',
                                'local') == 'host')
        self.network_mode = getattr(self.network, 'network_mode', 'local')
        self.start_button = Button((screen.get_width() // 2 - 100,
                                    screen.get_height() - 120, 200, 60),
                                   "Start Game", self.button_font)
        self.waiting_for_host = False
        self.original_player_names = settings_manager.get("PLAYERS", [])
        if self.network_mode == "local":
            self.switch_scene(GameState.GAME)
            return
        self._update_player_status()

    def _update_player_status(self):
        """Update the connection status of all players in the lobby."""
        session = self.get_game_session()
        self.players = session.get_players() if session else []
        self.status_list = []
        for i, origName in enumerate(self.original_player_names):
            player = next((p for p in self.players if p.get_index() == i),
                          None)
            if player is not None and player.get_is_ai():
                status = "AI"
                color = theme.THEME_LOBBY_STATUS_AI_COLOR
                name = player.get_name()
            elif player is not None and player.is_human:
                status = "Connected"
                color = theme.THEME_LOBBY_STATUS_CONNECTED_COLOR
                name = player.get_name()
            else:
                status = "Waiting..."
                color = theme.THEME_LOBBY_STATUS_WAITING_COLOR
                name = origName
            self.status_list.append({
                "name": name,
                "status": status,
                "color": color
            })
        self.required_humans = sum(1 for s in self.status_list
                                   if s["status"] != "AI")
        self.connected_humans = sum(1 for s in self.status_list
                                    if s["status"] == "Connected")
        self.all_connected = (self.connected_humans == self.required_humans)
        self.start_button.set_disabled(not (
            self.is_host and self.all_connected))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle user and network events in the lobby scene."""
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switch_scene(GameState.MENU)
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                self.start_button.handle_event(event,
                                               y_offset=self.scroll_offset)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.start_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                if self.is_host and self.start_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    if self.all_connected:
                        session = self.get_game_session()
                        if hasattr(session, 'lobby_completed'):
                            session.lobby_completed = True
                        self.start_game_callback(
                            [p.get_name() for p in self.players])
                    else:
                        self.toast_manager.add_toast(
                            Toast("Not all players are connected!",
                                  type="warning"))
        self._update_player_status()

    def update(self):
        """Update the lobby scene state."""
        self._update_player_status()

    def draw(self) -> None:
        """Draw the lobby scene, including player statuses and the start button."""
        self._draw_background(
            image_path=getattr(theme, "THEME_LOBBY_BACKGROUND_IMAGE", None),
            scale_mode_override=getattr(
                theme,
                "THEME_LOBBY_BACKGROUND_SCALE_MODE",
                None
            ),
            tint_color_override=getattr(
                theme,
                "THEME_LOBBY_BACKGROUND_TINT_COLOR",
                None
            ),
            blur_radius_override=getattr(
                theme,
                "THEME_LOBBY_BACKGROUND_BLUR_RADIUS",
                None
            )
        )
        offset_y = self.scroll_offset
        title_text = self.font.render("Lobby", True,
                                      theme.THEME_TEXT_COLOR_LIGHT)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2,
                                                 60 + offset_y))
        self.screen.blit(title_text, title_rect)
        label_font = theme.get_font(theme.THEME_FONT_SIZE_BUTTON)
        y = 160 + offset_y
        if self.is_host:
            for i, status in enumerate(self.status_list):
                name = status["name"]
                stat = status["status"]
                color = status["color"]
                name_surf = label_font.render(
                    f"{name}", True, theme.THEME_TEXT_COLOR_LIGHT)
                status_surf = label_font.render(stat, True, color)
                spacing = 32
                total_width = name_surf.get_width(
                ) + spacing + status_surf.get_width()
                start_x = (self.screen.get_width() - total_width) // 2
                self.screen.blit(name_surf, (start_x, y))
                self.screen.blit(
                    status_surf,
                    (start_x + name_surf.get_width() + spacing, y))
                y += 60
            self.start_button.draw(self.screen, y_offset=offset_y)
        else:
            wait_font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
            wait_text = wait_font.render(
                "Waiting for host to start the game...", True,
                theme.THEME_TEXT_COLOR_LIGHT)
            wait_rect = wait_text.get_rect(
                center=(self.screen.get_width() // 2,
                        self.screen.get_height() // 2 + 40 + offset_y))
            self.screen.blit(wait_text, wait_rect)
        self.toast_manager.draw(self.screen)
        if self.game_log:
            self.game_log.draw(self.screen)
        pygame.display.flip()
