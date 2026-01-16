import pygame
import time
from typing import List, Tuple
import typing
from utils.settings_manager import settings_manager

from ui import theme


class GameLogEntry:
    """Represents a single entry in the game log."""

    def __init__(self,
                 message: str,
                 level: str = "INFO",
                 timestamp: float = None) -> None:
        """
        Initialize a game log entry.
        
        Args:
            message: Log message
            level: Log level (INFO, DEBUG, SCORING, WARNING, ERROR)
            timestamp: Timestamp for the entry
        """
        self.message = message
        self.level = level
        self.timestamp = timestamp or time.time()

    def get_formatted_time(self) -> str:
        """Get the formatted timestamp for the log entry."""
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))


class GameLog:
    """Handles the display and management of the game log UI overlay."""

    def __init__(self) -> None:
        """Initialize the game log."""
        self.max_entries = settings_manager.get("GAME_LOG_MAX_ENTRIES", 2000)
        self.entries: List[GameLogEntry] = []
        self.visible = False
        self.scroll_offset = 0
        self.font = theme.get_font(theme.THEME_FONT_SIZE_GAME_LOG_BODY)
        self.title_font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
        self.level_colors = {
            "INFO": theme.THEME_GAME_LOG_INFO_COLOR,
            "DEBUG": theme.THEME_GAME_LOG_DEBUG_COLOR,
            "SCORING": theme.THEME_GAME_LOG_SCORING_COLOR,
            "WARNING": theme.THEME_GAME_LOG_WARNING_COLOR,
            "ERROR": theme.THEME_GAME_LOG_ERROR_COLOR,
        }
        self.level_backgrounds = {
            "INFO": theme.THEME_GAME_LOG_INFO_BG,
            "DEBUG": theme.THEME_GAME_LOG_DEBUG_BG,
            "SCORING": theme.THEME_GAME_LOG_SCORING_BG,
            "WARNING": theme.THEME_GAME_LOG_WARNING_BG,
            "ERROR": theme.THEME_GAME_LOG_ERROR_BG,
        }

    def add_entry(self, message: str, level: str = "INFO") -> None:
        """
        Add a new log entry.
        
        Args:
            message: Log message
            level: Log level
        """
        entry = GameLogEntry(message, level)
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)
        self.scroll_to_bottom()

    def toggle_visibility(self) -> None:
        """Toggle the visibility of the game log."""
        self.visible = not self.visible

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the log."""
        self.scroll_offset = 0

    def handle_scroll(self, scroll_delta: int) -> None:
        """
        Handle scrolling through log entries.
        
        Args:
            scroll_delta: Scroll amount
        """
        if not self.visible:
            return
        debug_enabled = settings_manager.get("DEBUG", False)
        filtered_count = 0
        for entry in self.entries:
            if entry.level == "DEBUG" and not debug_enabled:
                continue
            filtered_count += 1
        self.scroll_offset += scroll_delta * 5
        usable_height = settings_manager.get("WINDOW_HEIGHT", 1080) - 100
        line_height = 32
        max_visible_lines = usable_height // line_height
        max_scroll = max(0, filtered_count - max_visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def get_visible_lines(self) -> int:
        """Get the number of visible lines in the log."""
        screen_height = settings_manager.get("WINDOW_HEIGHT", 1080)
        usable_height = screen_height - 100
        line_height = 32
        return usable_height // line_height

    def update_max_entries(self) -> None:
        """Update the maximum number of log entries from settings."""
        new_max_entries = settings_manager.get("GAME_LOG_MAX_ENTRIES", 2000)
        if new_max_entries != self.max_entries:
            self.max_entries = new_max_entries
            if len(self.entries) > self.max_entries:
                remove_count = len(self.entries) - self.max_entries
                self.entries = self.entries[remove_count:]
                self.scroll_to_bottom()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the game log overlay.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return
        screen_width = settings_manager.get("WINDOW_WIDTH", 1920)
        screen_height = settings_manager.get("WINDOW_HEIGHT", 1080)
        overlay = pygame.Surface((screen_width, screen_height),
                                 pygame.SRCALPHA)
        overlay.fill(theme.THEME_GAME_LOG_OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))
        title_text = self.title_font.render(
            "Game Log (Press TAB to close, Mouse Wheel to scroll)", True,
            theme.THEME_GAME_LOG_TITLE_TEXT_COLOR)
        title_rect = title_text.get_rect(center=(screen_width // 2, 30))
        title_bg = pygame.Surface(
            (title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
        title_bg.fill(theme.THEME_GAME_LOG_TITLE_BG_COLOR)
        screen.blit(title_bg, (title_rect.x - 10, title_rect.y - 5))
        screen.blit(title_text, title_rect)
        debug_enabled = settings_manager.get("DEBUG", False)
        filtered_entries = []
        for entry in self.entries:
            if entry.level == "DEBUG" and not debug_enabled:
                continue
            filtered_entries.append(entry)
        usable_height = screen_height - 100
        line_height = 32
        max_visible_lines = usable_height // line_height
        total_filtered_entries = len(filtered_entries)
        if total_filtered_entries == 0:
            return
        start_index = max(
            0, total_filtered_entries - max_visible_lines - self.scroll_offset)
        end_index = min(total_filtered_entries,
                        total_filtered_entries - self.scroll_offset)
        max_scroll = max(0, total_filtered_entries - max_visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        start_index = max(
            0, total_filtered_entries - max_visible_lines - self.scroll_offset)
        end_index = min(total_filtered_entries,
                        total_filtered_entries - self.scroll_offset)
        y_pos = 70
        entries_drawn = 0
        for i in range(start_index, end_index):
            if i < 0 or i >= len(filtered_entries):
                continue
            entry = filtered_entries[i]
            if y_pos + line_height > screen_height - 20:
                break
            time_str = entry.get_formatted_time()
            level_str = f"[{entry.level}]"
            full_message = f"{time_str} {level_str} {entry.message}"
            text_color = self.level_colors.get(entry.level,
                                               theme.THEME_TEXT_COLOR_LIGHT)
            bg_color = self.level_backgrounds.get(entry.level,
                                                  theme.THEME_TRANSPARENT_COLOR)
            if bg_color[3] > 0:
                line_bg = pygame.Surface((screen_width - 20, line_height),
                                         pygame.SRCALPHA)
                line_bg.fill(bg_color)
                screen.blit(line_bg, (10, y_pos - 2))
            max_width = screen_width - 40
            test_surface = self.font.render(full_message, True, text_color)
            if test_surface.get_width() > max_width:
                words = entry.message.split(' ')
                lines = []
                current_line = f"{time_str} {level_str}"
                for word in words:
                    test_line = f"{current_line} {word}"
                    if self.font.size(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line.strip():
                            lines.append(current_line)
                        current_line = f"           {word}"
                if current_line.strip():
                    lines.append(current_line)
                for line in lines:
                    if y_pos + line_height > screen_height - 20:
                        break
                    wrapped_surface = self.font.render(line, True, text_color)
                    screen.blit(wrapped_surface, (20, y_pos))
                    y_pos += line_height
                    entries_drawn += 1
            else:
                screen.blit(test_surface, (20, y_pos))
                y_pos += line_height
                entries_drawn += 1
        if total_filtered_entries > max_visible_lines:
            visible_start = max(
                1, total_filtered_entries - self.scroll_offset -
                entries_drawn + 1)
            visible_end = total_filtered_entries - self.scroll_offset
            scroll_info = f"Lines {visible_start}-{visible_end} of {total_filtered_entries}"
            scroll_surface = self.font.render(
                scroll_info, True, theme.THEME_GAME_LOG_SCROLL_TEXT_COLOR)
            scroll_bg = pygame.Surface((scroll_surface.get_width() + 10,
                                        scroll_surface.get_height() + 6),
                                       pygame.SRCALPHA)
            scroll_bg.fill(theme.THEME_GAME_LOG_SCROLL_BG_COLOR)
            scroll_rect = (screen_width - scroll_surface.get_width() - 25,
                           screen_height - 35)
            screen.blit(scroll_bg, (scroll_rect[0] - 5, scroll_rect[1] - 3))
            screen.blit(scroll_surface, scroll_rect)

    def refresh_theme(self) -> None:
        """Refresh fonts and colors from the current theme."""
        self.font = theme.get_font(theme.THEME_FONT_SIZE_GAME_LOG_BODY)
        self.title_font = theme.get_font(theme.THEME_FONT_SIZE_BODY)
        self.level_colors = {
            "INFO": theme.THEME_GAME_LOG_INFO_COLOR,
            "DEBUG": theme.THEME_GAME_LOG_DEBUG_COLOR,
            "SCORING": theme.THEME_GAME_LOG_SCORING_COLOR,
            "WARNING": theme.THEME_GAME_LOG_WARNING_COLOR,
            "ERROR": theme.THEME_GAME_LOG_ERROR_COLOR,
        }
        self.level_backgrounds = {
            "INFO": theme.THEME_GAME_LOG_INFO_BG,
            "DEBUG": theme.THEME_GAME_LOG_DEBUG_BG,
            "SCORING": theme.THEME_GAME_LOG_SCORING_BG,
            "WARNING": theme.THEME_GAME_LOG_WARNING_BG,
            "ERROR": theme.THEME_GAME_LOG_ERROR_BG,
        }
