"""Centralized UI theme constants and font helpers."""

from __future__ import annotations

import os
import typing

import pygame

import settings

Color = tuple[int, int, int] | tuple[int, int, int, int]
ColorA = tuple[int, int, int, int]

# Font sizes
# Main menu title text size in pixels; integer size typically between 48-140.
THEME_FONT_SIZE_MAIN_MENU_TITLE: int = 96
# Scene title size (help/lobby/setup/settings); integer size typically 48-120.
THEME_FONT_SIZE_SCENE_TITLE: int = 72
# Section header size for in-scene group headers; integer size typically 20-48.
THEME_FONT_SIZE_SECTION_HEADER: int = 26
# Large game-over headline size; integer size typically 56-96.
THEME_FONT_SIZE_GAME_OVER_TITLE: int = 48
# Button/label size for menu controls and score table headers; integer size 32-64.
THEME_FONT_SIZE_BUTTON: int = 28
# Score table row font size in the game-over panel; integer size 28-56.
THEME_FONT_SIZE_GAME_OVER_ROW: int = 24
# Standard UI body text size (dialogs, inputs, toast, game HUD); integer size 24-48.
THEME_FONT_SIZE_BODY: int = 18
# Help scene control text size; integer size 20-40.
THEME_FONT_SIZE_HELP_CONTROLS: int = 24
# Game log body text size; integer size 18-32.
THEME_FONT_SIZE_GAME_LOG_BODY: int = 24

# Font families (asset filename or system font name).
# Title text font family name or file in assets/fonts/; None uses default pygame font.
THEME_FONT_FAMILY_TITLE: str | None = "CinzelDecorative-Bold.ttf"
# Section header font family name or file in assets/fonts/; None uses default pygame font.
THEME_FONT_FAMILY_SECTION_HEADER: str | None = "Marcellus-Regular.ttf"
# Body text font family name or file in assets/fonts/; None uses default pygame font.
THEME_FONT_FAMILY_BODY: str | None = "EBGaramond-Regular.ttf"
# Label text font family name or file in assets/fonts/; None uses default pygame font.
THEME_FONT_FAMILY_LABEL: str | None = "EBGaramond-Regular.ttf"
# Button text font family name or file in assets/fonts/; None uses default pygame font.
THEME_FONT_FAMILY_BUTTON: str | None = "EBGaramond-Bold.ttf"

# Layout spacing
# Vertical gap between stacked UI components; integer size in pixels.
THEME_LAYOUT_VERTICAL_GAP: int = 12
# Extra vertical spacing between help sections; integer size in pixels.
THEME_LAYOUT_SECTION_GAP: int = 24
# Extra vertical spacing between content and bottom action buttons.
THEME_LAYOUT_BUTTON_SECTION_GAP: int = 36
# Vertical spacing between help body text lines; integer size in pixels.
THEME_LAYOUT_LINE_GAP: int = 8
# Scene header padding above/below the title; integer size in pixels.
THEME_SCENE_HEADER_TOP_PADDING: int = 12
# Optional explicit scene header height override; 0 uses title height + padding.
THEME_SCENE_HEADER_HEIGHT: int = 0
# Help content max width cap; integer size in pixels.
THEME_HELP_MAX_WIDTH: int = 900
# Padding above/below help section dividers; integer size in pixels.
THEME_SECTION_DIVIDER_PADDING: int = 6

# Button colors
# Horizontal padding applied on each side of button labels; integer size in pixels.
THEME_BUTTON_HORIZONTAL_PADDING: int = 12
# Vertical padding applied above/below button labels; integer size in pixels.
THEME_BUTTON_VERTICAL_PADDING: int = 6
# Default state
# Background for default button state; RGB tuple (0-255 per channel).
THEME_BUTTON_BG_COLOR: Color = (42, 42, 42, 100)
# Hover state
# Background for hovered button state; RGB tuple (0-255 per channel).
THEME_BUTTON_HOVER_BG_COLOR: Color = (32, 32, 32, 180)
# Active/pressed state
# Background for pressed button state; RGB tuple (0-255 per channel).
THEME_BUTTON_PRESSED_BG_COLOR: Color = (22, 22, 22, 180)
# Default text
# Text color for enabled buttons; RGB tuple (0-255 per channel).
THEME_BUTTON_TEXT_COLOR: Color = (190, 190, 190)
# Disabled state
# Text color for disabled buttons; RGB tuple (0-255 per channel).
THEME_BUTTON_TEXT_DISABLED_COLOR: Color = (130, 130, 130)
# Background for disabled buttons; RGB tuple (0-255 per channel).
THEME_BUTTON_DISABLED_BG_COLOR: Color = (110, 110, 110, 100)

