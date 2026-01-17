import pygame
from ui.scene import Scene
from game_state import GameState
from ui.components.button import Button
from ui.components.input_field import InputField
from ui.components.dropdown import Dropdown
from ui.components.toast import Toast, ToastManager
from ui.components.checkbox import Checkbox
from ui.components.slider import Slider
from utils.settings_manager import settings_manager
from ui import theme
import typing


class SettingsScene(Scene):

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)
        self.font = theme.get_font("title", theme.THEME_FONT_SIZE_SCENE_TITLE)
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

        settings_manager.subscribe("FULLSCREEN", self._on_fullscreen_changed)
        settings_manager.subscribe("DEBUG", self._on_debug_changed)

        current_resolution = f"{settings_manager.get('WINDOW_WIDTH')}x{settings_manager.get('WINDOW_HEIGHT')}"
        x_center = screen.get_width() // 2 - 100
        button_center_x = screen.get_width() // 2
        self.header_height = self._get_scene_header_height(
            self.font.get_height()
        )
        current_y = self.header_height + theme.THEME_LAYOUT_VERTICAL_GAP

        # ===== DISPLAY SETTINGS =====
        self.display_label_y = current_y
        current_y += (self.dropdown_font.get_height()
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        resolution_options = [
            "800x600", "1024x768", "1280x720", "1366x768", "1600x900",
            "1920x1080", "2560x1440", "3840x2160"
        ]
        default_index = resolution_options.index(
            current_resolution
        ) if current_resolution in resolution_options else 0

        self.resolution_dropdown = Dropdown(
            rect=(x_center, current_y, 200, 40),
            font=self.dropdown_font,
            options=resolution_options,
            default_index=default_index,
            on_select=lambda value: self.add_toast(
                Toast("In order to apply resolution setting, restart the game",
                      type="warning")),
        )
        self.resolution_dropdown.set_disabled(
            settings_manager.get("FULLSCREEN"))
        current_y += (self.resolution_dropdown.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.fullscreen_checkbox = Checkbox(
            rect=(x_center, current_y, 20, 20),
            checked=settings_manager.get("FULLSCREEN"),
            on_toggle=lambda value: [
                self._handle_fullscreen_toggle(value),
                self.add_toast(
                    Toast(
                        "In order to apply fullscreen setting, restart the game",
                        type="warning"))
            ])
        current_y += (self.fullscreen_checkbox.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        # ===== GAME SETTINGS =====
        self.game_label_y = current_y
        current_y += (self.dropdown_font.get_height()
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.valid_placement_checkbox = Checkbox(
            rect=(x_center, current_y, 20, 20),
            checked=settings_manager.get("SHOW_VALID_PLACEMENTS", True),
            on_toggle=lambda value: self._handle_valid_placement_toggle(value))
        current_y += (self.valid_placement_checkbox.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        # ===== DEBUG SETTINGS =====
        self.debug_label_y = current_y
        current_y += (self.dropdown_font.get_height()
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.log_to_console_checkbox = Checkbox(
            rect=(x_center, current_y, 20, 20),
            checked=settings_manager.get("LOG_TO_CONSOLE", True),
            on_toggle=lambda value: [
                self._handle_log_to_console_toggle(value),
                self.add_toast(
                    Toast(
                        "In order to apply log to console setting, restart the game",
                        type="warning"))
            ])
        self.log_to_console_checkbox.set_disabled(
            not settings_manager.get("DEBUG"))
        current_y += (self.log_to_console_checkbox.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.fps_slider = Slider(rect=(x_center, current_y, 180, 20),
                                 font=self.dropdown_font,
                                 min_value=30,
                                 max_value=240,
                                 value=settings_manager.get("FPS", 60),
                                 on_change=None)
        self.fps_slider.set_disabled(not settings_manager.get("DEBUG"))
        current_y += (self.fps_slider.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.grid_size_slider = Slider(rect=(x_center, current_y, 180, 20),
                                       font=self.dropdown_font,
                                       min_value=10,
                                       max_value=50,
                                       value=settings_manager.get(
                                           "GRID_SIZE", 20),
                                       on_change=None)
        self.grid_size_slider.set_disabled(not settings_manager.get("DEBUG"))
        current_y += (self.grid_size_slider.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.tile_size_slider = Slider(rect=(x_center, current_y, 180, 20),
                                       font=self.dropdown_font,
                                       min_value=50,
                                       max_value=150,
                                       value=settings_manager.get("TILE_SIZE"),
                                       on_change=None)
        self.tile_size_slider.set_disabled(not settings_manager.get("DEBUG"))
        current_y += (self.tile_size_slider.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.figure_size_slider = Slider(
            rect=(x_center, current_y, 180, 20),
            font=self.dropdown_font,
            min_value=10,
            max_value=50,
            value=settings_manager.get("FIGURE_SIZE"),
            on_change=None)
        self.figure_size_slider.set_disabled(not settings_manager.get("DEBUG"))
        current_y += (self.figure_size_slider.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        current_tile_size = settings_manager.get("TILE_SIZE")
        current_sidebar_width = settings_manager.get("SIDEBAR_WIDTH")
        min_sidebar_width = current_tile_size + 20
        self.sidebar_width_slider = Slider(rect=(x_center, current_y, 180, 20),
                                           font=self.dropdown_font,
                                           min_value=min_sidebar_width,
                                           max_value=400,
                                           value=max(current_sidebar_width,
                                                     min_sidebar_width),
                                           on_change=None)
        self.sidebar_width_slider.set_disabled(
            not settings_manager.get("DEBUG"))
        current_y += (self.sidebar_width_slider.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.game_log_max_entries_field = InputField(
            rect=(x_center, current_y, 200, 40),
            font=self.input_font,
            initial_text=str(settings_manager.get("GAME_LOG_MAX_ENTRIES",
                                                  2000)),
            on_text_change=lambda value: self.add_toast(
                Toast(
                    "In order to apply game log max entries setting, restart the game",
                    type="warning")),
            numeric=True,
            min_value=100,
            max_value=50000)
        self.game_log_max_entries_field.set_disabled(
            not settings_manager.get("DEBUG"))
        current_y += (self.game_log_max_entries_field.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        # ===== AI SETTINGS =====
        self.ai_label_y = current_y
        current_y += (self.dropdown_font.get_height()
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.ai_simulation_checkbox = Checkbox(
            rect=(x_center, current_y, 20, 20),
            checked=settings_manager.get("AI_USE_SIMULATION", False),
            on_toggle=lambda value: self._handle_ai_simulation_toggle(value))
        self.ai_simulation_checkbox.set_disabled(
            not settings_manager.get("DEBUG"))
        current_y += (self.ai_simulation_checkbox.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.ai_strategic_candidates_field = InputField(
            rect=(x_center, current_y, 80, 40),
            font=self.input_font,
            initial_text=str(settings_manager.get("AI_STRATEGIC_CANDIDATES",
                                                  3)),
            on_text_change=None,
            numeric=True,
            min_value=-1,
            max_value=20)
        self.ai_strategic_candidates_field.set_disabled(
            not settings_manager.get("DEBUG"))
        current_y += (self.ai_strategic_candidates_field.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        self.ai_thinking_speed_field = InputField(
            rect=(x_center, current_y, 80, 40),
            font=self.input_font,
            initial_text=str(settings_manager.get("AI_THINKING_SPEED", 0.5)),
            on_text_change=None,
            numeric=True,
            min_value=-1,
            max_value=2.0)
        self.ai_thinking_speed_field.set_disabled(
            not settings_manager.get("DEBUG"))
        current_y += (self.ai_thinking_speed_field.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        apply_rect = pygame.Rect(0, 0, 0, 60)
        apply_rect.center = (button_center_x,
                             current_y + apply_rect.height // 2)
        self.apply_button = Button(apply_rect, "Apply", self.button_font,
                                   lambda: self._apply_settings())
        current_y += (self.apply_button.rect.height
                      + theme.THEME_LAYOUT_VERTICAL_GAP)

        back_rect = pygame.Rect(0, 0, 0, 60)
        back_rect.center = (button_center_x,
                            current_y + back_rect.height // 2)
        self.back_button = Button(back_rect, "Back", self.button_font,
                                  lambda: self.switch_scene(GameState.MENU))

        self._layout_controls(settings_manager.get("DEBUG"))

    def _on_tile_size_changed(self, new_tile_size):
        new_min_sidebar_width = new_tile_size + 20
        self.sidebar_width_slider.set_min_value(new_min_sidebar_width)

        current_sidebar_width = self.sidebar_width_slider.get_value()
        if current_sidebar_width < new_min_sidebar_width:
            self.sidebar_width_slider.set_value(new_min_sidebar_width)
            self.add_toast(
                Toast(
                    f"Sidebar width adjusted to minimum ({new_min_sidebar_width}px)",
                    type="info"))

    def _set_component_rect(self, component, x: int, y: int,
                            padding: int) -> int:
        width, height = component.rect.size
        component.rect = pygame.Rect(x, y, width, height)
        return y + height + padding

    def _set_component_center(self, component, center_x: int, y: int,
                              padding: int) -> int:
        width, height = component.rect.size
        component.rect = pygame.Rect(0, 0, width, height)
        component.rect.center = (center_x, y + height // 2)
        return y + height + padding

    def _set_slider_rect(self, slider: Slider, x: int, y: int,
                         padding: int) -> int:
        width, height = slider.rect.size
        slider.rect = pygame.Rect(x, y, width, height)
        input_width, _ = slider.input_field.rect.size
        slider.input_field.rect = pygame.Rect(slider.rect.right + 10, y,
                                              input_width, height)
        return y + height + padding

    def _layout_controls(self, debug_enabled: bool) -> None:
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        x_center = self.screen.get_width() // 2 - 100
        button_center_x = self.screen.get_width() // 2
        self.header_height = self._get_scene_header_height(
            self.font.get_height()
        )
        current_y = self.header_height + theme.THEME_LAYOUT_VERTICAL_GAP

        self.display_label_y = current_y
        current_y += self.dropdown_font.get_height() + padding

        current_y = self._set_component_rect(
            self.resolution_dropdown, x_center, current_y, padding)

        current_y = self._set_component_rect(
            self.fullscreen_checkbox, x_center, current_y, padding)

        self.game_label_y = current_y
        current_y += self.dropdown_font.get_height() + padding

        current_y = self._set_component_rect(
            self.valid_placement_checkbox, x_center, current_y, padding)

        self.debug_label_y = current_y
        if debug_enabled:
            current_y += self.dropdown_font.get_height() + padding

            current_y = self._set_component_rect(
                self.log_to_console_checkbox, x_center, current_y, padding)

            current_y = self._set_slider_rect(
                self.fps_slider, x_center, current_y, padding)
            current_y = self._set_slider_rect(
                self.grid_size_slider, x_center, current_y, padding)
            current_y = self._set_slider_rect(
                self.tile_size_slider, x_center, current_y, padding)
            current_y = self._set_slider_rect(
                self.figure_size_slider, x_center, current_y, padding)
            current_y = self._set_slider_rect(
                self.sidebar_width_slider, x_center, current_y, padding)

            current_y = self._set_component_rect(
                self.game_log_max_entries_field, x_center, current_y, padding)

            self.ai_label_y = current_y
            current_y += self.dropdown_font.get_height() + padding

            current_y = self._set_component_rect(
                self.ai_simulation_checkbox, x_center, current_y, padding)
            current_y = self._set_component_rect(
                self.ai_strategic_candidates_field, x_center, current_y,
                padding)
            current_y = self._set_component_rect(
                self.ai_thinking_speed_field, x_center, current_y, padding)
        else:
            self.ai_label_y = current_y

        current_y = self._set_component_center(
            self.apply_button, button_center_x, current_y, padding)
        self._set_component_center(
            self.back_button, button_center_x, current_y, padding)

    def _on_fullscreen_changed(self, key, old_value, new_value):
        self.resolution_dropdown.set_disabled(new_value)

    def _on_debug_changed(self, key, old_value, new_value):
        from utils.logging_config import update_logging_level
        update_logging_level()

        self.fps_slider.set_disabled(not new_value)
        self.grid_size_slider.set_disabled(not new_value)
        self.sidebar_width_slider.set_disabled(not new_value)
        self.tile_size_slider.set_disabled(not new_value)
        self.figure_size_slider.set_disabled(not new_value)
        self.game_log_max_entries_field.set_disabled(not new_value)
        self.ai_simulation_checkbox.set_disabled(not new_value)
        self.ai_strategic_candidates_field.set_disabled(not new_value)
        self.ai_thinking_speed_field.set_disabled(not new_value)
        self.log_to_console_checkbox.set_disabled(not new_value)

        if not new_value:
            self.log_to_console_checkbox.set_checked(False)
            settings_manager.set("LOG_TO_CONSOLE", False, temporary=True)

        self._layout_controls(new_value)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch_scene(GameState.MENU)
            if self.resolution_dropdown.handle_event(
                    event, y_offset=self.scroll_offset):
                continue
            self.fullscreen_checkbox.handle_event(event,
                                                  y_offset=self.scroll_offset)
            debug_enabled = settings_manager.get("DEBUG")
            if debug_enabled:
                self.log_to_console_checkbox.handle_event(
                    event, y_offset=self.scroll_offset)
            self.valid_placement_checkbox.handle_event(
                event, y_offset=self.scroll_offset)
            if debug_enabled:
                self.ai_simulation_checkbox.handle_event(
                    event, y_offset=self.scroll_offset)
                fps_was_dragging = self.fps_slider.dragging
                grid_was_dragging = self.grid_size_slider.dragging
                tile_was_dragging = self.tile_size_slider.dragging
                figure_was_dragging = self.figure_size_slider.dragging
                sidebar_was_dragging = self.sidebar_width_slider.dragging
                self.fps_slider.handle_event(event, y_offset=self.scroll_offset)
                self.grid_size_slider.handle_event(event,
                                                   y_offset=self.scroll_offset)
                self.tile_size_slider.handle_event(event,
                                                   y_offset=self.scroll_offset)
                self.figure_size_slider.handle_event(
                    event, y_offset=self.scroll_offset)
                self.sidebar_width_slider.handle_event(
                    event, y_offset=self.scroll_offset)
                if event.type == pygame.MOUSEBUTTONUP:
                    if fps_was_dragging:
                        self.add_toast(
                            Toast(
                                "In order to apply FPS setting, restart the game",
                                type="warning"))
                    if grid_was_dragging:
                        self.add_toast(
                            Toast(
                                "In order to apply grid size setting, restart the game",
                                type="warning"))
                    if tile_was_dragging:
                        self.add_toast(
                            Toast(
                                "In order to apply tile size setting, restart the game",
                                type="warning"))
                    if figure_was_dragging:
                        self.add_toast(
                            Toast(
                                "In order to apply figure size setting, restart the game",
                                type="warning"))
                    if sidebar_was_dragging:
                        self.add_toast(
                            Toast(
                                "In order to apply sidebar width setting, restart the game",
                                type="warning"))
                self.game_log_max_entries_field.handle_event(
                    event, y_offset=self.scroll_offset)
                self.ai_strategic_candidates_field.handle_event(
                    event, y_offset=self.scroll_offset)
                self.ai_thinking_speed_field.handle_event(
                    event, y_offset=self.scroll_offset)
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                self.back_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.apply_button.handle_event(event,
                                               y_offset=self.scroll_offset)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.back_button.handle_event(event,
                                              y_offset=self.scroll_offset)
                self.apply_button.handle_event(event,
                                               y_offset=self.scroll_offset)
                if self.back_button._is_clicked(event.pos,
                                                y_offset=self.scroll_offset):
                    self.switch_scene(GameState.MENU)
                elif self.apply_button._is_clicked(
                        event.pos, y_offset=self.scroll_offset):
                    self._apply_settings()

    def _handle_ai_simulation_toggle(self, value):
        settings_manager.set("AI_USE_SIMULATION", value, temporary=True)

    def _handle_log_to_console_toggle(self, value):
        settings_manager.set("LOG_TO_CONSOLE", value, temporary=True)

    def _handle_valid_placement_toggle(self, value):
        settings_manager.set("SHOW_VALID_PLACEMENTS", value, temporary=True)

    def _apply_settings(self):
        changes = {}

        selected_resolution = self.resolution_dropdown.get_selected()
        if selected_resolution:
            width, height = map(int, selected_resolution.split("x"))
            changes["WINDOW_WIDTH"] = width
            changes["WINDOW_HEIGHT"] = height

        changes["FULLSCREEN"] = self.fullscreen_checkbox.is_checked()
        debug_enabled = settings_manager.get("DEBUG")
        if not debug_enabled:
            changes["LOG_TO_CONSOLE"] = False
        elif not self.log_to_console_checkbox.is_disabled():
            changes[
                "LOG_TO_CONSOLE"] = self.log_to_console_checkbox.is_checked()
        if not self.valid_placement_checkbox.is_disabled():
            changes[
                "SHOW_VALID_PLACEMENTS"] = self.valid_placement_checkbox.is_checked(
                )
        if not self.ai_simulation_checkbox.is_disabled():
            changes[
                "AI_USE_SIMULATION"] = self.ai_simulation_checkbox.is_checked(
                )

        if not self.fps_slider.is_disabled():
            changes["FPS"] = self.fps_slider.get_value()

        if not self.grid_size_slider.is_disabled():
            changes["GRID_SIZE"] = self.grid_size_slider.get_value()

        if not self.tile_size_slider.is_disabled():
            changes["TILE_SIZE"] = self.tile_size_slider.get_value()

        if not self.figure_size_slider.is_disabled():
            changes["FIGURE_SIZE"] = self.figure_size_slider.get_value()

        if not self.sidebar_width_slider.is_disabled():
            changes["SIDEBAR_WIDTH"] = self.sidebar_width_slider.get_value()

        if not self.game_log_max_entries_field.is_disabled():
            try:
                log_max_entries = int(
                    self.game_log_max_entries_field.get_text())
                if 100 <= log_max_entries <= 50000:
                    changes["GAME_LOG_MAX_ENTRIES"] = log_max_entries
                else:
                    self.add_toast(
                        Toast(
                            "Game log max entries must be between 100 and 50000",
                            type="error"))
                    return
            except ValueError:
                self.add_toast(
                    Toast("Invalid game log max entries value", type="error"))
                return

        if not self.ai_strategic_candidates_field.is_disabled():
            try:
                candidates = int(self.ai_strategic_candidates_field.get_text())
                if candidates == -1 or (1 <= candidates <= 20):
                    changes["AI_STRATEGIC_CANDIDATES"] = candidates
                else:
                    self.add_toast(
                        Toast(
                            "AI strategic candidates must be -1 (all) or between 1 and 20",
                            type="error"))
                    return
            except ValueError:
                self.add_toast(
                    Toast("Invalid AI strategic candidates value",
                          type="error"))
                return

        if not self.ai_thinking_speed_field.is_disabled():
            try:
                thinking_speed = float(self.ai_thinking_speed_field.get_text())
                if -1 <= thinking_speed <= 2.0:
                    changes["AI_THINKING_SPEED"] = thinking_speed
                else:
                    self.add_toast(
                        Toast(
                            "AI thinking speed must be between -1 and 2.0 seconds",
                            type="error"))
                    return
            except ValueError:
                self.add_toast(
                    Toast("Invalid AI thinking speed value", type="error"))
                return

        success = True
        for key, value in changes.items():
            if not settings_manager.set(key, value, temporary=False):
                success = False

        if success:
            self.add_toast(Toast("Settings successfully saved",
                                 type="success"))
            #self.add_toast(Toast("Restart the game to apply changes", type="warning"))

            if "GAME_LOG_MAX_ENTRIES" in changes:
                from utils.logging_config import game_log_instance
                if game_log_instance:
                    game_log_instance.update_max_entries()
        else:
            self.add_toast(Toast("Failed to save some settings", type="error"))

    def _handle_fullscreen_toggle(self, value):
        self.resolution_dropdown.set_disabled(value)

    def draw(self) -> None:
        self._draw_background(
            background_color=theme.THEME_SETTINGS_BACKGROUND_COLOR,
            image_name=theme.THEME_SETTINGS_BACKGROUND_IMAGE,
            scale_mode=theme.THEME_SETTINGS_BACKGROUND_SCALE_MODE,
            tint_color=theme.THEME_SETTINGS_BACKGROUND_TINT_COLOR,
            blur_radius=theme.THEME_SETTINGS_BACKGROUND_BLUR_RADIUS,
        )
        offset_y = self.scroll_offset
        label_font = self.dropdown_font

        title_text = self.font.render("Settings", True,
                                      theme.THEME_TEXT_COLOR_LIGHT)
        self._draw_scene_header(title_text)

        # Draw section headers
        display_label = self.dropdown_font.render(
            "Display", True, theme.THEME_SECTION_HEADER_COLOR)
        display_label_rect = display_label.get_rect()
        display_label_rect.centerx = self.screen.get_width() // 2
        display_label_rect.y = self.display_label_y + offset_y
        self.screen.blit(display_label, display_label_rect)

        game_label = self.dropdown_font.render(
            "Game", True, theme.THEME_SECTION_HEADER_COLOR)
        game_label_rect = game_label.get_rect()
        game_label_rect.centerx = self.screen.get_width() // 2
        game_label_rect.y = self.game_label_y + offset_y
        self.screen.blit(game_label, game_label_rect)

        debug_enabled = settings_manager.get("DEBUG")
        if debug_enabled:
            debug_label = self.dropdown_font.render(
                "Debug", True, theme.THEME_SECTION_HEADER_COLOR)
            debug_label_rect = debug_label.get_rect()
            debug_label_rect.centerx = self.screen.get_width() // 2
            debug_label_rect.y = self.debug_label_y + offset_y
            self.screen.blit(debug_label, debug_label_rect)

        if debug_enabled:
            ai_label = self.dropdown_font.render(
                "AI", True, theme.THEME_SECTION_HEADER_COLOR)
            ai_label_rect = ai_label.get_rect()
            ai_label_rect.centerx = self.screen.get_width() // 2
            ai_label_rect.y = self.ai_label_y + offset_y
            self.screen.blit(ai_label, ai_label_rect)

        # Display Settings
        res_label = label_font.render(
            "Resolution:", True, theme.THEME_TEXT_COLOR_LIGHT)
        res_label_rect = res_label.get_rect(
            right=self.resolution_dropdown.rect.left - 10,
            centery=self.resolution_dropdown.rect.centery + offset_y)
        self.screen.blit(res_label, res_label_rect)

        fs_label = label_font.render(
            "Fullscreen:", True, theme.THEME_TEXT_COLOR_LIGHT)
        fs_label_rect = fs_label.get_rect(
            right=self.fullscreen_checkbox.rect.left - 10,
            centery=self.fullscreen_checkbox.rect.centery + offset_y)
        self.screen.blit(fs_label, fs_label_rect)

        # Game Settings
        label_color = (
            theme.THEME_LABEL_DISABLED_COLOR
            if self.valid_placement_checkbox.is_disabled()
            else theme.THEME_TEXT_COLOR_LIGHT)
        valid_placements_label = label_font.render(
            "Show valid card placements:", True, label_color)
        valid_placements_label_rect = valid_placements_label.get_rect(
            right=self.valid_placement_checkbox.rect.left - 10,
            centery=self.valid_placement_checkbox.rect.centery + offset_y)
        self.screen.blit(valid_placements_label, valid_placements_label_rect)

        # Debug Settings
        if debug_enabled:
            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.log_to_console_checkbox.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            log_to_console_label = label_font.render("Log to console:", True,
                                                     label_color)
            log_to_console_label_rect = log_to_console_label.get_rect(
                right=self.log_to_console_checkbox.rect.left - 10,
                centery=self.log_to_console_checkbox.rect.centery + offset_y)
            self.screen.blit(log_to_console_label, log_to_console_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.fps_slider.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            fps_label = label_font.render("FPS:", True, label_color)
            fps_label_rect = fps_label.get_rect(
                right=self.fps_slider.rect.left - 10,
                centery=self.fps_slider.rect.centery + offset_y)
            self.screen.blit(fps_label, fps_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.grid_size_slider.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            grid_label = label_font.render("Grid size:", True, label_color)
            grid_label_rect = grid_label.get_rect(
                right=self.grid_size_slider.rect.left - 10,
                centery=self.grid_size_slider.rect.centery + offset_y)
            self.screen.blit(grid_label, grid_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.tile_size_slider.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            tsz_label = label_font.render("Tile size:", True, label_color)
            tsz_label_rect = tsz_label.get_rect(
                right=self.tile_size_slider.rect.left - 10,
                centery=self.tile_size_slider.rect.centery + offset_y)
            self.screen.blit(tsz_label, tsz_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.figure_size_slider.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            fsz_label = label_font.render("Figure size:", True, label_color)
            fsz_label_rect = fsz_label.get_rect(
                right=self.figure_size_slider.rect.left - 10,
                centery=self.figure_size_slider.rect.centery + offset_y)
            self.screen.blit(fsz_label, fsz_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.sidebar_width_slider.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            sbw_label = label_font.render("Sidebar width:", True, label_color)
            sbw_label_rect = sbw_label.get_rect(
                right=self.sidebar_width_slider.rect.left - 10,
                centery=self.sidebar_width_slider.rect.centery + offset_y)
            self.screen.blit(sbw_label, sbw_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.game_log_max_entries_field.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            log_label = label_font.render("Game log max entries:", True,
                                          label_color)
            log_label_rect = log_label.get_rect(
                right=self.game_log_max_entries_field.rect.left - 10,
                centery=self.game_log_max_entries_field.rect.centery + offset_y)
            self.screen.blit(log_label, log_label_rect)

        # AI Settings
        if debug_enabled:
            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.ai_simulation_checkbox.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            ai_simulation_label = label_font.render("AI simulation:", True,
                                                    label_color)
            ai_simulation_label_rect = ai_simulation_label.get_rect(
                right=self.ai_simulation_checkbox.rect.left - 10,
                centery=self.ai_simulation_checkbox.rect.centery + offset_y)
            self.screen.blit(ai_simulation_label, ai_simulation_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.ai_strategic_candidates_field.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            ai_candidates_label = label_font.render(
                "AI strategic candidates:", True, label_color)
            ai_candidates_label_rect = ai_candidates_label.get_rect(
                right=self.ai_strategic_candidates_field.rect.left - 10,
                centery=self.ai_strategic_candidates_field.rect.centery +
                offset_y)
            self.screen.blit(ai_candidates_label,
                             ai_candidates_label_rect)

            label_color = (
                theme.THEME_LABEL_DISABLED_COLOR
                if self.ai_thinking_speed_field.is_disabled()
                else theme.THEME_TEXT_COLOR_LIGHT)
            thinking_speed_label = label_font.render(
                "AI Thinking Speed (s):", True, label_color)
            thinking_speed_label_rect = thinking_speed_label.get_rect(
                right=self.ai_thinking_speed_field.rect.left - 10,
                centery=self.ai_thinking_speed_field.rect.centery + offset_y)
            self.screen.blit(thinking_speed_label, thinking_speed_label_rect)

        # Draw all UI components in logical order
        self.fullscreen_checkbox.draw(self.screen, y_offset=offset_y)
        self.valid_placement_checkbox.draw(self.screen, y_offset=offset_y)
        if debug_enabled:
            self.log_to_console_checkbox.draw(self.screen, y_offset=offset_y)
            self.fps_slider.draw(self.screen, y_offset=offset_y)
            self.grid_size_slider.draw(self.screen, y_offset=offset_y)
            self.tile_size_slider.draw(self.screen, y_offset=offset_y)
            self.figure_size_slider.draw(self.screen, y_offset=offset_y)
            self.sidebar_width_slider.draw(self.screen, y_offset=offset_y)
            self.game_log_max_entries_field.draw(self.screen,
                                                 y_offset=offset_y)
            self.ai_simulation_checkbox.draw(self.screen, y_offset=offset_y)
            self.ai_strategic_candidates_field.draw(self.screen,
                                                    y_offset=offset_y)
            self.ai_thinking_speed_field.draw(self.screen, y_offset=offset_y)
        self.apply_button.draw(self.screen, y_offset=offset_y)
        self.back_button.draw(self.screen, y_offset=offset_y)

        self.max_scroll = max(
            self.screen.get_height(),
            self.back_button.rect.bottom + theme.THEME_LAYOUT_VERTICAL_GAP * 2,
        )

        self.toast_manager.draw(self.screen)
        self._draw_dropdowns([self.resolution_dropdown], y_offset=offset_y)
        self._draw_dropdowns(
            [self.resolution_dropdown],
            y_offset=offset_y,
            expanded_only=True,
        )

    def refresh_theme(self) -> None:
        """Refresh fonts and component styling after theme changes."""
        super().refresh_theme()
        self.font = theme.get_font("title", theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.button_font = theme.get_font(
            "button", theme.THEME_FONT_SIZE_BUTTON
        )
        self.input_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.dropdown_font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)

        self.resolution_dropdown.set_font(self.dropdown_font)
        self.resolution_dropdown.apply_theme()

        checkboxes = [
            self.fullscreen_checkbox,
            self.valid_placement_checkbox,
            self.log_to_console_checkbox,
            self.ai_simulation_checkbox,
        ]
        for checkbox in checkboxes:
            checkbox.apply_theme()

        sliders = [
            self.fps_slider,
            self.grid_size_slider,
            self.tile_size_slider,
            self.figure_size_slider,
            self.sidebar_width_slider,
        ]
        for slider in sliders:
            slider.set_font(self.dropdown_font)
            slider.apply_theme()

        inputs = [
            self.game_log_max_entries_field,
            self.ai_strategic_candidates_field,
            self.ai_thinking_speed_field,
        ]
        for input_field in inputs:
            input_field.set_font(self.input_font)
            input_field.apply_theme()

        self.apply_button.set_font(self.button_font)
        self.apply_button.apply_theme()
        self.back_button.set_font(self.button_font)
        self.back_button.apply_theme()
        self.toast_manager.apply_theme()
        self._layout_controls(settings_manager.get("DEBUG"))

    def add_toast(self, toast):
        self.toast_manager.add_toast(toast)
