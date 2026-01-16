import typing

import pygame

from game_state import GameState
from ui import theme
from ui.components.button import Button
from ui.components.checkbox import Checkbox
from ui.components.dropdown import Dropdown
from ui.components.input_field import InputField
from ui.components.slider import Slider
from ui.scene import Scene
from utils.settings_manager import settings_manager


class ThemeDebugScene(Scene):
    """Scene for previewing and editing theme values at runtime."""

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable) -> None:
        super().__init__(screen, switch_scene_callback)
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        self._theme_components: list[object] = []
        self._font_components: list[object] = []
        self._control_rows: list[dict[str, typing.Any]] = []
        self._optional_color_controls: dict[str, dict[str, typing.Any]] = {}
        self._optional_string_controls: dict[str, dict[str, typing.Any]] = {}
        self._refresh_fonts()

        self._build_preview_components()
        self._build_theme_controls()

        self.back_button = Button(
            (0, 0, 200, 50),
            "Back",
            self.button_font,
            lambda: self.switch_scene(GameState.SETTINGS),
        )
        self._register_component(self.back_button)

        self._layout()
        self._sync_theme_components()

    def _refresh_fonts(self) -> None:
        self.title_font = theme.get_font(theme.THEME_FONT_SIZE_SCENE_TITLE)
        self.label_font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
        self.button_font = theme.get_font(theme.THEME_FONT_SIZE_BUTTON)
        self.small_font = theme.get_font(theme.THEME_FONT_SIZE_HELP_CONTROLS)

        for component in self._font_components:
            if isinstance(component, Button):
                component.font = self.button_font
                component._update_render()
            elif isinstance(component, Slider):
                component.font = self.label_font
                component.input_field.font = self.label_font
            elif isinstance(component, InputField):
                component.font = self.label_font
            elif isinstance(component, Dropdown):
                component.font = self.label_font

    def _register_component(self, component: object) -> None:
        self._theme_components.append(component)
        if isinstance(component, (Button, Slider, InputField, Dropdown)):
            self._font_components.append(component)

    def _build_preview_components(self) -> None:
        self.preview_button = Button(
            (0, 0, 220, 60),
            "Primary Button",
            self.button_font,
            None,
        )
        self.preview_checkbox = Checkbox((0, 0, 22, 22), checked=True)
        self.preview_slider = Slider(
            rect=(0, 0, 180, 20),
            font=self.label_font,
            min_value=0,
            max_value=100,
            value=50,
            on_change=None,
        )
        self.preview_dropdown = Dropdown(
            rect=(0, 0, 200, 36),
            font=self.label_font,
            options=["Option A", "Option B", "Option C"],
            default_index=0,
        )
        self.preview_input = InputField(
            rect=(0, 0, 220, 36),
            font=self.label_font,
            initial_text="Sample text",
        )
        for component in (
                self.preview_button,
                self.preview_checkbox,
                self.preview_slider,
                self.preview_dropdown,
                self.preview_input,
        ):
            self._register_component(component)

    def _build_theme_controls(self) -> None:
        skip_names = {"THEME_TOAST_COLORS", "THEME_PLAYER_COLOR_MAP"}
        theme_names = sorted(
            name for name in dir(theme)
            if name.startswith("THEME_") and name not in skip_names)
        for name in theme_names:
            value = getattr(theme, name)
            if name.endswith("_IMAGE"):
                self._add_optional_string_control(name, value)
            elif name.endswith("_TINT_COLOR"):
                self._add_optional_color_controls(
                    name, value, default=(0, 0, 0, 0))
            elif isinstance(value, tuple):
                self._add_color_controls(name, value)
            elif value is None:
                if "COLOR" in name:
                    self._add_optional_color_controls(
                        name, value, default=(0, 0, 0, 0))
                else:
                    self._add_optional_string_control(name, value)
            elif isinstance(value, str):
                if name.endswith("SCALE_MODE"):
                    self._add_scale_mode_control(name, value)
                else:
                    self._add_string_control(name, value)
            elif isinstance(value, int) and not isinstance(value, bool):
                self._add_integer_control(name, value)
            elif isinstance(value, float):
                self._add_float_control(name, value)

    def _add_control_row(self,
                         label: str,
                         components: list[object],
                         offsets: list[int] | None = None,
                         height: int | None = None) -> None:
        if offsets is None:
            offsets = [0 for _ in components]
        if height is None:
            height = max(
                component.rect.height for component in components
                if hasattr(component, "rect"))
        self._control_rows.append({
            "label": label,
            "components": components,
            "offsets": offsets,
            "height": height,
        })
        for component in components:
            self._register_component(component)

    def _pretty_label(self, name: str) -> str:
        return name.replace("THEME_", "").replace("_", " ").title()

    def _set_theme_value(self, name: str, value: object) -> None:
        theme.set_theme_value(name, value)
        if "FONT_SIZE" in name:
            theme.clear_font_cache()
            self._refresh_fonts()
        self._sync_theme_components()

    def _add_color_controls(self, name: str, value: tuple) -> None:
        label = self._pretty_label(name)
        color_state = list(value)
        channels = ["R", "G", "B"] + (["A"] if len(color_state) == 4 else [])

        for index, channel in enumerate(channels):
            slider = Slider(
                rect=(0, 0, 200, 20),
                font=self.label_font,
                min_value=0,
                max_value=255,
                value=color_state[index],
                on_change=self._make_color_handler(name, color_state, index),
            )
            self._add_control_row(f"{label} {channel}", [slider], height=30)

    def _add_optional_color_controls(self,
                                     name: str,
                                     value: tuple | None,
                                     default: tuple) -> None:
        label = self._pretty_label(name)
        color_state = list(value or default)
        enabled = value is not None

        checkbox = Checkbox(
            rect=(0, 0, 20, 20),
            checked=enabled,
            on_toggle=lambda checked: self._toggle_optional_color(
                name, checked),
        )
        self._optional_color_controls[name] = {
            "checkbox": checkbox,
            "color_state": color_state,
            "sliders": [],
        }
        self._add_control_row(f"{label} Enabled", [checkbox], height=24)

        channels = ["R", "G", "B", "A"]
        for index, channel in enumerate(channels):
            slider = Slider(
                rect=(0, 0, 200, 20),
                font=self.label_font,
                min_value=0,
                max_value=255,
                value=color_state[index],
                on_change=self._make_optional_color_handler(
                    name, color_state, index),
            )
            slider.set_disabled(not enabled)
            self._optional_color_controls[name]["sliders"].append(slider)
            self._add_control_row(f"{label} {channel}", [slider], height=30)

    def _toggle_optional_color(self, name: str, enabled: bool) -> None:
        control = self._optional_color_controls[name]
        for slider in control["sliders"]:
            slider.set_disabled(not enabled)
        if enabled:
            self._set_theme_value(name, tuple(control["color_state"]))
        else:
            self._set_theme_value(name, None)

    def _make_color_handler(self,
                            name: str,
                            color_state: list[int],
                            index: int) -> typing.Callable:
        def _handler(new_value: int) -> None:
            color_state[index] = int(new_value)
            self._set_theme_value(name, tuple(color_state))

        return _handler

    def _make_optional_color_handler(self,
                                     name: str,
                                     color_state: list[int],
                                     index: int) -> typing.Callable:
        def _handler(new_value: int) -> None:
            color_state[index] = int(new_value)
            control = self._optional_color_controls[name]
            if control["checkbox"].is_checked():
                self._set_theme_value(name, tuple(color_state))

        return _handler

    def _add_integer_control(self, name: str, value: int) -> None:
        label = self._pretty_label(name)
        min_value, max_value = self._range_for_int(name, value)
        slider = Slider(
            rect=(0, 0, 200, 20),
            font=self.label_font,
            min_value=min_value,
            max_value=max_value,
            value=value,
            on_change=lambda new_value: self._set_theme_value(
                name, int(new_value)),
        )
        self._add_control_row(label, [slider], height=30)

    def _add_float_control(self, name: str, value: float) -> None:
        label = self._pretty_label(name)
        input_field = InputField(
            rect=(0, 0, 220, 36),
            font=self.label_font,
            initial_text=f"{value:.2f}",
            numeric=True,
            on_text_change=lambda text: self._handle_float_input(name, text),
        )
        self._add_control_row(label, [input_field], height=40)

    def _add_string_control(self, name: str, value: str) -> None:
        label = self._pretty_label(name)
        input_field = InputField(
            rect=(0, 0, 240, 36),
            font=self.label_font,
            initial_text=value,
            on_text_change=lambda text: self._set_theme_value(name, text),
        )
        self._add_control_row(label, [input_field], height=40)

    def _add_optional_string_control(self,
                                     name: str,
                                     value: str | None) -> None:
        label = self._pretty_label(name)
        enabled = value is not None
        checkbox = Checkbox(rect=(0, 0, 20, 20), checked=enabled)
        input_field = InputField(
            rect=(0, 0, 240, 36),
            font=self.label_font,
            initial_text=value or "",
            on_text_change=lambda text: self._set_optional_string_value(
                name, text),
        )
        input_field.set_disabled(not enabled)
        checkbox.on_toggle = lambda checked: self._toggle_optional_string(
            name, checked)
        self._optional_string_controls[name] = {
            "checkbox": checkbox,
            "input": input_field,
        }
        self._add_control_row(f"{label} Enabled", [checkbox], height=24)
        self._add_control_row(label, [input_field], height=40)

    def _toggle_optional_string(self, name: str, enabled: bool) -> None:
        control = self._optional_string_controls[name]
        control["input"].set_disabled(not enabled)
        if enabled:
            self._set_theme_value(name, control["input"].get_text())
        else:
            self._set_theme_value(name, None)

    def _set_optional_string_value(self, name: str, value: str) -> None:
        control = self._optional_string_controls[name]
        if control["checkbox"].is_checked():
            self._set_theme_value(name, value)

    def _add_scale_mode_control(self, name: str, value: str) -> None:
        label = self._pretty_label(name)
        options = ["fill", "fit", "stretch"]
        selected_index = options.index(value) if value in options else 0
        dropdown = Dropdown(
            rect=(0, 0, 200, 36),
            font=self.label_font,
            options=options,
            default_index=selected_index,
            on_select=lambda selected: self._set_theme_value(name, selected),
        )
        self._add_control_row(label, [dropdown], height=40)

    def _handle_float_input(self, name: str, text: str) -> None:
        if not text or text in {"-", ".", "-."}:
            return
        try:
            self._set_theme_value(name, float(text))
        except ValueError:
            return

    def _range_for_int(self, name: str,
                       value: int) -> tuple[int, int]:
        if "FONT_SIZE" in name:
            return 8, 160
        if "BLUR" in name:
            return 0, 30
        if "TITLE" in name:
            return 20, max(120, value + 20)
        return 0, max(255, value + 20)

    def _layout(self) -> None:
        self._layout_preview()
        self._layout_controls()

    def _layout_preview(self) -> None:
        preview_left = 60
        preview_top = 120
        column_gap = 260
        row_gap = 50

        self.preview_button.rect.topleft = (preview_left, preview_top)
        self.preview_checkbox.rect.topleft = (preview_left,
                                              preview_top + row_gap)
        self.preview_slider.rect.topleft = (preview_left + column_gap,
                                            preview_top + row_gap)
        self.preview_slider.input_field.rect.topleft = (
            self.preview_slider.rect.right + 10,
            self.preview_slider.rect.y,
        )
        self.preview_dropdown.rect.topleft = (
            preview_left,
            preview_top + row_gap * 2,
        )
        self.preview_input.rect.topleft = (
            preview_left + column_gap,
            preview_top + row_gap * 2,
        )

        self.preview_bottom = preview_top + row_gap * 3

    def _layout_controls(self) -> None:
        label_right = min(360, self.screen.get_width() // 2 - 40)
        control_x = label_right + 20
        current_y = self.preview_bottom + 80
        row_spacing = 10

        for row in self._control_rows:
            row_height = row["height"]
            for component, offset in zip(row["components"], row["offsets"]):
                x = control_x + offset
                if isinstance(component, Slider):
                    component.rect = pygame.Rect(x, current_y, 200, 20)
                    component.input_field.rect = pygame.Rect(
                        component.rect.right + 10,
                        current_y,
                        component.input_field.rect.width,
                        component.rect.height,
                    )
                else:
                    component.rect = pygame.Rect(
                        x,
                        current_y,
                        component.rect.width,
                        component.rect.height,
                    )
            current_y += row_height + row_spacing

        self.back_button.rect = pygame.Rect(control_x, current_y + 20, 200, 50)
        self.max_scroll = max(self.screen.get_height(),
                              self.back_button.rect.bottom + 80)

    def _sync_theme_components(self) -> None:
        for component in self._theme_components:
            if isinstance(component, Button):
                component.bg_color = theme.THEME_BUTTON_BG_COLOR
                component.hover_bg_color = theme.THEME_BUTTON_HOVER_BG_COLOR
                component.pressed_bg_color = theme.THEME_BUTTON_PRESSED_BG_COLOR
                component.text_color = theme.THEME_BUTTON_TEXT_COLOR
                component._update_render()
            elif isinstance(component, Slider):
                component.bg_color = theme.THEME_SLIDER_BG_COLOR
                component.fg_color = theme.THEME_SLIDER_FG_COLOR
                component.handle_color = theme.THEME_SLIDER_HANDLE_COLOR
                component.border_color = theme.THEME_SLIDER_BORDER_COLOR
                component.handle_hover_color = (
                    theme.THEME_SLIDER_HANDLE_HOVER_COLOR)
                component.handle_active_color = (
                    theme.THEME_SLIDER_HANDLE_ACTIVE_COLOR)
                component.track_hover_color = theme.THEME_SLIDER_TRACK_HOVER_COLOR
                component.track_active_color = (
                    theme.THEME_SLIDER_TRACK_ACTIVE_COLOR)
                component.hover_border_color = theme.THEME_SLIDER_HOVER_BORDER_COLOR
                component.disabled_bg_color = theme.THEME_SLIDER_DISABLED_BG_COLOR
                component.disabled_fg_color = theme.THEME_SLIDER_DISABLED_FG_COLOR
                component.disabled_handle_color = (
                    theme.THEME_SLIDER_DISABLED_HANDLE_COLOR)
                component.disabled_border_color = (
                    theme.THEME_SLIDER_DISABLED_BORDER_COLOR)
            elif isinstance(component, InputField):
                component.text_color = theme.THEME_INPUT_TEXT_COLOR
                component.bg_color = theme.THEME_INPUT_BG_COLOR
                component.border_color = theme.THEME_INPUT_BORDER_COLOR
            elif isinstance(component, Dropdown):
                component.text_color = theme.THEME_DROPDOWN_TEXT_COLOR
                component.bg_color = theme.THEME_DROPDOWN_BG_COLOR
                component.border_color = theme.THEME_DROPDOWN_BORDER_COLOR
                component.highlight_color = theme.THEME_DROPDOWN_HIGHLIGHT_COLOR
                component.hover_bg_color = theme.THEME_DROPDOWN_HOVER_BG_COLOR
                component.hover_option_color = (
                    theme.THEME_DROPDOWN_HOVER_OPTION_COLOR)
            elif isinstance(component, Checkbox):
                component.box_color = theme.THEME_CHECKBOX_BOX_COLOR
                component.check_color = theme.THEME_CHECKBOX_CHECK_COLOR
                component.border_color = theme.THEME_CHECKBOX_BORDER_COLOR
                component.hover_box_color = theme.THEME_CHECKBOX_HOVER_BOX_COLOR
                component.disabled_color = theme.THEME_CHECKBOX_DISABLED_COLOR

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if not settings_manager.get("DEBUG"):
            self.switch_scene(GameState.SETTINGS)
            return
        self._apply_scroll(events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch_scene(GameState.SETTINGS)

            for component in (
                    self.preview_button,
                    self.preview_checkbox,
                    self.preview_slider,
                    self.preview_dropdown,
                    self.preview_input,
                    self.back_button,
            ):
                if isinstance(component, Dropdown):
                    component.handle_event(event, y_offset=self.scroll_offset)
                else:
                    component.handle_event(event, y_offset=self.scroll_offset)

            for row in self._control_rows:
                for component in row["components"]:
                    if isinstance(component, Dropdown):
                        component.handle_event(event,
                                               y_offset=self.scroll_offset)
                    else:
                        component.handle_event(event,
                                               y_offset=self.scroll_offset)

    def draw(self) -> None:
        self._draw_background(
            background_color=theme.THEME_SETTINGS_BACKGROUND_COLOR,
            image_name=theme.THEME_SETTINGS_BACKGROUND_IMAGE,
            scale_mode=theme.THEME_SETTINGS_BACKGROUND_SCALE_MODE,
            tint_color=theme.THEME_SETTINGS_BACKGROUND_TINT_COLOR,
            blur_radius=theme.THEME_SETTINGS_BACKGROUND_BLUR_RADIUS,
        )
        offset_y = self.scroll_offset
        title_text = self.title_font.render(
            "Theme Debug", True, theme.THEME_TEXT_COLOR_LIGHT)
        title_rect = title_text.get_rect(
            center=(self.screen.get_width() // 2, 60 + offset_y))
        self.screen.blit(title_text, title_rect)

        preview_label = self.label_font.render(
            "Preview", True, theme.THEME_SECTION_HEADER_COLOR)
        preview_rect = preview_label.get_rect(
            left=60, centery=100 + offset_y)
        self.screen.blit(preview_label, preview_rect)

        preview_caption = self.small_font.render(
            "Sample UI elements using current theme colors",
            True,
            theme.THEME_SUBSECTION_COLOR,
        )
        self.screen.blit(preview_caption, (60, 140 + offset_y))

        self.preview_button.draw(self.screen, y_offset=offset_y)
        self.preview_checkbox.draw(self.screen, y_offset=offset_y)
        self.preview_slider.draw(self.screen, y_offset=offset_y)
        self.preview_dropdown.draw(self.screen, y_offset=offset_y)
        self.preview_input.draw(self.screen, y_offset=offset_y)

        theme_label = self.label_font.render(
            "Theme Values", True, theme.THEME_SECTION_HEADER_COLOR)
        self.screen.blit(theme_label, (60, self.preview_bottom + 40 + offset_y))

        label_right = min(360, self.screen.get_width() // 2 - 40)
        for row in self._control_rows:
            label = self.label_font.render(
                row["label"], True, theme.THEME_TEXT_COLOR_LIGHT)
            label_rect = label.get_rect()
            label_rect.right = label_right
            label_rect.centery = row["components"][0].rect.centery + offset_y
            self.screen.blit(label, label_rect)
            for component in row["components"]:
                component.draw(self.screen, y_offset=offset_y)

        self.back_button.draw(self.screen, y_offset=offset_y)
        pygame.display.flip()