# Checkbox colors
# Default state
# Checkbox fill when unchecked; RGB tuple (0-255 per channel).
THEME_CHECKBOX_BOX_COLOR: Color = (255, 255, 255, 255)
# Active/checked state
# Checkbox checkmark fill; RGB tuple (0-255 per channel).
THEME_CHECKBOX_CHECK_COLOR: Color = (0, 200, 0, 255)
# Default border
# Checkbox border color; RGB tuple (0-255 per channel).
THEME_CHECKBOX_BORDER_COLOR: Color = (255, 255, 255, 255)
# Hover state
# Checkbox hover fill when unchecked; RGB tuple (0-255 per channel).
THEME_CHECKBOX_HOVER_BOX_COLOR: Color = (235, 235, 235, 255)
# Disabled state
# Checkbox color when disabled (border/check); RGB tuple (0-255 per channel).
THEME_CHECKBOX_DISABLED_COLOR: Color = (100, 100, 100, 255)

# Dropdown colors
# Default state
# Dropdown text color; RGB tuple (0-255 per channel).
THEME_DROPDOWN_TEXT_COLOR: Color = (0, 0, 0)
# Dropdown background color; RGB tuple (0-255 per channel).
THEME_DROPDOWN_BG_COLOR: Color = (255, 255, 255, 255)
# Dropdown border color; RGB tuple (0-255 per channel).
THEME_DROPDOWN_BORDER_COLOR: Color = (0, 0, 0, 255)
# Active/selected state
# Dropdown selected option highlight; RGB tuple (0-255 per channel).
THEME_DROPDOWN_HIGHLIGHT_COLOR: Color = (200, 200, 200, 255)
# Hover state
# Dropdown background when hovering the control; RGB tuple (0-255 per channel).
THEME_DROPDOWN_HOVER_BG_COLOR: Color = (235, 235, 235, 255)
# Dropdown background when hovering an option; RGB tuple (0-255 per channel).
THEME_DROPDOWN_HOVER_OPTION_COLOR: Color = (230, 230, 230, 255)
# Disabled state
# Dropdown disabled text color; RGB tuple (0-255 per channel).
THEME_DROPDOWN_DISABLED_TEXT_COLOR: Color = (150, 150, 150)

# Input field colors
# Default state
# Input text color; RGB tuple (0-255 per channel).
THEME_INPUT_TEXT_COLOR: Color = (0, 0, 0)
# Input background color; RGB tuple (0-255 per channel).
THEME_INPUT_BG_COLOR: Color = (255, 255, 255, 255)
# Input border color; RGB tuple (0-255 per channel).
THEME_INPUT_BORDER_COLOR: Color = (0, 0, 0, 255)
# Disabled state
# Input background when disabled; RGB tuple (0-255 per channel).
THEME_INPUT_DISABLED_BG_COLOR: Color = (200, 200, 200, 255)
# Input border when disabled; RGB tuple (0-255 per channel).
THEME_INPUT_DISABLED_BORDER_COLOR: Color = (100, 100, 100, 255)
# Input text when disabled; RGB tuple (0-255 per channel).
THEME_INPUT_DISABLED_TEXT_COLOR: Color = (150, 150, 150)
# Placeholder
# Placeholder text color for empty inputs; RGB tuple (0-255 per channel).
THEME_INPUT_PLACEHOLDER_COLOR: Color = (150, 150, 150)

