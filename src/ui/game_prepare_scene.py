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

        self.font = pygame.font.Font(None, 80)
        self.button_font = pygame.font.Font(None, 48)
        self.input_font = pygame.font.Font(None, 36)
        self.dropdown_font = pygame.font.Font(None, 36)

        self.toast_manager = ToastManager(max_toasts=5)

        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30

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
        current_y = 60

        self.title_y = current_y
        current_y += 60

        self.player_label_y = current_y
        current_y += 50

        self.add_player_button = Button(
            (self.screen.get_width() // 2 + 180, current_y + 60, 40, 40), "+",
            self.button_font)
        self.remove_player_button = Button(
            (self.screen.get_width() // 2 + 230, current_y + 60, 40, 40), "−",
            self.button_font)

        self.player_list_y = current_y

        self._build_player_fields()
        current_y += 300 + 40

        self.game_label_y = current_y
        current_y += 50

        self.ai_difficulty_dropdown = Dropdown(
            rect=(x_center, current_y, 200, 40),
            font=self.dropdown_font,
            options=["EASY", "NORMAL", "HARD", "EXPERT"],
            default_index=1,
            on_select=self._handle_ai_difficulty_change)
        current_y += 80

        self.card_set_label_y = current_y
        current_y += 50

        self.available_card_sets = get_available_card_sets()
        self.default_card_sets = settings_manager.get("SELECTED_CARD_SETS",
                                                      ["base_game"])
        self.selected_card_sets = list(self.default_card_sets)
        self.card_set_checkboxes = []
        self.card_set_section_y = current_y

        sorted_card_sets = sorted(
            self.available_card_sets,
            key=lambda x: (x['name'] not in self.default_card_sets, x['name']))

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

        card_set_count = len(self.available_card_sets)
        current_y += 30 * card_set_count + 80

        self.network_label_y = current_y
        current_y += 50

        self.network_modes = ["local", "host", "client"]
        default_index = self.network_modes.index(network_mode)
        self.network_mode_dropdown = Dropdown(
            rect=(x_center, current_y, 200, 40),
            font=self.dropdown_font,
            options=self.network_modes,
            default_index=default_index,
            on_select=self._handle_network_mode_change)
        current_y += 60

        self.host_ip_field = InputField(rect=(x_center, current_y, 200, 40),
                                        font=self.input_font)
        self.host_ip_field.set_text(host_ip)
        current_y += 60

        self.port_field = InputField(rect=(x_center, current_y, 200, 40),
                                     font=self.input_font)
        self.port_field.set_text(port)
        current_y += 80

        self.start_button = Button((x_center, current_y, 200, 60),
                                   "Start Game", self.button_font)
        current_y += 80
        self.back_button = Button((x_center, current_y, 200, 60), "Back",
                                  self.button_font)

        self._handle_network_mode_change(network_mode)

    def _get_enabled_players_count(self):
        """Get count of enabled players"""
        return sum(1 for player in self.players if player.enabled)

    def _build_player_fields(self) -> None:
        """Build UI fields based on current player data (single source of truth)"""
        self.player_fields = []

        for i, player in enumerate(self.players):
            y = self.player_list_y + (i * 50 if i == 0 else 60 + (i - 1) * 50)

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
                rect=(self.screen.get_width() // 2 - 100, y, 200, 40),
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
                    rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                    checked=player.is_ai,
                    on_toggle=(lambda value, index=i: self._toggle_player_ai(
                        index, value)) if can_toggle_ai else None)
                ai_checkbox.set_disabled(not player.enabled
                                         or not can_toggle_ai)

            elif i != 0:
                can_toggle_ai = (self.network_mode == "local")
                ai_checkbox = Checkbox(
                    rect=(self.screen.get_width() // 2 + 110, y + 10, 20, 20),
                    checked=player.is_ai,
                    on_toggle=(lambda value, index=i: self._toggle_player_ai(
                        index, value)) if can_toggle_ai else None)
                ai_checkbox.set_disabled(not player.enabled
                                         or not can_toggle_ai)

            self.player_fields.append((name_field, ai_checkbox))

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
                if checkbox.handle_event(event, y_offset=0):
                    continue

            for name_field, ai_checkbox in self.player_fields:
                name_field.handle_event(event, y_offset=self.scroll_offset)
                if ai_checkbox:
                    ai_checkbox.handle_event(event,
                                             y_offset=self.scroll_offset)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        self.screen.fill((30, 30, 30))
        offset_y = self.scroll_offset

        title_text = self.font.render("Game Setup", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2,
                                                 self.title_y + offset_y))
        self.screen.blit(title_text, title_rect)

        player_label = self.dropdown_font.render("Players", True,
                                                 (255, 215, 0))
        player_label_rect = player_label.get_rect()
        player_label_rect.centerx = self.screen.get_width() // 2
        player_label_rect.y = self.player_label_y + offset_y
        self.screen.blit(player_label, player_label_rect)

        game_label = self.dropdown_font.render("Game", True, (255, 215, 0))
        game_label_rect = game_label.get_rect()
        game_label_rect.centerx = self.screen.get_width() // 2
        game_label_rect.y = self.game_label_y + offset_y
        self.screen.blit(game_label, game_label_rect)

        card_set_label = self.dropdown_font.render("Card Sets", True,
                                                   (255, 215, 0))
        card_set_label_rect = card_set_label.get_rect()
        card_set_label_rect.centerx = self.screen.get_width() // 2
        card_set_label_rect.y = self.card_set_label_y + offset_y
        self.screen.blit(card_set_label, card_set_label_rect)

        network_label = self.dropdown_font.render("Network", True,
                                                  (255, 215, 0))
        network_label_rect = network_label.get_rect()
        network_label_rect.centerx = self.screen.get_width() // 2
        network_label_rect.y = self.network_label_y + offset_y
        self.screen.blit(network_label, network_label_rect)

        label_font = self.dropdown_font

        for i, (name_field, ai_checkbox) in enumerate(self.player_fields):
            label_text = "Your name:" if i == 0 else f"Player {i + 1}:"
            label = label_font.render(label_text, True, (255, 255, 255))
            label_rect = label.get_rect(right=name_field.rect.left - 10,
                                        centery=name_field.rect.centery +
                                        offset_y)
            self.screen.blit(label, label_rect)
            name_field.draw(self.screen, y_offset=offset_y)
            ai_checkbox.draw(self.screen, y_offset=offset_y)

        net_label = label_font.render("Network mode:", True, (255, 255, 255))
        net_label_rect = net_label.get_rect(
            right=self.network_mode_dropdown.rect.left - 10,
            centery=self.network_mode_dropdown.rect.centery + offset_y)
        self.screen.blit(net_label, net_label_rect)

        ai_label = label_font.render("AI Difficulty:", True, (255, 255, 255))
        ai_label_rect = ai_label.get_rect(
            right=self.ai_difficulty_dropdown.rect.left - 10,
            centery=self.ai_difficulty_dropdown.rect.centery + offset_y)
        self.screen.blit(ai_label, ai_label_rect)

        for i, (card_set, checkbox) in enumerate(self.card_set_checkboxes):
            y = self.card_set_section_y + 20 + i * 30 + offset_y
            checkbox.rect.x = self.ai_difficulty_dropdown.rect.x
            checkbox.rect.y = y - 10
            checkbox.draw(self.screen, y_offset=0)
            card_set_text = label_font.render(
                f"{card_set['display_name']} ({card_set['card_count']} cards):",
                True, (255, 255, 255))
            card_set_rect = card_set_text.get_rect(
                right=checkbox.rect.left - 10, centery=checkbox.rect.centery)
            self.screen.blit(card_set_text, card_set_rect)

        ip_label = label_font.render("Host IP:", True, (255, 255, 255))
        ip_label_rect = ip_label.get_rect(
            right=self.host_ip_field.rect.left - 10,
            centery=self.host_ip_field.rect.centery + offset_y)
        self.screen.blit(ip_label, ip_label_rect)
        self.host_ip_field.draw(self.screen, y_offset=offset_y)

        port_label = label_font.render("Port:", True, (255, 255, 255))
        port_label_rect = port_label.get_rect(
            right=self.port_field.rect.left - 10,
            centery=self.port_field.rect.centery + offset_y)
        self.screen.blit(port_label, port_label_rect)
        self.port_field.draw(self.screen, y_offset=offset_y)

        self.ai_difficulty_dropdown.draw(self.screen, y_offset=offset_y)
        self.network_mode_dropdown.draw(self.screen, y_offset=offset_y)
        self.add_player_button.draw(self.screen, y_offset=offset_y)
        self.remove_player_button.draw(self.screen, y_offset=offset_y)
        self.back_button.draw(self.screen, y_offset=offset_y)
        self.start_button.draw(self.screen, y_offset=offset_y)

        self.max_scroll = max(self.screen.get_height(),
                              self.back_button.rect.bottom + 80)

        self.toast_manager.draw(self.screen)

        pygame.display.flip()

    def add_toast(self, toast):
        self.toast_manager.add_toast(toast)
