import pygame
import socket
from ui.scene import Scene
from ui.components.button import Button
from ui.components.input_field import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast, ToastManager
from ui.components.checkbox import Checkbox
from game_state import GameState
from utils.settings_manager import settings_manager
from ui import theme
import typing
from models.card_sets.set_loader import get_available_card_sets

FORBIDDEN_WORDS = ["ai", "easy", "normal", "hard", "expert"]


def _get_local_ip():
    """
    Get the local IP address using multiple methods.
    Falls back to default IP from settings if all methods fail.
    """
    default_ip = settings_manager.get("HOST_IP", "0.0.0.0")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip != "127.0.0.1" and not local_ip.startswith("127."):
            return local_ip
    except Exception:
        pass

    try:
        for interface in socket.getaddrinfo(socket.gethostname(), None):
            ip = interface[4][0]
            if ip != "127.0.0.1" and not ip.startswith("127."):
                return ip
    except Exception:
        pass

    return default_ip


class PlayerConfiguration:
    """Single source of truth for player data"""

    def __init__(self, name="", is_ai=False, enabled=True):
        self.name = name
        self.is_ai = is_ai
        self.enabled = enabled

    def set_name(self, name):
        """Update name and handle AI prefix logic"""
        if self.is_ai and not name.startswith("AI_"):
            self.is_ai = False
        self.name = name

    def set_ai(self, is_ai):
        """Update AI status and handle name prefix"""
        self.is_ai = is_ai
        if is_ai and not self.name.startswith("AI_"):
            self.name = f"AI_{self.name}"
        elif not is_ai and self.name.startswith("AI_"):
            if self.name.startswith("AI_EASY_"):
                self.name = self.name[8:]
            elif self.name.startswith("AI_HARD_"):
                self.name = self.name[8:]
            elif self.name.startswith("AI_EXPERT_"):
                self.name = self.name[10:]
            elif self.name.startswith("AI_NORMAL_"):
                self.name = self.name[10:]
            elif self.name.startswith("AI_"):
                self.name = self.name[3:]

    def get_display_name(self):
        """Get name for display purposes"""
        return self.name

    def copy(self):
        """Create a copy of this configuration"""
        return PlayerConfiguration(self.name, self.is_ai, self.enabled)