# Slider colors
# Default state
# Slider track background; RGB tuple (0-255 per channel).
THEME_SLIDER_BG_COLOR: Color = (200, 200, 200, 255)
# Slider filled track color; RGB tuple (0-255 per channel).
THEME_SLIDER_FG_COLOR: Color = (100, 100, 255, 255)
# Slider handle fill color; RGB tuple (0-255 per channel).
THEME_SLIDER_HANDLE_COLOR: Color = (255, 255, 255, 255)
# Slider border color; RGB tuple (0-255 per channel).
THEME_SLIDER_BORDER_COLOR: Color = (0, 0, 0, 255)
# Hover state
# Slider handle hover fill; RGB tuple (0-255 per channel).
THEME_SLIDER_HANDLE_HOVER_COLOR: Color = (235, 235, 255, 255)
# Active/drag state
# Slider handle active fill; RGB tuple (0-255 per channel).
THEME_SLIDER_HANDLE_ACTIVE_COLOR: Color = (180, 180, 255, 255)
# Hover state
# Slider track hover fill; RGB tuple (0-255 per channel).
THEME_SLIDER_TRACK_HOVER_COLOR: Color = (120, 120, 255, 255)
# Active/drag state
# Slider track active fill; RGB tuple (0-255 per channel).
THEME_SLIDER_TRACK_ACTIVE_COLOR: Color = (80, 80, 230, 255)
# Hover state
# Slider border color when hovering handle; RGB tuple (0-255 per channel).
THEME_SLIDER_HOVER_BORDER_COLOR: Color = (50, 50, 50, 255)
# Disabled state
# Slider background when disabled; RGB tuple (0-255 per channel).
THEME_SLIDER_DISABLED_BG_COLOR: Color = (100, 100, 100, 255)
# Slider filled track when disabled; RGB tuple (0-255 per channel).
THEME_SLIDER_DISABLED_FG_COLOR: Color = (60, 60, 60, 255)
# Slider handle when disabled; RGB tuple (0-255 per channel).
THEME_SLIDER_DISABLED_HANDLE_COLOR: Color = (150, 150, 150, 255)
# Slider border when disabled; RGB tuple (0-255 per channel).
THEME_SLIDER_DISABLED_BORDER_COLOR: Color = (80, 80, 80, 255)

# Progress bar colors
# Default state
# Progress bar background; RGB tuple (0-255 per channel).
THEME_PROGRESS_BAR_BG_COLOR: Color = (80, 80, 80, 255)
# Progress bar fill; RGB tuple (0-255 per channel).
THEME_PROGRESS_BAR_PROGRESS_COLOR: Color = (100, 255, 100, 255)
# Progress bar border; RGB tuple (0-255 per channel).
THEME_PROGRESS_BAR_BORDER_COLOR: Color = (150, 150, 150, 255)
# Progress bar text color; RGB tuple (0-255 per channel).
THEME_PROGRESS_BAR_TEXT_COLOR: Color = (255, 255, 255)

# Toast colors
# Default state
# Toast "info" text color; RGB tuple (0-255 per channel).
THEME_TOAST_INFO_TEXT_COLOR: Color = (30, 30, 30)
# Toast "info" background color; RGB tuple (0-255 per channel).
THEME_TOAST_INFO_BG_COLOR: Color = (255, 255, 255, 255)
# Success state
# Toast "success" text color; RGB tuple (0-255 per channel).
THEME_TOAST_SUCCESS_TEXT_COLOR: Color = (255, 255, 255)
# Toast "success" background color; RGB tuple (0-255 per channel).
THEME_TOAST_SUCCESS_BG_COLOR: Color = (0, 128, 0, 255)
# Error state
# Toast "error" text color; RGB tuple (0-255 per channel).
THEME_TOAST_ERROR_TEXT_COLOR: Color = (255, 255, 255)
# Toast "error" background color; RGB tuple (0-255 per channel).
THEME_TOAST_ERROR_BG_COLOR: Color = (128, 0, 0, 255)
# Warning state
# Toast "warning" text color; RGB tuple (0-255 per channel).
THEME_TOAST_WARNING_TEXT_COLOR: Color = (0, 0, 0)
# Toast "warning" background color; RGB tuple (0-255 per channel).
THEME_TOAST_WARNING_BG_COLOR: Color = (255, 215, 0, 255)

