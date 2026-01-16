from __future__ import annotations

"""Centralized UI theme definitions and accessors.

Usage:
    from ui.theme import get_theme, set_theme, Theme, register_theme

    theme = get_theme()
    color = theme.color("text_primary")
    font = theme.font("button")

    # Experiment with fonts at runtime:
    theme.set_font_name("arial")
    theme.set_font_sizes({"button": 42, "body": 30, "dialog": 36})

    # Register a custom theme and switch to it:
    custom = Theme(name="custom", colors={...}, font_sizes={...})
    register_theme("custom", custom)
    set_theme("custom")
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import pygame

Color = Tuple[int, int, int]
ColorWithAlpha = Tuple[int, int, int, int]


@dataclass
class Theme:
    """Represents a UI theme with colors and fonts."""

    name: str
    colors: Dict[str, Color | ColorWithAlpha]
    font_sizes: Dict[str, int]
    font_name: Optional[str] = None
    _font_cache: Dict[int, pygame.font.Font] = field(
        default_factory=dict, init=False, repr=False
    )

    def get_font(self, size: int) -> pygame.font.Font:
        """Return a cached font for the requested size."""
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.Font(self.font_name, size)
        return self._font_cache[size]

    def font(self, key: str) -> pygame.font.Font:
        """Return a cached font for a named size in the theme."""
        return self.get_font(self.font_sizes[key])

    def color(self, key: str) -> Color | ColorWithAlpha:
        """Return a named color from the theme palette."""
        return self.colors[key]

    def set_font_name(self, font_name: Optional[str]) -> None:
        """Update the font name and clear cached fonts."""
        if font_name != self.font_name:
            self.font_name = font_name
            self._font_cache.clear()

    def set_font_sizes(self, font_sizes: Dict[str, int]) -> None:
        """Replace the font size map and clear cached fonts."""
        self.font_sizes = dict(font_sizes)
        self._font_cache.clear()


def _build_default_theme() -> Theme:
    return Theme(
        name="default",
        font_sizes={
            "menu_title": 100,
            "scene_title": 80,
            "button": 48,
            "dialog": 36,
            "controls": 32,
            "body": 36,
            "small": 28,
            "game_over": 72,
            "score_header": 48,
            "score_row": 42,
        },
        colors={
            "background": (30, 30, 30),
            "overlay": (0, 0, 0, 128),
            "dialog_bg": (60, 60, 60),
            "dialog_border": (200, 200, 200),
            "text_primary": (255, 255, 255),
            "text_secondary": (220, 220, 220),
            "text_accent": (255, 215, 0),
            "text_muted": (180, 180, 180),
            "text_disabled": (150, 150, 150),
            "text_dark": (0, 0, 0),
            "button_bg": (200, 200, 200),
            "button_hover_bg": (220, 220, 220),
            "button_pressed_bg": (160, 160, 160),
            "button_disabled_bg": (180, 180, 180),
            "button_text": (0, 0, 0),
            "button_text_disabled": (150, 150, 150),
            "checkbox_box": (255, 255, 255),
            "checkbox_check": (0, 200, 0),
            "checkbox_border": (255, 255, 255),
            "checkbox_disabled": (100, 100, 100),
            "checkbox_hover_fill": (230, 230, 230),
            "dropdown_text": (0, 0, 0),
            "dropdown_bg": (255, 255, 255),
            "dropdown_border": (0, 0, 0),
            "dropdown_highlight": (200, 200, 200),
            "dropdown_hover_bg": (240, 240, 240),
            "input_text": (0, 0, 0),
            "input_bg": (255, 255, 255),
            "input_border": (0, 0, 0),
            "input_placeholder": (150, 150, 150),
            "input_disabled_bg": (200, 200, 200),
            "input_disabled_border": (100, 100, 100),
            "slider_bg": (200, 200, 200),
            "slider_fg": (100, 100, 255),
            "slider_handle": (255, 255, 255),
            "slider_border": (0, 0, 0),
            "slider_handle_hover": (235, 235, 255),
            "slider_handle_active": (180, 180, 255),
            "slider_track_hover": (120, 120, 255),
            "slider_track_active": (80, 80, 230),
            "slider_border_hover": (50, 50, 50),
            "slider_disabled_bg": (100, 100, 100),
            "slider_disabled_fg": (60, 60, 60),
            "slider_disabled_handle": (150, 150, 150),
            "slider_disabled_border": (80, 80, 80),
            "progress_bg": (80, 80, 80),
            "progress_fg": (100, 255, 100),
            "progress_border": (150, 150, 150),
            "progress_text": (255, 255, 255),
            "toast_info_bg": (30, 30, 30),
            "toast_info_text": (255, 255, 255),
            "toast_success_bg": (255, 255, 255),
            "toast_success_text": (0, 128, 0),
            "toast_error_bg": (255, 255, 255),
            "toast_error_text": (128, 0, 0),
            "toast_warning_bg": (0, 0, 0),
            "toast_warning_text": (255, 215, 0),
            "log_overlay": (0, 0, 0, 200),
            "log_title_bg": (50, 50, 50, 180),
            "log_scroll_bg": (0, 0, 0, 150),
            "log_scroll_text": (180, 180, 180),
            "log_info": (240, 240, 240),
            "log_debug": (150, 200, 255),
            "log_scoring": (255, 255, 0),
            "log_warning": (255, 220, 100),
            "log_error": (255, 120, 120),
            "log_info_bg": (0, 0, 0, 0),
            "log_debug_bg": (0, 50, 100, 30),
            "log_scoring_bg": (80, 80, 0, 40),
            "log_warning_bg": (100, 80, 0, 40),
            "log_error_bg": (100, 0, 0, 50),
            "transparent": (0, 0, 0, 0),
            "game_board_bg": (25, 25, 25),
            "game_panel_bg": (40, 40, 40),
            "game_panel_border": (100, 100, 100),
            "game_sidebar_bg": (50, 50, 50),
            "game_table_bg": (40, 40, 40),
            "game_table_line": (100, 100, 100),
            "game_table_row_line": (70, 70, 70),
            "game_highlight": (255, 255, 0),
            "game_highlight_overlay": (255, 255, 0, 100),
            "game_hover_overlay": (255, 255, 0, 150),
            "game_grid_line": (0, 0, 0),
            "game_score_bg": (70, 70, 70),
            "game_score_border": (100, 100, 100),
            "game_status_wait": (100, 100, 255),
            "game_status_ready": (0, 255, 0),
            "game_status_blocked": (200, 0, 0),
            "game_thinking": (255, 255, 100),
            "game_tile_preview_bg": (60, 80, 120),
            "game_tile_preview_border": (100, 150, 255),
            "player_red": (255, 100, 100),
            "player_blue": (100, 100, 255),
            "player_green": (100, 255, 100),
            "player_yellow": (255, 255, 100),
            "player_pink": (255, 100, 255),
            "player_black": (200, 200, 200),
        },
    )


_THEMES = {
    "default": _build_default_theme(),
}

_current_theme = _THEMES["default"]


def get_theme() -> Theme:
    """Return the current theme."""
    return _current_theme


def set_theme(theme: str | Theme) -> Theme:
    """Set the current theme by name or by Theme instance."""
    global _current_theme
    if isinstance(theme, Theme):
        _current_theme = theme
        return _current_theme
    if theme not in _THEMES:
        raise ValueError(f"Unknown theme: {theme}")
    _current_theme = _THEMES[theme]
    return _current_theme


def register_theme(name: str, theme: Theme) -> None:
    """Register a custom theme for later use."""
    _THEMES[name] = theme