class GamePrepareScene(Scene):

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)

        settings_manager.reload_from_file()

        self.switch_scene_callback = switch_scene_callback

        self.font = theme.get_font("title", theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.section_header_font = theme.get_font(
            "section_header", theme.THEME_FONT_SIZE_SECTION_HEADER
        )
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.input_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.dropdown_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)

        self.toast_manager = ToastManager(max_toasts=5)

        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self.header_height = 0
        self._title_text = "Game Setup"
        self._title_surface: pygame.Surface | None = None
        self._cached_title_text: str | None = None
        self._section_header_surfaces: dict[str, pygame.Surface] = {}
        self._label_surfaces: dict[tuple[int, str, tuple[int, int, int]],
                                   pygame.Surface] = {}

        self.original_player_names = settings_manager.get("PLAYERS", []).copy()

        self.players = []
        for i in range(6):
            if i < len(self.original_player_names):
                name = self.original_player_names[i]
            else:
                name = f"Player {i + 1}"

            enabled = i < 2
            self.players.append(PlayerConfiguration(name, False, enabled))

        network_mode = settings_manager.get("NETWORK_MODE", "local")
        host_ip = settings_manager.get("HOST_IP", "0.0.0.0")
        port = str(settings_manager.get("HOST_PORT", 222))
        self.local_ip = _get_local_ip()
        self.network_mode = network_mode

        x_center = screen.get_width() // 2 - 100

        self.player_label_y = 0

        add_player_rect = pygame.Rect(0, 0, 0, 40)
        self.add_player_button = Button(add_player_rect, "+",
                                        self.button_font)
        remove_player_rect = pygame.Rect(0, 0, 0, 40)
        self.remove_player_button = Button(remove_player_rect, "−",
                                           self.button_font)

        self.player_list_y = 0

        self._build_player_fields()

        self.game_label_y = 0

        self.ai_difficulty_dropdown = Dropdown(
            rect=(x_center, 0, 200, 40),
            font=self.dropdown_font,
            options=["EASY", "NORMAL", "HARD", "EXPERT"],
            default_index=1,
            on_select=self._handle_ai_difficulty_change)

        self.card_set_label_y = 0

        self.available_card_sets = get_available_card_sets()
        self.default_card_sets = settings_manager.get("SELECTED_CARD_SETS",
                                                      ["base_game"])
        self.selected_card_sets = list(self.default_card_sets)
        self.card_set_checkboxes = []
        self.card_set_section_y = 0

        sorted_card_sets = sorted(
            self.available_card_sets,
            key=lambda x: (
                x['name'] not in self.default_card_sets,
                x.get('display_name', x['name']).lower(),
            ))

        for card_set in sorted_card_sets:
            is_default = card_set['name'] in self.default_card_sets
            checkbox = Checkbox(
                rect=(x_center, 0, 20, 20),
                checked=is_default,
                on_toggle=lambda checked, name=card_set[
                    'name']: self._toggle_card_set(name, checked))
            if is_default:
                checkbox.set_disabled(True)
            self.card_set_checkboxes.append((card_set, checkbox))

        self.network_label_y = 0

        self.network_modes = ["local", "host", "client"]
        default_index = self.network_modes.index(network_mode)
        self.network_mode_dropdown = Dropdown(
            rect=(x_center, 0, 200, 40),
            font=self.dropdown_font,
            options=self.network_modes,
            default_index=default_index,
            on_select=self._handle_network_mode_change)

        self.host_ip_field = InputField(rect=(x_center, 0, 200, 40),
                                        font=self.input_font)
        self.host_ip_field.set_text(host_ip)

        self.port_field = InputField(rect=(x_center, 0, 200, 40),
                                     font=self.input_font)
        self.port_field.set_text(port)

        start_rect = pygame.Rect(0, 0, 0, 60)
        self.start_button = Button(start_rect, "Start game", self.button_font)
        back_rect = pygame.Rect(0, 0, 0, 60)
        self.back_button = Button(back_rect, "Back", self.button_font)

        self._handle_network_mode_change(network_mode)

    def _get_enabled_players_count(self):
        """Get count of enabled players"""
        return sum(1 for player in self.players if player.enabled)

    def _build_player_fields(self) -> None:
        """Build UI fields based on current player data (single source of truth)"""
        self.player_fields = []

        x_center = self.screen.get_width() // 2 - 100
        for i, player in enumerate(self.players):

            def _make_text_change_handler(index):

                def _handler(new_text):
                    lowered = new_text.lower()
                    forbidden_found = None
                    for word in FORBIDDEN_WORDS:
                        if word in lowered:
                            forbidden_found = word
                            break
                    if forbidden_found:
                        if index < len(self.original_player_names):
                            default_name = self.original_player_names[index]
                        else:
                            default_name = f"Player {index + 1}"
                        self.players[index].set_name(default_name)
                        if hasattr(self, 'player_fields') and len(
                                self.player_fields) > index:
                            name_field = self.player_fields[index][0]
                            name_field.set_text(default_name)
                        self.add_toast(
                            Toast(
                                f"Forbidden word detected in name. Reset to default.",
                                type="error"))
                        if hasattr(self, 'player_fields') and len(
                                self.player_fields) > index:
                            ai_checkbox = self.player_fields[index][1]
                            if ai_checkbox:
                                ai_checkbox.set_checked(
                                    self.players[index].is_ai)
                        return
                    self.players[index].set_name(new_text)
                    if hasattr(self, 'player_fields') and len(
                            self.player_fields) > index:
                        ai_checkbox = self.player_fields[index][1]
                        if ai_checkbox:
                            ai_checkbox.set_checked(self.players[index].is_ai)

                return _handler

            name_field = InputField(
                rect=(x_center, 0, 200, 40),
                font=self.input_font,
                on_text_change=_make_text_change_handler(i))

            if self.network_mode == "client" and i > 0:
                name_field.set_text("")
                name_field.set_disabled(True)
            else:
                name_field.set_text(player.get_display_name())
                name_field.set_disabled(not player.enabled)
                if i > 0 and self.network_mode == "host":
                    name_field.set_read_only(True)

            ai_checkbox = None

            if i == 0:
                can_toggle_ai = settings_manager.get("DEBUG", False)
                ai_checkbox = Checkbox(
                    rect=(0, 0, 20, 20),
                    checked=player.is_ai,
                    on_toggle=(lambda value, index=i: self._toggle_player_ai(
                        index, value)) if can_toggle_ai else None)
                ai_checkbox.set_disabled(not player.enabled
                                         or not can_toggle_ai)

            elif i != 0:
                can_toggle_ai = (self.network_mode == "local")
                ai_checkbox = Checkbox(
                    rect=(0, 0, 20, 20),
                    checked=player.is_ai,
                    on_toggle=(lambda value, index=i: self._toggle_player_ai(
                        index, value)) if can_toggle_ai else None)
                ai_checkbox.set_disabled(not player.enabled
                                         or not can_toggle_ai)

            self.player_fields.append((name_field, ai_checkbox))

    def _layout_player_fields(self, start_y: int, padding: int,
                              x_center: int) -> int:
        current_y = start_y
        for name_field, ai_checkbox in self.player_fields:
            width, field_height = name_field.rect.size
            name_field.rect = pygame.Rect(x_center, current_y, width,
                                          field_height)
            if ai_checkbox:
                checkbox_width, checkbox_height = ai_checkbox.rect.size
                checkbox_x = name_field.rect.right + 10
                checkbox_y = current_y + (field_height - checkbox_height) // 2
                ai_checkbox.rect = pygame.Rect(checkbox_x, checkbox_y,
                                               checkbox_width, checkbox_height)
            current_y += field_height + padding
        return current_y

    def _layout_controls(self) -> None:
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        section_gap = theme.THEME_LAYOUT_SECTION_GAP
        x_center = self.screen.get_width() // 2 - 100
        button_center_x = self.screen.get_width() // 2
        self.header_height = self._get_scene_header_height(
            self.font.get_height()
        )
        current_y = self.header_height + section_gap

        self.player_label_y = current_y
        current_y += self.section_header_font.get_height() + section_gap

        self.player_list_y = current_y
        current_y = self._layout_player_fields(current_y, padding, x_center)

        if self.player_fields:
            players_center_y = self.player_fields[0][0].rect.centery
        else:
            players_center_y = current_y + self.add_player_button.rect.height // 2

        add_width, add_height = self.add_player_button.rect.size
        self.add_player_button.rect = pygame.Rect(0, 0, add_width, add_height)
        self.add_player_button.rect.center = (
            self.screen.get_width() // 2 + 200, players_center_y)

        remove_width, remove_height = self.remove_player_button.rect.size
        self.remove_player_button.rect = pygame.Rect(0, 0, remove_width,
                                                     remove_height)
        self.remove_player_button.rect.center = (
            self.screen.get_width() // 2 + 250, players_center_y)

        self.game_label_y = current_y
        current_y += self.section_header_font.get_height() + section_gap

        dropdown_width, dropdown_height = self.ai_difficulty_dropdown.rect.size
        self.ai_difficulty_dropdown.rect = pygame.Rect(
            x_center, current_y, dropdown_width, dropdown_height)
        current_y += dropdown_height + padding

        self.card_set_label_y = current_y
        current_y += self.section_header_font.get_height() + section_gap

        self.card_set_section_y = current_y
        for _, checkbox in self.card_set_checkboxes:
            checkbox_width, checkbox_height = checkbox.rect.size
            checkbox.rect = pygame.Rect(x_center, current_y, checkbox_width,
                                        checkbox_height)
            current_y += checkbox_height + padding

        self.network_label_y = current_y
        current_y += self.section_header_font.get_height() + section_gap

        network_width, network_height = self.network_mode_dropdown.rect.size
        self.network_mode_dropdown.rect = pygame.Rect(
            x_center, current_y, network_width, network_height)
        current_y += network_height + padding

        host_width, host_height = self.host_ip_field.rect.size
        self.host_ip_field.rect = pygame.Rect(x_center, current_y, host_width,
                                              host_height)
        current_y += host_height + padding

        port_width, port_height = self.port_field.rect.size
        self.port_field.rect = pygame.Rect(x_center, current_y, port_width,
                                           port_height)
        current_y += port_height + padding

        current_y += theme.THEME_LAYOUT_BUTTON_SECTION_GAP
        start_width, start_height = self.start_button.rect.size
        self.start_button.rect = pygame.Rect(0, 0, start_width, start_height)
        self.start_button.rect.center = (button_center_x,
                                         current_y + start_height // 2)
        current_y += start_height + padding

        back_width, back_height = self.back_button.rect.size
        self.back_button.rect = pygame.Rect(0, 0, back_width, back_height)
        self.back_button.rect.center = (button_center_x,
                                        current_y + back_height // 2)

    def _get_label_surface(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
    ) -> pygame.Surface:
        cache_key = (id(font), text, color)
        cached = self._label_surfaces.get(cache_key)
        if cached is None:
            cached = font.render(text, True, color)
            self._label_surfaces[cache_key] = cached
        return cached

    def _toggle_player_ai(self, index: int, value: bool) -> None:
        """Toggle AI status for a player"""
        self.players[index].set_ai(value)

        name_field = self.player_fields[index][0]
        name_field.set_text(self.players[index].get_display_name())

        player = self.players[index]
        if value:
            current_difficulty = self.ai_difficulty_dropdown.get_selected()
            base_name = player.name
            if base_name.startswith("AI_EASY_"):
                base_name = base_name[8:]
            elif base_name.startswith("AI_HARD_"):
                base_name = base_name[8:]
            elif base_name.startswith("AI_EXPERT_"):
                base_name = base_name[10:]
            elif base_name.startswith("AI_NORMAL_"):
                base_name = base_name[10:]
            elif base_name.startswith("AI_"):
                base_name = base_name[3:]

            player.name = f"AI_{current_difficulty}_{base_name}"
            name_field.set_text(player.get_display_name())

    def _handle_ai_difficulty_change(self, difficulty: str) -> None:
        """Handle AI difficulty change for all AI players"""
        for i, player in enumerate(self.players):
            if player.is_ai:
                base_name = player.name
                if base_name.startswith("AI_EASY_"):
                    base_name = base_name[8:]
                elif base_name.startswith("AI_HARD_"):
                    base_name = base_name[8:]
                elif base_name.startswith("AI_EXPERT_"):
                    base_name = base_name[10:]
                elif base_name.startswith("AI_NORMAL_"):
                    base_name = base_name[10:]
                elif base_name.startswith("AI_"):
                    base_name = base_name[3:]

                player.name = f"AI_{difficulty}_{base_name}"

                if i < len(self.player_fields):
                    name_field = self.player_fields[i][0]
                    name_field.set_text(player.get_display_name())

    def _handle_network_mode_change(self, mode: str) -> None:
        """Handle network mode change"""
        self.network_mode = mode
        is_local = mode == "local"

        if not is_local:
            for i, player in enumerate(self.players):
                if i > 0:
                    base_name = player.name
                    if base_name.startswith("AI_EASY_"):
                        base_name = base_name[8:]
                    elif base_name.startswith("AI_HARD_"):
                        base_name = base_name[8:]
                    elif base_name.startswith("AI_EXPERT_"):
                        base_name = base_name[10:]
                    elif base_name.startswith("AI_NORMAL_"):
                        base_name = base_name[10:]
                    elif base_name.startswith("AI_"):
                        base_name = base_name[3:]

                    player.name = base_name
                    player.set_ai(False)

        if mode == "host":
            host_value = self.local_ip
        elif is_local:
            host_value = None
        else:
            host_value = settings_manager.get("HOST_IP", "0.0.0.0")

        self.host_ip_field.set_text(host_value or "")
        self.host_ip_field.set_disabled(is_local)
        self.port_field.set_disabled(is_local)

        self.ai_difficulty_dropdown.set_disabled(not is_local)

        is_client = mode == "client"
        for card_set, checkbox in self.card_set_checkboxes:
            if card_set['name'] not in self.default_card_sets:
                checkbox.set_disabled(is_client)

        self._build_player_fields()
        self._layout_controls()
        self._layout_controls()

    def _toggle_card_set(self, set_name: str, checked: bool) -> None:
        """Handle card set selection toggle"""
        if checked and set_name not in self.selected_card_sets:
            self.selected_card_sets.append(set_name)
        elif not checked and set_name in self.selected_card_sets:
            self.selected_card_sets.remove(set_name)

        settings_manager.set("SELECTED_CARD_SETS",
                             self.selected_card_sets,
                             temporary=True)

    def _add_player_field(self) -> None:
        """Add a new player"""
        enabled_count = self._get_enabled_players_count()
        if enabled_count >= 6:
            self.add_toast(Toast("Maximum 6 players allowed", type="warning"))
            return

        for player in self.players:
            if not player.enabled:
                player.enabled = True
                break

        self._build_player_fields()
        self._layout_controls()

    def _remove_player_field(self) -> None:
        """Remove a player"""
        enabled_count = self._get_enabled_players_count()
        if enabled_count <= 2:
            self.add_toast(Toast("At least 2 players required",
                                 type="warning"))
            return

        for i in reversed(range(len(self.players))):
            if self.players[i].enabled:
                self.players[i].enabled = False
                if i < len(self.original_player_names):
                    self.players[i].name = self.original_player_names[i]
                else:
                    self.players[i].name = f"Player {i + 1}"
                self.players[i].is_ai = False
                break

        self._build_player_fields()
        self._layout_controls()

    def _apply_settings_and_start(self) -> None:
        """Apply settings and start the game"""
        player_names = []
        for player in self.players:
            if player.enabled:
                player_names.append(player.get_display_name())

        settings_manager.set("PLAYERS", player_names, temporary=True)
        settings_manager.set("NETWORK_MODE",
                             self.network_mode_dropdown.get_selected(),
                             temporary=True)
        settings_manager.set("HOST_IP",
                             self.host_ip_field.get_text(),
                             temporary=True)

        selected_card_sets = []
        for card_set, checkbox in self.card_set_checkboxes:
            if checkbox.is_checked():
                selected_card_sets.append(card_set['name'])
        settings_manager.set("SELECTED_CARD_SETS",
                             selected_card_sets,
                             temporary=True)

        if self.network_mode_dropdown.get_selected() != "local":
            try:
                port = int(self.port_field.get_text())
                if not (1024 <= port <= 65535):
                    raise ValueError
                settings_manager.set("HOST_PORT", port, temporary=True)
            except ValueError:
                self.add_toast(Toast("Invalid port number", type="error"))
                return
        network_mode = self.network_mode_dropdown.get_selected()
        if network_mode == "local":
            self.switch_scene("start_game", player_names)
        else:
            self.switch_scene("start_lobby", player_names)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self._apply_scroll(events)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switch_scene(GameState.MENU)

            if self.network_mode_dropdown.handle_event(
                    event, y_offset=self.scroll_offset):
                continue

            if self.ai_difficulty_dropdown.handle_event(
                    event, y_offset=self.scroll_offset):
                continue

            self.host_ip_field.handle_event(event, y_offset=self.scroll_offset)
            self.port_field.handle_event(event, y_offset=self.scroll_offset)

            for card_set, checkbox in self.card_set_checkboxes:
                if checkbox.handle_event(event, y_offset=self.scroll_offset):
                    continue

            for name_field, ai_checkbox in self.player_fields:
                name_field.handle_event(event, y_offset=self.scroll_offset)
                if ai_checkbox:
                    ai_checkbox.handle_event(event,
                                             y_offset=self.scroll_offset)

            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                self.back_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.start_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                self.add_player_button.handle_event(
                    event, y_offset=self.scroll_offset)
                self.remove_player_button.handle_event(
                    event, y_offset=self.scroll_offset)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.back_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.start_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                self.add_player_button.handle_event(
                    event, y_offset=self.scroll_offset)
                self.remove_player_button.handle_event(
                    event, y_offset=self.scroll_offset)
                if self.back_button._is_clicked(event.pos,
                                                y_offset=self.scroll_offset):
                    self.switch_scene(GameState.MENU)
                elif self.start_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    self._apply_settings_and_start()
                elif self.add_player_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    self._add_player_field()
                elif self.remove_player_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    self._remove_player_field()

    def draw(self) -> None:
        self._draw_background(
            background_color=theme.THEME_PREPARE_BACKGROUND_COLOR,
            image_name=theme.THEME_PREPARE_BACKGROUND_IMAGE,
            scale_mode=theme.THEME_PREPARE_BACKGROUND_SCALE_MODE,
            tint_color=theme.THEME_PREPARE_BACKGROUND_TINT_COLOR,
            blur_radius=theme.THEME_PREPARE_BACKGROUND_BLUR_RADIUS,
        )
        offset_y = self.scroll_offset

        if (self._title_surface is None
                or self._cached_title_text != self._title_text):
            self._title_surface = self.font.render(
                self._title_text, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            self._cached_title_text = self._title_text

        player_label = self._section_header_surfaces.get("Players")
        if player_label is None:
            player_label = self.section_header_font.render(
                "Players", True, theme.THEME_SECTION_HEADER_COLOR
            )
            self._section_header_surfaces["Players"] = player_label
        player_label_rect = player_label.get_rect()
        player_label_rect.centerx = self.screen.get_width() // 2
        player_label_rect.y = self.player_label_y + offset_y
        self.screen.blit(player_label, player_label_rect)

        game_label = self._section_header_surfaces.get("Game")
        if game_label is None:
            game_label = self.section_header_font.render(
                "Game", True, theme.THEME_SECTION_HEADER_COLOR)
            self._section_header_surfaces["Game"] = game_label
        game_label_rect = game_label.get_rect()
        game_label_rect.centerx = self.screen.get_width() // 2
        game_label_rect.y = self.game_label_y + offset_y
        self.screen.blit(game_label, game_label_rect)

        card_set_label = self._section_header_surfaces.get("Card Sets")
        if card_set_label is None:
            card_set_label = self.section_header_font.render(
                "Card Sets", True, theme.THEME_SECTION_HEADER_COLOR)
            self._section_header_surfaces["Card Sets"] = card_set_label
        card_set_label_rect = card_set_label.get_rect()
        card_set_label_rect.centerx = self.screen.get_width() // 2
        card_set_label_rect.y = self.card_set_label_y + offset_y
        self.screen.blit(card_set_label, card_set_label_rect)

        network_label = self._section_header_surfaces.get("Network")
        if network_label is None:
            network_label = self.section_header_font.render(
                "Network", True, theme.THEME_SECTION_HEADER_COLOR)
            self._section_header_surfaces["Network"] = network_label
        network_label_rect = network_label.get_rect()
        network_label_rect.centerx = self.screen.get_width() // 2
        network_label_rect.y = self.network_label_y + offset_y
        self.screen.blit(network_label, network_label_rect)

        label_font = self.dropdown_font

        for i, (name_field, ai_checkbox) in enumerate(self.player_fields):
            label_text = "Your name:" if i == 0 else f"Player {i + 1}:"
            label = self._get_label_surface(
                label_font, label_text, theme.THEME_TEXT_COLOR_LIGHT)
            label_rect = label.get_rect(right=name_field.rect.left - 10,
                                        centery=name_field.rect.centery +
                                        offset_y)
            self.screen.blit(label, label_rect)
            name_field.draw(self.screen, y_offset=offset_y)
            ai_checkbox.draw(self.screen, y_offset=offset_y)

        net_label = self._get_label_surface(
            label_font, "Network mode:", theme.THEME_TEXT_COLOR_LIGHT)
        net_label_rect = net_label.get_rect(
            right=self.network_mode_dropdown.rect.left - 10,
            centery=self.network_mode_dropdown.rect.centery + offset_y)
        self.screen.blit(net_label, net_label_rect)

        ai_label = self._get_label_surface(
            label_font, "AI Difficulty:", theme.THEME_TEXT_COLOR_LIGHT)
        ai_label_rect = ai_label.get_rect(
            right=self.ai_difficulty_dropdown.rect.left - 10,
            centery=self.ai_difficulty_dropdown.rect.centery + offset_y)
        self.screen.blit(ai_label, ai_label_rect)

        for card_set, checkbox in self.card_set_checkboxes:
            checkbox.draw(self.screen, y_offset=offset_y)
            card_set_text = self._get_label_surface(
                label_font,
                f"{card_set['display_name']} ({card_set['card_count']} cards):",
                theme.THEME_TEXT_COLOR_LIGHT,
            )
            card_set_rect = card_set_text.get_rect(
                right=checkbox.rect.left - 10,
                centery=checkbox.rect.centery + offset_y)
            self.screen.blit(card_set_text, card_set_rect)

        ip_label = self._get_label_surface(
            label_font, "Host IP:", theme.THEME_TEXT_COLOR_LIGHT)
        ip_label_rect = ip_label.get_rect(
            right=self.host_ip_field.rect.left - 10,
            centery=self.host_ip_field.rect.centery + offset_y)
        self.screen.blit(ip_label, ip_label_rect)
        self.host_ip_field.draw(self.screen, y_offset=offset_y)

        port_label = self._get_label_surface(
            label_font, "Port:", theme.THEME_TEXT_COLOR_LIGHT)
        port_label_rect = port_label.get_rect(
            right=self.port_field.rect.left - 10,
            centery=self.port_field.rect.centery + offset_y)
        self.screen.blit(port_label, port_label_rect)
        self.port_field.draw(self.screen, y_offset=offset_y)

        self.add_player_button.draw(self.screen, y_offset=offset_y)
        self.remove_player_button.draw(self.screen, y_offset=offset_y)
        self.back_button.draw(self.screen, y_offset=offset_y)
        self.start_button.draw(self.screen, y_offset=offset_y)

        self.max_scroll = max(
            self.screen.get_height(),
            self.back_button.rect.bottom + theme.THEME_LAYOUT_SECTION_GAP * 2,
        )

        self.toast_manager.draw(self.screen)
        self._draw_dropdowns(
            [self.ai_difficulty_dropdown, self.network_mode_dropdown],
            y_offset=offset_y,
        )
        self._draw_dropdowns(
            [self.ai_difficulty_dropdown, self.network_mode_dropdown],
            y_offset=offset_y,
            expanded_only=True,
        )
        self._draw_scene_header(self._title_surface)

    def refresh_theme(self, theme_name: str | None = None) -> None:
        """Refresh fonts and component styling after theme changes."""
        super().refresh_theme(theme_name)
        self.font = theme.get_font("title", theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.section_header_font = theme.get_font(
            "section_header", theme.THEME_FONT_SIZE_SECTION_HEADER
        )
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.input_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.dropdown_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self._title_surface = None
        self._cached_title_text = None
        self._section_header_surfaces.clear()
        self._label_surfaces.clear()

        self.add_player_button.set_font(self.button_font)
        self.add_player_button.apply_theme()
        self.remove_player_button.set_font(self.button_font)
        self.remove_player_button.apply_theme()
        self.start_button.set_font(self.button_font)
        self.start_button.apply_theme()
        self.back_button.set_font(self.button_font)
        self.back_button.apply_theme()

        self.host_ip_field.set_font(self.input_font)
        self.host_ip_field.apply_theme()
        self.port_field.set_font(self.input_font)
        self.port_field.apply_theme()

        self.ai_difficulty_dropdown.set_font(self.dropdown_font)
        self.ai_difficulty_dropdown.apply_theme()
        self.network_mode_dropdown.set_font(self.dropdown_font)
        self.network_mode_dropdown.apply_theme()

        for checkbox in self.card_set_checkboxes:
            checkbox[1].apply_theme()

        if hasattr(self, "player_fields"):
            for name_field, ai_checkbox in self.player_fields:
                name_field.set_font(self.input_font)
                name_field.apply_theme()
                if ai_checkbox is not None:
                    ai_checkbox.apply_theme()

        self.toast_manager.apply_theme()
        self._layout_controls()

    def add_toast(self, toast):
        self.toast_manager.add_toast(toast)