# Game log colors
# Game log info text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_INFO_COLOR: Color = (240, 240, 240)
# Game log debug text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_DEBUG_COLOR: Color = (150, 200, 255)
# Game log scoring text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_SCORING_COLOR: Color = (255, 255, 0)
# Game log warning text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_WARNING_COLOR: Color = (255, 220, 100)
# Game log error text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_ERROR_COLOR: Color = (255, 120, 120)
# Game log info row background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_INFO_BG: ColorA = (0, 0, 0, 0)
# Game log debug row background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_DEBUG_BG: ColorA = (0, 50, 100, 30)
# Game log scoring row background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_SCORING_BG: ColorA = (80, 80, 0, 40)
# Game log warning row background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_WARNING_BG: ColorA = (100, 80, 0, 40)
# Game log error row background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_ERROR_BG: ColorA = (100, 0, 0, 50)
# Game log overlay dim color; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_OVERLAY_COLOR: ColorA = (0, 0, 0, 200)
# Game log title text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_TITLE_TEXT_COLOR: Color = (255, 255, 255)
# Game log title background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_TITLE_BG_COLOR: ColorA = (50, 50, 50, 180)
# Game log scroll info text color; RGB tuple (0-255 per channel).
THEME_GAME_LOG_SCROLL_TEXT_COLOR: Color = (180, 180, 180)
# Game log scroll info background; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_LOG_SCROLL_BG_COLOR: ColorA = (0, 0, 0, 150)

# Shared scene colors
# Scene header background color; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_SCENE_HEADER_BG_COLOR: ColorA = (42, 42, 42, 100)
# Optional blur radius/strength for the scene header background; 0 disables blur.
THEME_SCENE_HEADER_BLUR_RADIUS: float = 5.0
# Optional blur radius/strength for UI alpha primitives; 0 disables blur.
THEME_UI_ALPHA_BLUR_RADIUS: float = 5.0
# Scene header text color; RGB tuple (0-255 per channel).
THEME_SCENE_HEADER_TEXT_COLOR: Color = (212, 175, 55)
# Primary light text for titles and labels; RGB tuple (0-255 per channel).
THEME_TEXT_COLOR_LIGHT: Color = (242, 242, 242)
# Section header highlight color (gold); RGB tuple (0-255 per channel).
THEME_SECTION_HEADER_COLOR: Color = (212, 175, 55)
# Section divider color for help sections; RGBA tuple (0-255 per channel, alpha).
THEME_SECTION_DIVIDER_COLOR: ColorA = (255, 255, 255, 40)
# Subsection highlight color (light blue); RGB tuple (0-255 per channel).
THEME_SUBSECTION_COLOR: Color = (143, 170, 214)
# Disabled label text color in settings; RGB tuple (0-255 per channel).
THEME_LABEL_DISABLED_COLOR: Color = (138, 138, 138)

# Scene-specific backgrounds (image filenames are relative to settings.BACKGROUND_IMAGE_PATH).
THEME_MAIN_MENU_BACKGROUND_COLOR: Color = (30, 30, 30, 255)
THEME_MAIN_MENU_BACKGROUND_IMAGE: str | None = "main_menu.png"
THEME_MAIN_MENU_BACKGROUND_SCALE_MODE: str = "fill"
THEME_MAIN_MENU_BACKGROUND_TINT_COLOR: ColorA | None = (0, 0, 0, 160)
THEME_MAIN_MENU_BACKGROUND_BLUR_RADIUS: float = 0.0

THEME_SETTINGS_BACKGROUND_COLOR: Color = (30, 30, 30, 255)
THEME_SETTINGS_BACKGROUND_IMAGE: str | None = "settings.png"
THEME_SETTINGS_BACKGROUND_SCALE_MODE: str = "fill"
THEME_SETTINGS_BACKGROUND_TINT_COLOR: ColorA | None = (0, 0, 0, 160)
THEME_SETTINGS_BACKGROUND_BLUR_RADIUS: float = 0.0

THEME_HELP_BACKGROUND_COLOR: Color = (30, 30, 30, 255)
THEME_HELP_BACKGROUND_IMAGE: str | None = "how_to_play.png"
THEME_HELP_BACKGROUND_SCALE_MODE: str = "fill"
THEME_HELP_BACKGROUND_TINT_COLOR: ColorA | None = (0, 0, 0, 160)
THEME_HELP_BACKGROUND_BLUR_RADIUS: float = 0.0

THEME_LOBBY_BACKGROUND_COLOR: Color = (30, 30, 30, 255)
THEME_LOBBY_BACKGROUND_IMAGE: str | None = "lobby.png"
THEME_LOBBY_BACKGROUND_SCALE_MODE: str = "fill"
THEME_LOBBY_BACKGROUND_TINT_COLOR: ColorA | None = (0, 0, 0, 160)
THEME_LOBBY_BACKGROUND_BLUR_RADIUS: float = 0.0

