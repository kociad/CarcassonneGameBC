from __future__ import annotations

from dataclasses import dataclass
import typing

import pygame

from ui import theme
from ui.components.button import Button
from ui.components.checkbox import Checkbox
from ui.components.dropdown import Dropdown
from ui.components.input_field import InputField
from ui.components.slider import Slider


@dataclass
class ThemeControl:
    name: str
    label: str
    y: int
    height: int
    components: list[typing.Any]
    draw: typing.Callable[[pygame.Surface, int], None]
    handle_event: typing.Callable[[pygame.event.Event, int], None]
    sync: typing.Callable[[], None]
    is_section: bool = False


@dataclass
class ThemeItem:
    name: str
    value: typing.Any
    is_section: bool = False


class ThemeDebugOverlay:
    """Debug-only overlay for live theme editing."""

    def __init__(
        self,
        screen: pygame.Surface,
        on_theme_update: typing.Callable[[str | None], None],
    ) -> None:
        self.screen = screen
        self._on_theme_update = on_theme_update
        self.active = False
        self.scroll_offset = 0
        self.max_scroll = 0
        self.panel_width = 560
        self.panel_margin = 20
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.toggle_button = None
        self.save_button = None
        self._controls_start_y = 0
        self.controls: list[ThemeControl] = []
        self._optional_values: dict[str, typing.Any] = {}
        self._pending_values: dict[str, typing.Any] = {}
        self._dirty_names: set[str] = set()
        self._apply_buttons: dict[str, Button] = {}
        self._control_map: dict[str, ThemeControl] = {}
        self._title_text = "Theme Debug Overlay"
        self._title_surface: pygame.Surface | None = None
        self._cached_title_text: str | None = None
        self._cached_title_font_id: int | None = None
        self._build_layout()
        self._build_controls()

    def _build_layout(self) -> None:
        screen_width, screen_height = self.screen.get_size()
        self.panel_rect = pygame.Rect(
            screen_width - self.panel_width - self.panel_margin,
            self.panel_margin,
            self.panel_width,
            screen_height - (self.panel_margin * 2),
        )
        self.title_font = theme.get_font(
            "title", max(18, int(theme.THEME_FONT_SIZE_BODY * 0.6))
        )
        self.label_font = theme.get_font(
            "label", max(14, int(theme.THEME_FONT_SIZE_BODY * 0.45))
        )
        self.control_font = theme.get_font(
            "label", max(14, int(theme.THEME_FONT_SIZE_BODY * 0.45))
        )
        self.section_font = theme.get_font(
            "section_header", max(16, theme.THEME_FONT_SIZE_SECTION_HEADER)
        )
        self.apply_font = theme.get_font(
            "button", max(12, int(theme.THEME_FONT_SIZE_BODY * 0.35))
        )
        if (self._title_surface is None
                or self._cached_title_text != self._title_text
                or self._cached_title_font_id != id(self.title_font)):
            self._title_surface = self.title_font.render(
                self._title_text, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            self._cached_title_text = self._title_text
            self._cached_title_font_id = id(self.title_font)
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        button_size = max(24, int(self.title_font.get_height() * 0.9))
        toggle_rect = pygame.Rect(0, 0, 0, button_size)
        toggle_rect.center = (
            screen_width - button_size // 2 - padding,
            padding + button_size // 2,
        )
        self.toggle_button = Button(
            rect=toggle_rect,
            text="DBG",
            font=theme.get_font("button", 16),
            callback=self.toggle,
        )
        save_rect = pygame.Rect(0, 0, 0, 36)
        save_rect.center = (
            self.panel_rect.left + padding + save_rect.height // 2,
            self.panel_rect.top + padding + save_rect.height // 2,
        )
        self.save_button = Button(
            rect=save_rect,
            text="Save",
            font=theme.get_font("button", 18),
            callback=self._save_theme,
        )
        save_width, save_height = self.save_button.rect.size
        self.save_button.rect.center = (
            self.panel_rect.left + padding + save_width // 2,
            self.panel_rect.top + padding + save_height // 2,
        )
        header_height = max(self._title_surface.get_height(),
                            self.save_button.rect.height)
        self._controls_start_y = (self.panel_rect.top + header_height
                                  + padding * 2)

    def _build_controls(self) -> None:
        self.controls.clear()
        self._control_map.clear()
        self._apply_buttons.clear()
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        label_x = self.panel_rect.left + padding
        control_x = self.panel_rect.left + 260
        current_y = self._controls_start_y
        line_gap = padding
        slider_width = self.panel_rect.right - control_x - 140
        for item in self._theme_items():
            if item.is_section:
                control = self._build_section_header_control(
                    item.name,
                    label_x,
                    current_y,
                )
                self.controls.append(control)
                current_y += control.height + line_gap
                continue
            name = item.name
            value = item.value
            if name not in self._pending_values:
                self._pending_values[name] = value
            label = name.replace("THEME_", "").replace("_", " ")
            if name.endswith("_TINT_COLOR"):
                enabled = value is not None
                initial_value = value if value is not None else (0, 0, 0, 255)
                control = self._build_color_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    initial_value,
                    slider_width,
                    optional=True,
                    enabled=enabled,
                )
            elif isinstance(value, tuple):
                control = self._build_color_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                    slider_width,
                    optional=False,
                    enabled=True,
                )
            elif name.endswith("_IMAGE"):
                control = self._build_image_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                )
            elif name.endswith("_SCALE_MODE"):
                control = self._build_scale_mode_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                )
            elif isinstance(value, float) and name.endswith("_BLUR_RADIUS"):
                control = self._build_float_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                    min_value=0,
                    max_value=30,
                )
            elif isinstance(value, int) and name.startswith("THEME_FONT_SIZE_"):
                control = self._build_int_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                    min_value=8,
                    max_value=160,
                )
            elif isinstance(value, (int, float)):
                control = self._build_int_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                    min_value=0,
                    max_value=400,
                )
            elif isinstance(value, str) or value is None:
                control = self._build_text_control(
                    name,
                    label,
                    label_x,
                    control_x,
                    current_y,
                    value,
                )
            else:
                continue
            self.controls.append(control)
            self._control_map[name] = control
            current_y += control.height + line_gap
        self._update_scroll_bounds(current_y)

    def _get_pending_value(self, name: str) -> typing.Any:
        if name in self._pending_values:
            return self._pending_values[name]
        return getattr(theme, name)

    def _set_pending_value(self, name: str, value: typing.Any) -> None:
        self._pending_values[name] = value
        if getattr(theme, name, None) == value:
            self._dirty_names.discard(name)
        else:
            self._dirty_names.add(name)
        self._update_apply_button_state(name)

    def _update_apply_button_state(self, name: str) -> None:
        apply_button = self._apply_buttons.get(name)
        if not apply_button:
            return
        apply_button.set_disabled(name not in self._dirty_names)

    def _apply_pending_value(self, name: str) -> None:
        if name not in self._pending_values:
            return
        value = self._pending_values[name]
        if not theme.apply_theme_update(name, value):
            self._dirty_names.discard(name)
            self._update_apply_button_state(name)
            return
        self._dirty_names.discard(name)
        self._update_apply_button_state(name)
        self._on_theme_update(name)
        if self._needs_full_refresh(name):
            self.refresh_theme()
        else:
            control = self._control_map.get(name)
            if control and not control.is_section:
                control.sync()

    @staticmethod
    def _needs_full_refresh(name: str) -> bool:
        if name in {"THEME_TEXT_COLOR_LIGHT", "THEME_SCENE_HEADER_TEXT_COLOR"}:
            return True
        return name.startswith("THEME_FONT_") or name.startswith(
            "THEME_LAYOUT_"
        )

    def _theme_items(self) -> list[ThemeItem]:
        items: list[ThemeItem] = []
        included: set[str] = set()

        def add_item(name: str) -> None:
            if name in included or not hasattr(theme, name):
                return
            value = getattr(theme, name)
            if callable(value) or isinstance(value, dict):
                return
            items.append(ThemeItem(name=name, value=value))
            included.add(name)

        def add_section(title: str, names: list[str]) -> None:
            section_items: list[str] = []
            for name in names:
                if not hasattr(theme, name):
                    continue
                value = getattr(theme, name)
                if callable(value) or isinstance(value, dict):
                    continue
                if name in included:
                    continue
                section_items.append(name)
            if not section_items:
                return
            items.append(ThemeItem(name=title, value=None, is_section=True))
            for name in section_items:
                add_item(name)

        def add_section_by_prefix(title: str, prefixes: list[str]) -> None:
            names = [
                name for name in sorted(dir(theme))
                if name.startswith(tuple(prefixes))
            ]
            add_section(title, names)

        add_section(
            "Layout",
            [
                "THEME_LAYOUT_VERTICAL_GAP",
                "THEME_LAYOUT_SECTION_GAP",
                "THEME_LAYOUT_BUTTON_SECTION_GAP",
                "THEME_LAYOUT_LINE_GAP",
                "THEME_SCENE_HEADER_TOP_PADDING",
                "THEME_SCENE_HEADER_HEIGHT",
                "THEME_HELP_MAX_WIDTH",
                "THEME_SECTION_DIVIDER_PADDING",
                "THEME_SECTION_DIVIDER_COLOR",
            ],
        )
        add_section(
            "Typography",
            sorted([
                name for name in dir(theme)
                if name.startswith("THEME_FONT_SIZE_")
                or name.startswith("THEME_FONT_FAMILY_")
            ]) + [
                "THEME_TEXT_COLOR_LIGHT",
                "THEME_SECTION_HEADER_COLOR",
                "THEME_SUBSECTION_COLOR",
                "THEME_LABEL_DISABLED_COLOR",
            ],
        )
        add_section(
            "Scene Headers",
            [
                "THEME_SCENE_HEADER_BG_COLOR",
                "THEME_SCENE_HEADER_BACKGROUND_IMAGE",
                "THEME_SCENE_HEADER_BACKGROUND_SCALE_MODE",
                "THEME_SCENE_HEADER_BACKGROUND_TINT_COLOR",
                "THEME_SCENE_HEADER_BLUR_RADIUS",
                "THEME_SCENE_HEADER_TEXT_COLOR",
            ],
        )
        add_section(
            "UI Effects",
            [
                "THEME_UI_ALPHA_BLUR_RADIUS",
            ],
        )
        add_section(
            "Scene Backgrounds",
            [
                name for name in sorted(dir(theme))
                if name.startswith(
                    (
                        "THEME_MAIN_MENU_BACKGROUND_",
                        "THEME_SETTINGS_BACKGROUND_",
                        "THEME_HELP_BACKGROUND_",
                        "THEME_LOBBY_BACKGROUND_",
                        "THEME_PREPARE_BACKGROUND_",
                        "THEME_GAME_BACKGROUND_",
                    )
                )
            ],
        )
        add_section_by_prefix("Buttons", ["THEME_BUTTON_"])
        add_section_by_prefix("Inputs", ["THEME_INPUT_"])
        add_section_by_prefix("Checkboxes", ["THEME_CHECKBOX_"])
        add_section_by_prefix("Dropdowns", ["THEME_DROPDOWN_"])
        add_section_by_prefix("Sliders", ["THEME_SLIDER_"])
        add_section_by_prefix("Progress Bars", ["THEME_PROGRESS_BAR_"])
        add_section_by_prefix("Menu Dialogs", ["THEME_MENU_"])
        add_section_by_prefix("Lobby Status", ["THEME_LOBBY_STATUS_"])
        add_section(
            "Game UI",
            [
                name for name in sorted(dir(theme))
                if name.startswith("THEME_GAME_")
                and not name.startswith("THEME_GAME_LOG_")
            ],
        )
        add_section_by_prefix("Game Log", ["THEME_GAME_LOG_"])
        add_section_by_prefix("Toasts", ["THEME_TOAST_"])
        add_section_by_prefix("Player Colors", ["THEME_PLAYER_COLOR_"])
        add_section(
            "Miscellaneous",
            [
                name for name in sorted(dir(theme))
                if name.startswith("THEME_") and name not in included
            ],
        )
        return items

    def _build_section_header_control(
        self,
        title: str,
        label_x: int,
        start_y: int,
    ) -> ThemeControl:
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        label_surface = self.section_font.render(
            title, True, theme.THEME_SECTION_HEADER_COLOR
        )

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            return

        def sync() -> None:
            nonlocal label_surface
            label_surface = self.section_font.render(
                title, True, theme.THEME_SECTION_HEADER_COLOR
            )

        height = label_surface.get_height() + padding // 2
        return ThemeControl(
            name=title,
            label=title,
            y=start_y,
            height=height,
            components=[],
            draw=draw,
            handle_event=handle_event,
            sync=sync,
            is_section=True,
        )

    def _build_color_control(
        self,
        name: str,
        label: str,
        label_x: int,
        control_x: int,
        start_y: int,
        value: tuple,
        slider_width: int,
        optional: bool = False,
        enabled: bool = True,
    ) -> ThemeControl:
        display_value = self._get_pending_value(name)
        enabled = display_value is not None
        if display_value is None:
            channels = self._normalize_color_channels(
                self._optional_values.get(name, [0, 0, 0, 255])
            )
        else:
            channels = self._normalize_color_channels(display_value)
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        slider_height = 20
        channel_gap = max(4, padding // 2)
        label_height = self.label_font.get_height()
        sliders: list[Slider] = []
        channel_labels = ["R", "G", "B", "A"][:len(channels)]
        checkbox = None
        swatch_size = 26
        swatch_margin = 10

        def build_sliders(y_offset: int) -> None:
            for idx, channel in enumerate(channels):
                slider_y = (y_offset + label_height + padding // 2
                            + idx * (slider_height + channel_gap))
                slider = Slider(
                    rect=(control_x + 20, slider_y, slider_width, slider_height),
                    font=self.control_font,
                    min_value=0,
                    max_value=255,
                    value=int(channel),
                    on_change=lambda val, i=idx: self._update_color_channel(
                        name, i, val
                    ),
                )
                sliders.append(slider)

        build_sliders(start_y)

        if optional:
            checkbox = Checkbox(
                rect=(control_x, start_y, 20, 20),
                checked=enabled,
                on_toggle=lambda enabled: self._toggle_optional_color(
                    name, enabled, sliders
                ),
            )
            if not enabled:
                for slider in sliders:
                    slider.set_disabled(True)

        height = (label_height + (slider_height + channel_gap) * len(sliders)
                  + padding // 2)
        apply_button = Button(
            rect=pygame.Rect(0, 0, 0, 24),
            text="Apply",
            font=self.apply_font,
            callback=lambda: self._apply_pending_value(name),
        )
        apply_button.rect.center = (
            self.panel_rect.right - padding - apply_button.rect.width // 2,
            start_y + height // 2,
        )
        self._apply_buttons[name] = apply_button
        self._update_apply_button_state(name)
        components: list[typing.Any] = sliders[:]
        if checkbox is not None:
            components.insert(0, checkbox)
        components.append(apply_button)

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))
            if checkbox is not None:
                checkbox.draw(surface, y_offset=y_offset)
                surface.blit(enabled_label,
                             (control_x + 26, start_y + y_offset))
            for idx, slider in enumerate(sliders):
                label_y = (start_y + y_offset + label_height + padding // 2
                           + idx * (slider_height + channel_gap))
                surface.blit(channel_label_surfaces[idx],
                             (control_x, label_y - 2))
                slider.draw(surface, y_offset=y_offset)
            if checkbox is None or checkbox.checked:
                swatch_x = control_x + slider_width + swatch_margin
                swatch_y = start_y + y_offset + label_height + padding // 2
                swatch_surface = pygame.Surface(
                    (swatch_size, swatch_size), pygame.SRCALPHA
                )
                swatch_color = tuple(int(slider.value) for slider in sliders)
                swatch_surface.fill(swatch_color)
                surface.blit(swatch_surface, (swatch_x, swatch_y))
                pygame.draw.rect(
                    surface,
                    theme.THEME_TEXT_COLOR_LIGHT,
                    pygame.Rect(swatch_x, swatch_y, swatch_size, swatch_size),
                    1,
                )
            apply_button.draw(surface, y_offset=y_offset)

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            if checkbox is not None:
                checkbox.handle_event(event, y_offset=y_offset)
            for slider in sliders:
                slider.handle_event(event, y_offset=y_offset)
            apply_button.handle_event(event, y_offset=y_offset)

        def _refresh_label_surfaces() -> None:
            nonlocal label_surface
            nonlocal enabled_label
            nonlocal channel_label_surfaces
            label_surface = self.label_font.render(
                label, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            enabled_label = self.label_font.render(
                "Enabled", True, theme.THEME_TEXT_COLOR_LIGHT
            )
            channel_label_surfaces = [
                self.label_font.render(
                    channel_label, True, theme.THEME_TEXT_COLOR_LIGHT
                ) for channel_label in channel_labels
            ]

        label_surface = None
        enabled_label = None
        channel_label_surfaces: list[pygame.Surface] = []
        _refresh_label_surfaces()

        def sync() -> None:
            _refresh_label_surfaces()
            current_value = (self._get_pending_value(name)
                             if name in self._dirty_names else
                             getattr(theme, name))
            if optional and current_value is None:
                if checkbox is not None:
                    checkbox.set_checked(False)
                for slider in sliders:
                    slider.set_disabled(True)
                    slider.apply_theme()
                    slider.set_font(self.control_font)
                if checkbox is not None:
                    checkbox.apply_theme()
                apply_button.apply_theme()
                apply_button.set_font(self.apply_font)
                self._update_apply_button_state(name)
                return
            if checkbox is not None:
                checkbox.set_checked(True)
                for slider in sliders:
                    slider.set_disabled(False)
            current_channels = self._normalize_color_channels(current_value)
            for idx, slider in enumerate(sliders):
                slider.set_value(int(current_channels[idx]))
                slider.apply_theme()
                slider.set_font(self.control_font)
            if checkbox is not None:
                checkbox.apply_theme()
            apply_button.apply_theme()
            apply_button.set_font(self.apply_font)
            self._update_apply_button_state(name)

        return ThemeControl(
            name=name,
            label=label,
            y=start_y,
            height=height,
            components=components,
            draw=draw,
            handle_event=handle_event,
            sync=sync,
        )

    def _build_int_control(
        self,
        name: str,
        label: str,
        label_x: int,
        control_x: int,
        start_y: int,
        value: typing.Union[int, float],
        min_value: int,
        max_value: int,
    ) -> ThemeControl:
        display_value = self._get_pending_value(name)
        slider = Slider(
            rect=(control_x, start_y, 200, 20),
            font=self.control_font,
            min_value=min_value,
            max_value=max_value,
            value=int(display_value),
            on_change=lambda val: self._set_pending_value(name, int(val)),
        )
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        height = max(self.label_font.get_height(), slider.rect.height)
        apply_button = Button(
            rect=pygame.Rect(0, 0, 0, 24),
            text="Apply",
            font=self.apply_font,
            callback=lambda: self._apply_pending_value(name),
        )
        apply_button.rect.center = (
            self.panel_rect.right - padding - apply_button.rect.width // 2,
            start_y + height // 2,
        )
        self._apply_buttons[name] = apply_button
        self._update_apply_button_state(name)

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))
            slider.draw(surface, y_offset=y_offset)
            apply_button.draw(surface, y_offset=y_offset)

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            slider.handle_event(event, y_offset=y_offset)
            apply_button.handle_event(event, y_offset=y_offset)

        def sync() -> None:
            nonlocal label_surface
            label_surface = self.label_font.render(
                label, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            current_value = (self._get_pending_value(name)
                             if name in self._dirty_names else
                             getattr(theme, name))
            slider.set_value(int(current_value))
            slider.apply_theme()
            slider.set_font(self.control_font)
            apply_button.apply_theme()
            apply_button.set_font(self.apply_font)
            self._update_apply_button_state(name)

        label_surface = self.label_font.render(
            label, True, theme.THEME_TEXT_COLOR_LIGHT
        )

        return ThemeControl(
            name=name,
            label=label,
            y=start_y,
            height=height,
            components=[slider, apply_button],
            draw=draw,
            handle_event=handle_event,
            sync=sync,
        )

    def _build_float_control(
        self,
        name: str,
        label: str,
        label_x: int,
        control_x: int,
        start_y: int,
        value: float,
        min_value: int,
        max_value: int,
    ) -> ThemeControl:
        display_value = self._get_pending_value(name)
        slider = Slider(
            rect=(control_x, start_y, 200, 20),
            font=self.control_font,
            min_value=min_value,
            max_value=max_value,
            value=int(display_value),
            on_change=lambda val: self._set_pending_value(name, float(val)),
        )
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        height = max(self.label_font.get_height(), slider.rect.height)
        apply_button = Button(
            rect=pygame.Rect(0, 0, 0, 24),
            text="Apply",
            font=self.apply_font,
            callback=lambda: self._apply_pending_value(name),
        )
        apply_button.rect.center = (
            self.panel_rect.right - padding - apply_button.rect.width // 2,
            start_y + height // 2,
        )
        self._apply_buttons[name] = apply_button
        self._update_apply_button_state(name)

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))
            slider.draw(surface, y_offset=y_offset)
            apply_button.draw(surface, y_offset=y_offset)

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            slider.handle_event(event, y_offset=y_offset)
            apply_button.handle_event(event, y_offset=y_offset)

        def sync() -> None:
            nonlocal label_surface
            label_surface = self.label_font.render(
                label, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            current_value = (self._get_pending_value(name)
                             if name in self._dirty_names else
                             getattr(theme, name))
            slider.set_value(int(current_value))
            slider.apply_theme()
            slider.set_font(self.control_font)
            apply_button.apply_theme()
            apply_button.set_font(self.apply_font)
            self._update_apply_button_state(name)

        label_surface = self.label_font.render(
            label, True, theme.THEME_TEXT_COLOR_LIGHT
        )

        return ThemeControl(
            name=name,
            label=label,
            y=start_y,
            height=height,
            components=[slider, apply_button],
            draw=draw,
            handle_event=handle_event,
            sync=sync,
        )

    def _build_text_control(
        self,
        name: str,
        label: str,
        label_x: int,
        control_x: int,
        start_y: int,
        value: str | None,
    ) -> ThemeControl:
        display_value = self._get_pending_value(name)
        input_field = InputField(
            rect=(control_x, start_y, 220, 28),
            font=self.control_font,
            initial_text="" if display_value is None else str(display_value),
            on_text_change=lambda text: self._set_pending_value(
                name, text if text else None
            ),
            commit_on_blur=True,
        )
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        height = max(self.label_font.get_height(), input_field.rect.height)
        apply_button = Button(
            rect=pygame.Rect(0, 0, 0, 24),
            text="Apply",
            font=self.apply_font,
            callback=lambda: self._apply_pending_value(name),
        )
        apply_button.rect.center = (
            self.panel_rect.right - padding - apply_button.rect.width // 2,
            start_y + height // 2,
        )
        self._apply_buttons[name] = apply_button
        self._update_apply_button_state(name)

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))
            input_field.draw(surface, y_offset=y_offset)
            apply_button.draw(surface, y_offset=y_offset)

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            input_field.handle_event(event, y_offset=y_offset)
            apply_button.handle_event(event, y_offset=y_offset)

        def sync() -> None:
            nonlocal label_surface
            label_surface = self.label_font.render(
                label, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            current_value = (self._get_pending_value(name)
                             if name in self._dirty_names else
                             getattr(theme, name))
            input_field.set_text("" if current_value is None else
                                 str(current_value))
            input_field.apply_theme()
            input_field.set_font(self.control_font)
            apply_button.apply_theme()
            apply_button.set_font(self.apply_font)
            self._update_apply_button_state(name)

        label_surface = self.label_font.render(
            label, True, theme.THEME_TEXT_COLOR_LIGHT
        )

        return ThemeControl(
            name=name,
            label=label,
            y=start_y,
            height=height,
            components=[input_field, apply_button],
            draw=draw,
            handle_event=handle_event,
            sync=sync,
        )

    def _build_image_control(
        self,
        name: str,
        label: str,
        label_x: int,
        control_x: int,
        start_y: int,
        value: str | None,
    ) -> ThemeControl:
        display_value = self._get_pending_value(name)
        def handle_toggle(enabled: bool) -> None:
            self._toggle_image(enabled, name)
            input_field.set_disabled(not enabled)

        checkbox = Checkbox(
            rect=(control_x, start_y, 20, 20),
            checked=display_value is not None,
            on_toggle=handle_toggle,
        )
        input_field = InputField(
            rect=(control_x + 80, start_y, 200, 28),
            font=self.control_font,
            initial_text="" if display_value is None else str(display_value),
            on_text_change=lambda text: self._update_image_path(name, text),
            commit_on_blur=True,
        )
        if display_value is None:
            input_field.set_disabled(True)
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        height = max(
            self.label_font.get_height(),
            checkbox.rect.height,
            input_field.rect.height,
        )
        apply_button = Button(
            rect=pygame.Rect(0, 0, 0, 24),
            text="Apply",
            font=self.apply_font,
            callback=lambda: self._apply_pending_value(name),
        )
        apply_button.rect.center = (
            self.panel_rect.right - padding - apply_button.rect.width // 2,
            start_y + height // 2,
        )
        self._apply_buttons[name] = apply_button
        self._update_apply_button_state(name)

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))
            checkbox.draw(surface, y_offset=y_offset)
            surface.blit(enabled_label, (control_x + 26, start_y + y_offset))
            input_field.draw(surface, y_offset=y_offset)
            apply_button.draw(surface, y_offset=y_offset)

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            checkbox.handle_event(event, y_offset=y_offset)
            input_field.handle_event(event, y_offset=y_offset)
            apply_button.handle_event(event, y_offset=y_offset)

        def sync() -> None:
            nonlocal label_surface
            nonlocal enabled_label
            label_surface = self.label_font.render(
                label, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            enabled_label = self.label_font.render(
                "Enabled", True, theme.THEME_TEXT_COLOR_LIGHT
            )
            current_value = (self._get_pending_value(name)
                             if name in self._dirty_names else
                             getattr(theme, name))
            checkbox.set_checked(current_value is not None)
            input_field.set_text("" if current_value is None else
                                 str(current_value))
            input_field.set_disabled(current_value is None)
            checkbox.apply_theme()
            input_field.apply_theme()
            input_field.set_font(self.control_font)
            apply_button.apply_theme()
            apply_button.set_font(self.apply_font)
            self._update_apply_button_state(name)

        label_surface = self.label_font.render(
            label, True, theme.THEME_TEXT_COLOR_LIGHT
        )
        enabled_label = self.label_font.render(
            "Enabled", True, theme.THEME_TEXT_COLOR_LIGHT
        )

        return ThemeControl(
            name=name,
            label=label,
            y=start_y,
            height=height,
            components=[checkbox, input_field, apply_button],
            draw=draw,
            handle_event=handle_event,
            sync=sync,
        )

    def _build_scale_mode_control(
        self,
        name: str,
        label: str,
        label_x: int,
        control_x: int,
        start_y: int,
        value: str,
    ) -> ThemeControl:
        options = ["fill", "fit", "stretch"]
        display_value = self._get_pending_value(name)
        selected = options.index(display_value) if display_value in options else 0
        dropdown = Dropdown(
            rect=(control_x, start_y, 160, 28),
            font=self.control_font,
            options=options,
            default_index=selected,
            on_select=lambda option: self._set_pending_value(name, option),
        )
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        height = max(self.label_font.get_height(), dropdown.rect.height)
        apply_button = Button(
            rect=pygame.Rect(0, 0, 0, 24),
            text="Apply",
            font=self.apply_font,
            callback=lambda: self._apply_pending_value(name),
        )
        apply_button.rect.center = (
            self.panel_rect.right - padding - apply_button.rect.width // 2,
            start_y + height // 2,
        )
        self._apply_buttons[name] = apply_button
        self._update_apply_button_state(name)

        def draw(surface: pygame.Surface, y_offset: int) -> None:
            surface.blit(label_surface, (label_x, start_y + y_offset))
            dropdown.draw(surface, y_offset=y_offset)
            apply_button.draw(surface, y_offset=y_offset)

        def handle_event(event: pygame.event.Event, y_offset: int) -> None:
            dropdown.handle_event(event, y_offset=y_offset)
            apply_button.handle_event(event, y_offset=y_offset)

        def sync() -> None:
            nonlocal label_surface
            label_surface = self.label_font.render(
                label, True, theme.THEME_TEXT_COLOR_LIGHT
            )
            current_value = (self._get_pending_value(name)
                             if name in self._dirty_names else
                             getattr(theme, name))
            if current_value in options:
                dropdown.set_selected(options.index(current_value))
            else:
                dropdown.set_selected(0)
            dropdown.apply_theme()
            dropdown.set_font(self.control_font)
            apply_button.apply_theme()
            apply_button.set_font(self.apply_font)
            self._update_apply_button_state(name)

        label_surface = self.label_font.render(
            label, True, theme.THEME_TEXT_COLOR_LIGHT
        )

        return ThemeControl(
            name=name,
            label=label,
            y=start_y,
            height=height,
            components=[dropdown, apply_button],
            draw=draw,
            handle_event=handle_event,
            sync=sync,
        )

    def _toggle_optional_color(self, name: str, enabled: bool,
                               sliders: list[Slider]) -> None:
        if enabled:
            restored = self._optional_values.get(name, [0, 0, 0, 255])
            self._set_pending_value(name, tuple(restored))
            for slider in sliders:
                slider.set_disabled(False)
        else:
            current_value = self._get_pending_value(name)
            if current_value is not None:
                self._optional_values[name] = list(current_value)
            self._set_pending_value(name, None)
            for slider in sliders:
                slider.set_disabled(True)

    def _toggle_image(self, enabled: bool, name: str) -> None:
        if enabled:
            last_value = self._optional_values.get(name, "")
            self._set_pending_value(
                name, last_value if last_value is not None else ""
            )
        else:
            current_value = self._get_pending_value(name)
            if current_value is not None:
                self._optional_values[name] = current_value
            self._set_pending_value(name, None)

    def _update_image_path(self, name: str, text: str) -> None:
        if self._get_pending_value(name) is None:
            return
        self._set_pending_value(name, text if text else "")

    def _update_color_channel(self, name: str, channel_index: int,
                              value: int) -> None:
        current_value = self._get_pending_value(name)
        if current_value is None:
            current = self._optional_values.get(name, [0, 0, 0, 255])
        else:
            current = self._normalize_color_channels(current_value)
        current[channel_index] = int(value)
        self._set_pending_value(name, tuple(current))

    def _normalize_color_channels(self, value: tuple) -> list[int]:
        channels = list(value)
        if len(channels) < 3:
            channels.extend([0] * (3 - len(channels)))
        return channels[:4]

    def _update_scroll_bounds(self, content_end_y: int) -> None:
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        content_height = content_end_y - self._controls_start_y
        view_height = (self.panel_rect.height
                       - (self._controls_start_y - self.panel_rect.top)
                       - padding)
        self.max_scroll = max(0, content_height - view_height)
        self.scroll_offset = max(-self.max_scroll, min(0, self.scroll_offset))

    def _save_theme(self) -> None:
        theme_path = theme.__file__
        if theme_path.endswith(".pyc"):
            theme_path = theme_path[:-1]
        with open(theme_path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        theme_values = {
            item.name: getattr(theme, item.name)
            for item in self._theme_items()
            if not item.is_section and hasattr(theme, item.name)
        }
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith("THEME_"):
                continue
            if "=" not in line:
                continue
            left = line.split("=")[0].rstrip()
            name = left.split(":")[0].strip()
            if name not in theme_values:
                continue
            new_value = self._format_value(theme_values[name])
            lines[idx] = f"{left} = {new_value}\n"
        with open(theme_path, "w", encoding="utf-8") as handle:
            handle.writelines(lines)

    def _format_value(self, value: typing.Any) -> str:
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
            return f"\"{escaped}\""
        if value is None:
            return "None"
        if isinstance(value, tuple):
            inner = ", ".join(self._format_value(item) for item in value)
            if len(value) == 1:
                inner = f"{inner},"
            return f"({inner})"
        return repr(value)

    def handle_events(
        self, events: list[pygame.event.Event]
    ) -> list[pygame.event.Event]:
        remaining: list[pygame.event.Event] = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F9:
                    self.toggle()
                    continue
                if (event.key == pygame.K_t and
                        (event.mod & pygame.KMOD_CTRL) and
                        (event.mod & pygame.KMOD_SHIFT)):
                    self.toggle()
                    continue
            if not self.active:
                self.toggle_button.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.toggle_button._is_clicked(event.pos):
                        continue
                remaining.append(event)
                continue
            if event.type == pygame.MOUSEWHEEL:
                if self.panel_rect.collidepoint(pygame.mouse.get_pos()):
                    self.scroll_offset += event.y * 20
                    self.scroll_offset = max(-self.max_scroll,
                                             min(0, self.scroll_offset))
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.toggle()
                continue
            dropdown_controls = [
                control for control in self.controls
                if any(isinstance(component, Dropdown)
                       for component in control.components)
            ]
            expanded_dropdowns = [
                control for control in dropdown_controls
                if any(component.expanded for component in control.components
                       if isinstance(component, Dropdown))
            ]
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and expanded_dropdowns):
                for control in expanded_dropdowns:
                    control.handle_event(event, self.scroll_offset)
                continue
            self.save_button.handle_event(event)
            for control in self.controls:
                control.handle_event(event, self.scroll_offset)
        if self.active:
            return []
        return remaining

    def refresh_theme(self) -> None:
        self._build_layout()
        self._build_controls()
        self.toggle_button.apply_theme()
        self.save_button.apply_theme()
        self.toggle_button.set_font(theme.get_font("button", 16))
        self.save_button.set_font(theme.get_font("button", 18))
        for control in self.controls:
            if control.is_section:
                continue
            control.sync()

    def toggle(self) -> None:
        self.active = not self.active
        if self.active:
            self.scroll_offset = 0
            padding = theme.THEME_LAYOUT_VERTICAL_GAP
            self._update_scroll_bounds(self._controls_start_y + sum(
                control.height + padding for control in self.controls
            ))
            for control in self.controls:
                if control.is_section:
                    continue
                control.sync()

    def draw(self) -> None:
        if not self.active:
            self.toggle_button.draw(self.screen)
            return
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Surface(self.panel_rect.size, pygame.SRCALPHA)
        panel.fill((30, 30, 30, 230))
        self.screen.blit(panel, self.panel_rect.topleft)
        pygame.draw.rect(self.screen, (200, 200, 200), self.panel_rect, 2)
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        title_x = (self.panel_rect.left +
                   (self.panel_rect.width - self._title_surface.get_width())
                   // 2)
        title_y = self.panel_rect.top + padding
        self.screen.blit(self._title_surface, (title_x, title_y))
        self.save_button.draw(self.screen)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(self.panel_rect)
        dropdown_controls = [
            control for control in self.controls
            if any(isinstance(component, Dropdown)
                   for component in control.components)
        ]
        non_dropdown_controls = [
            control for control in self.controls
            if control not in dropdown_controls
        ]
        expanded_dropdown_controls = [
            control for control in dropdown_controls
            if any(isinstance(component, Dropdown) and component.expanded
                   for component in control.components)
        ]
        collapsed_dropdown_controls = [
            control for control in dropdown_controls
            if control not in expanded_dropdown_controls
        ]
        for control in non_dropdown_controls:
            control.draw(self.screen, self.scroll_offset)
        for control in collapsed_dropdown_controls:
            control.draw(self.screen, self.scroll_offset)
        for control in expanded_dropdown_controls:
            control.draw(self.screen, self.scroll_offset)
        self.screen.set_clip(previous_clip)