THEME_PREPARE_BACKGROUND_COLOR: Color = (30, 30, 30, 255)
THEME_PREPARE_BACKGROUND_IMAGE: str | None = "game_prepare.png"
THEME_PREPARE_BACKGROUND_SCALE_MODE: str = "fill"
THEME_PREPARE_BACKGROUND_TINT_COLOR: ColorA | None = (0, 0, 0, 160)
THEME_PREPARE_BACKGROUND_BLUR_RADIUS: float = 0.0

# Main menu dialog colors
# Main menu confirmation overlay fill; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_MENU_OVERLAY_COLOR: ColorA = (0, 0, 0, 128)
# Main menu dialog background; RGB tuple (0-255 per channel).
THEME_MENU_DIALOG_BG_COLOR: Color = (60, 60, 60, 255)
# Main menu dialog border; RGB tuple (0-255 per channel).
THEME_MENU_DIALOG_BORDER_COLOR: Color = (200, 200, 200, 255)
# Main menu dialog text color; RGB tuple (0-255 per channel).
THEME_MENU_DIALOG_TEXT_COLOR: Color = (255, 255, 255)

# Lobby status colors
# Lobby status color for AI players; RGB tuple (0-255 per channel).
THEME_LOBBY_STATUS_AI_COLOR: Color = (120, 120, 120)
# Lobby status color for connected players; RGB tuple (0-255 per channel).
THEME_LOBBY_STATUS_CONNECTED_COLOR: Color = (0, 200, 0)
# Lobby status color for waiting players; RGB tuple (0-255 per channel).
THEME_LOBBY_STATUS_WAITING_COLOR: Color = (200, 200, 0)

# Game scene colors
# Game board background; RGB tuple (0-255 per channel).
THEME_GAME_BOARD_BG_COLOR: Color = (25, 25, 25, 255)
# Valid placement highlight overlay; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_VALID_PLACEMENT_COLOR: ColorA = (255, 255, 0, 100)
# Selected/hover outline color; RGB tuple (0-255 per channel).
THEME_GAME_HIGHLIGHT_COLOR: Color = (255, 255, 0, 255)
# Hovered structure highlight overlay; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_GAME_STRUCTURE_HOVER_COLOR: ColorA = (255, 255, 0, 150)
# Transparent fill for structure overlays; RGBA tuple (0-255 per channel, alpha 0-255).
THEME_TRANSPARENT_COLOR: ColorA = (0, 0, 0, 0)
# Game over table background; RGB tuple (0-255 per channel).
THEME_GAME_OVER_TABLE_BG_COLOR: Color = (40, 40, 40, 255)
# Game over table separator line; RGB tuple (0-255 per channel).
THEME_GAME_OVER_TABLE_LINE_COLOR: Color = (100, 100, 100, 255)
# Game over row separator line; RGB tuple (0-255 per channel).
THEME_GAME_OVER_ROW_LINE_COLOR: Color = (70, 70, 70, 255)
# Game over player row text color; RGB tuple (0-255 per channel).
THEME_GAME_OVER_ROW_TEXT_COLOR: Color = (220, 220, 220)
# Game over hint text color; RGB tuple (0-255 per channel).
THEME_GAME_OVER_HINT_TEXT_COLOR: Color = (180, 180, 180)
# Debug grid line color on the board; RGB tuple (0-255 per channel).
THEME_GAME_DEBUG_GRID_COLOR: Color = (0, 0, 0, 255)
# Sidebar panel background; RGB tuple (0-255 per channel).
THEME_GAME_SIDEBAR_BG_COLOR: Color = (50, 50, 50, 255)
# Sidebar status color for local mode; RGB tuple (0-255 per channel).
THEME_GAME_STATUS_LOCAL_COLOR: Color = (100, 100, 255)
# Sidebar status color for active turn; RGB tuple (0-255 per channel).
THEME_GAME_STATUS_TURN_COLOR: Color = (0, 255, 0)
# Sidebar status color for waiting turn; RGB tuple (0-255 per channel).
THEME_GAME_STATUS_WAIT_COLOR: Color = (200, 0, 0)
# Sidebar highlight background for current player; RGB tuple (0-255 per channel).
THEME_GAME_CURRENT_PLAYER_BG_COLOR: Color = (60, 80, 120, 255)
# Sidebar highlight border for current player; RGB tuple (0-255 per channel).
THEME_GAME_CURRENT_PLAYER_BORDER_COLOR: Color = (100, 150, 255, 255)
# Sidebar score text color; RGB tuple (0-255 per channel).
THEME_GAME_SCORE_TEXT_COLOR: Color = (200, 200, 200)
# AI thinking text color; RGB tuple (0-255 per channel).
THEME_GAME_AI_THINKING_COLOR: Color = (255, 255, 100)

# Game scene background (image filename is relative to settings.BACKGROUND_IMAGE_PATH).
THEME_GAME_BACKGROUND_COLOR: Color = (25, 25, 25, 255)
THEME_GAME_BACKGROUND_IMAGE: str | None = None
THEME_GAME_BACKGROUND_SCALE_MODE: str = "fill"
THEME_GAME_BACKGROUND_TINT_COLOR: ColorA | None = None
THEME_GAME_BACKGROUND_BLUR_RADIUS: float = 0.0

# Player color palette
# Player "red" tint; RGB tuple (0-255 per channel).
THEME_PLAYER_COLOR_RED: Color = (255, 100, 100)
# Player "blue" tint; RGB tuple (0-255 per channel).
THEME_PLAYER_COLOR_BLUE: Color = (100, 100, 255)
# Player "green" tint; RGB tuple (0-255 per channel).
THEME_PLAYER_COLOR_GREEN: Color = (100, 255, 100)
# Player "yellow" tint; RGB tuple (0-255 per channel).
THEME_PLAYER_COLOR_YELLOW: Color = (255, 255, 100)
# Player "pink" tint; RGB tuple (0-255 per channel).
THEME_PLAYER_COLOR_PINK: Color = (255, 100, 255)
# Player "black" tint (light gray fallback); RGB tuple (0-255 per channel).
THEME_PLAYER_COLOR_BLACK: Color = (200, 200, 200)

# Cache for pygame font instances keyed by role, size, and font family.
_FONT_CACHE: dict[tuple[str, int, str | None], pygame.font.Font] = {}
_SYSTEM_FONT_MATCH_CACHE: dict[str, str | None] = {}


def resolve_font_path(font_name: str | None) -> str | None:
    """Resolve a font name to an assets/fonts path if it exists."""
    if not font_name:
        return None
    font_name = font_name.strip()
    if not font_name:
        return None
    if os.path.isabs(font_name) and os.path.isfile(font_name):
        return font_name
    asset_font_path = os.path.join(settings.ASSETS_PATH, "fonts", font_name)
    if os.path.isfile(asset_font_path):
        return asset_font_path
    return None


def _get_font_family(role: str) -> str | None:
    if role == "title":
        return THEME_FONT_FAMILY_TITLE
    if role == "section_header":
        return THEME_FONT_FAMILY_SECTION_HEADER
    if role == "label":
        return THEME_FONT_FAMILY_LABEL
    if role == "button":
        return THEME_FONT_FAMILY_BUTTON
    return THEME_FONT_FAMILY_BODY


def _load_font(font_name: str | None, size: int) -> pygame.font.Font:
    font_path = resolve_font_path(font_name)
    if font_path:
        return pygame.font.Font(font_path, size)
    if font_name:
        _, extension = os.path.splitext(font_name.lower())
        if extension in {".ttf", ".otf", ".ttc", ".otc"}:
            return pygame.font.Font(None, size)
        if font_name in _SYSTEM_FONT_MATCH_CACHE:
            matched = _SYSTEM_FONT_MATCH_CACHE[font_name]
        else:
            matched = pygame.font.match_font(font_name)
            _SYSTEM_FONT_MATCH_CACHE[font_name] = matched
        if matched:
            return pygame.font.Font(matched, size)
        return pygame.font.SysFont(font_name, size)
    return pygame.font.Font(None, size)


def get_font(role: str, size: int) -> pygame.font.Font:
    """Return a cached pygame font for the given role and size."""
    font_family = _get_font_family(role)
    cache_key = (role, size, font_family)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = _load_font(font_family, size)
    return _FONT_CACHE[cache_key]


def clear_font_cache() -> None:
    """Clear cached pygame fonts so updated sizes take effect."""
    _FONT_CACHE.clear()


def refresh_theme_state() -> None:
    """Refresh derived theme mappings after live updates."""
    global THEME_TOAST_COLORS
    global THEME_PLAYER_COLOR_MAP
    THEME_TOAST_COLORS = {
        "info": (THEME_TOAST_INFO_TEXT_COLOR, THEME_TOAST_INFO_BG_COLOR),
        "success": (THEME_TOAST_SUCCESS_TEXT_COLOR,
                    THEME_TOAST_SUCCESS_BG_COLOR),
        "error": (THEME_TOAST_ERROR_TEXT_COLOR, THEME_TOAST_ERROR_BG_COLOR),
        "warning": (THEME_TOAST_WARNING_TEXT_COLOR,
                    THEME_TOAST_WARNING_BG_COLOR),
    }
    THEME_PLAYER_COLOR_MAP = {
        "red": THEME_PLAYER_COLOR_RED,
        "blue": THEME_PLAYER_COLOR_BLUE,
        "green": THEME_PLAYER_COLOR_GREEN,
        "yellow": THEME_PLAYER_COLOR_YELLOW,
        "pink": THEME_PLAYER_COLOR_PINK,
        "black": THEME_PLAYER_COLOR_BLACK,
    }


# Toast color map for toast types (text color, background color); RGB tuples.
THEME_TOAST_COLORS: dict[str, tuple[Color, Color]] = {
    "info": (THEME_TOAST_INFO_TEXT_COLOR, THEME_TOAST_INFO_BG_COLOR),
    "success": (THEME_TOAST_SUCCESS_TEXT_COLOR, THEME_TOAST_SUCCESS_BG_COLOR),
    "error": (THEME_TOAST_ERROR_TEXT_COLOR, THEME_TOAST_ERROR_BG_COLOR),
    "warning": (THEME_TOAST_WARNING_TEXT_COLOR, THEME_TOAST_WARNING_BG_COLOR),
}

# Player color map used by the sidebar scoreboard; RGB tuples.
THEME_PLAYER_COLOR_MAP: dict[str, Color] = {
    "red": THEME_PLAYER_COLOR_RED,
    "blue": THEME_PLAYER_COLOR_BLUE,
    "green": THEME_PLAYER_COLOR_GREEN,
    "yellow": THEME_PLAYER_COLOR_YELLOW,
    "pink": THEME_PLAYER_COLOR_PINK,
    "black": THEME_PLAYER_COLOR_BLACK,
}

_TOAST_COLOR_UPDATE: dict[str, tuple[str, int]] = {
    "THEME_TOAST_INFO_TEXT_COLOR": ("info", 0),
    "THEME_TOAST_INFO_BG_COLOR": ("info", 1),
    "THEME_TOAST_SUCCESS_TEXT_COLOR": ("success", 0),
    "THEME_TOAST_SUCCESS_BG_COLOR": ("success", 1),
    "THEME_TOAST_ERROR_TEXT_COLOR": ("error", 0),
    "THEME_TOAST_ERROR_BG_COLOR": ("error", 1),
    "THEME_TOAST_WARNING_TEXT_COLOR": ("warning", 0),
    "THEME_TOAST_WARNING_BG_COLOR": ("warning", 1),
}

_PLAYER_COLOR_UPDATE: dict[str, str] = {
    "THEME_PLAYER_COLOR_RED": "red",
    "THEME_PLAYER_COLOR_BLUE": "blue",
    "THEME_PLAYER_COLOR_GREEN": "green",
    "THEME_PLAYER_COLOR_YELLOW": "yellow",
    "THEME_PLAYER_COLOR_PINK": "pink",
    "THEME_PLAYER_COLOR_BLACK": "black",
}


def apply_theme_update(name: str, value: typing.Any) -> bool:
    """Update a single theme property and refresh derived caches as needed."""
    current_value = globals().get(name, None)
    if current_value == value:
        return False
    globals()[name] = value
    if name in _TOAST_COLOR_UPDATE:
        toast_type, index = _TOAST_COLOR_UPDATE[name]
        text_color, bg_color = THEME_TOAST_COLORS[toast_type]
        if index == 0:
            text_color = value
        else:
            bg_color = value
        THEME_TOAST_COLORS[toast_type] = (text_color, bg_color)
    if name in _PLAYER_COLOR_UPDATE:
        player_key = _PLAYER_COLOR_UPDATE[name]
        THEME_PLAYER_COLOR_MAP[player_key] = value
    if name.startswith("THEME_FONT_FAMILY_") or name.startswith(
        "THEME_FONT_SIZE_"
    ):
        clear_font_cache()
    return True
