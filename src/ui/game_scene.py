import pygame
import logging
import typing
import settings

from ui.scene import Scene
from game_state import GameState
from utils.settings_manager import settings_manager
from ui.components.toast import Toast, ToastManager
from ui.components.button import Button
from ui.components.progress_bar import ProgressBar
from ui.utils.draw import draw_rect_alpha, draw_line_alpha
from ui import theme

logger = logging.getLogger(__name__)


class GameScene(Scene):

    def __init__(self, screen: pygame.Surface,
                 switch_scene_callback: typing.Callable,
                 game_session: typing.Any, clock: typing.Any,
                 network: typing.Any, game_log: typing.Any) -> None:
        super().__init__(screen, switch_scene_callback)
        self.session = game_session
        self.clock = clock
        self.network = network
        self.game_log = game_log

        self.scroll_speed = 10
        self.font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.game_over_title_font = theme.get_font(
            "title", theme.THEME_FONT_SIZE_GAME_OVER_TITLE
        )
        self.game_over_table_font = theme.get_font(
            "label", theme.THEME_FONT_SIZE_BUTTON
        )
        self.game_over_row_font = theme.get_font(
            "body", theme.THEME_FONT_SIZE_GAME_OVER_ROW
        )
        self.game_over_hint_font = theme.get_font(
            "body", theme.THEME_FONT_SIZE_BODY
        )
        self._compass_surface: pygame.Surface | None = None
        self._compass_tile_size: int | None = None

        self.toast_manager = ToastManager(max_toasts=5)

        self.sidebar_scroll_offset = 0
        self.sidebar_scroll_speed = 30

        tile_size = settings_manager.get("TILE_SIZE")
        grid_size = settings_manager.get("GRID_SIZE")
        window_width = settings_manager.get("WINDOW_WIDTH")
        window_height = settings_manager.get("WINDOW_HEIGHT")
        sidebar_width = settings_manager.get("SIDEBAR_WIDTH")

        game_area_width = window_width - sidebar_width

        board_center_x = (grid_size * tile_size) // 2
        board_center_y = (grid_size * tile_size) // 2

        self.offset_x = board_center_x - game_area_width // 2
        self.offset_y = board_center_y - window_height // 2

        self.keys_pressed = {
            pygame.K_w: False,
            pygame.K_s: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False
        }

        self.valid_placements = set()
        self.last_card_state = (None, None)

        self.last_ai_turn_time = 0
        self.player_action_time = 0
        self.ai_turn_start_time = None

        self._render_cache = {}
        self._render_cache_valid = False
        self._last_render_state = None
        self._text_surface_cache: dict[
            tuple[int, str, tuple[int, int, int]], pygame.Surface
        ] = {}

        bar_width = sidebar_width - 40
        bar_height = 20
        bar_x = window_width - sidebar_width + 20
        bar_y = 0
        self.ai_thinking_progress_bar = ProgressBar(
            rect=(bar_x, bar_y, bar_width, bar_height),
            font=self.font,
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            background_color=theme.THEME_PROGRESS_BAR_BG_COLOR,
            progress_color=theme.THEME_PROGRESS_BAR_PROGRESS_COLOR,
            border_color=theme.THEME_PROGRESS_BAR_BORDER_COLOR,
            show_text=True,
            text_color=theme.THEME_PROGRESS_BAR_TEXT_COLOR)

    def _get_render_state_hash(self) -> int:
        """Get a hash of the current render state for caching."""
        if not self.session:
            return 0

        board_state = len([
            (x, y)
            for y in range(self.session.get_game_board().get_grid_size())
            for x in range(self.session.get_game_board().get_grid_size())
            if self.session.get_game_board().get_card(x, y)
        ])
        current_card = self.session.get_current_card()
        card_state = id(current_card) if current_card else 0
        valid_placements = len(self.valid_placements)
        offset_x = self.offset_x
        offset_y = self.offset_y
        return hash(
            (board_state, card_state, valid_placements, offset_x, offset_y))

    def _get_render_cache_key(self, render_type: str) -> tuple:
        """Get a cache key for rendering."""
        return (render_type, self._get_render_state_hash(), self.offset_x,
                self.offset_y)

    def _invalidate_render_cache(self) -> None:
        """Invalidate the rendering cache."""
        self._render_cache.clear()
        self._render_cache_valid = False
        self._last_render_state = None

    def invalidate_render_cache(self) -> None:
        """Public method to invalidate the rendering cache."""
        self._invalidate_render_cache()

    def _render_cached(self, render_type: str, render_func) -> pygame.Surface:
        """Render with caching support."""
        cache_key = self._get_render_cache_key(render_type)
        if cache_key in self._render_cache:
            return self._render_cache[cache_key]

        result = render_func()
        self._render_cache[cache_key] = result
        return result

    def _get_cached_text(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, ...],
    ) -> pygame.Surface:
        cache_key = (id(font), text, color)
        cached = self._text_surface_cache.get(cache_key)
        if cached is None:
            cached = font.render(text, True, color)
            self._text_surface_cache[cache_key] = cached
        return cached

    def _get_compass_surface(self, tile_size: int) -> pygame.Surface | None:
        if (self._compass_surface is not None
                and self._compass_tile_size == tile_size):
            return self._compass_surface
        try:
            compass_image = pygame.image.load(
                settings.ICONS_PATH + "compass.png"
            ).convert_alpha()
        except Exception as exc:
            logger.error(f"Failed to load compass icon: {exc}")
            self._compass_surface = None
            self._compass_tile_size = tile_size
            return None
        compass_size = max(1, tile_size // 4)
        self._compass_surface = pygame.transform.smoothscale(
            compass_image, (compass_size, compass_size)
        )
        self._compass_tile_size = tile_size
        return self._compass_surface

    def _apply_sidebar_scroll(self, events: list[pygame.event.Event]) -> None:
        """Handle sidebar scrolling events"""
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                window_width = settings_manager.get("WINDOW_WIDTH")
                sidebar_width = settings_manager.get("SIDEBAR_WIDTH")
                panel_x = window_width - sidebar_width

                if mouse_x >= panel_x:
                    self.sidebar_scroll_offset -= event.y * self.sidebar_scroll_speed
                    self.sidebar_scroll_offset = max(
                        0, self.sidebar_scroll_offset)

    def get_offset_x(self) -> int:
        """
        Renderer x-axis offset getter method
        :return: Offset on the x-axis
        """
        return self.offset_x

    def get_offset_y(self) -> int:
        """
        Renderer y-axis offset getter method
        :return: Offset on the y-axis
        """
        return self.offset_y

    def _update_valid_placements(self):
        """Update the set of valid placements for the current card and board state."""
        current_card = self.session.get_current_card()
        if not current_card:
            self.valid_placements = set()
            self.last_card_state = (None, None)
            return

        card_id = id(current_card)
        rotation = getattr(current_card, 'rotation', 0)
        current_state = (card_id, rotation)

        if current_state == self.last_card_state:
            return

        self.last_card_state = current_state

        valid_placements = self.session.get_valid_placements(current_card)
        self.valid_placements = {(x, y)
                                 for x, y, card_rotation in valid_placements
                                 if card_rotation == rotation}

        self._invalidate_render_cache()

    def draw_board(self, game_board: typing.Any, placed_figures: list,
                   detected_structures: list, is_first_round: bool,
                   is_game_over: bool, players: list) -> None:
        """
        Draws the game board, including grid lines and placed cards.
        """
        self._update_valid_placements()

        def render_board():
            surface = pygame.Surface(
                (settings_manager.get("WINDOW_WIDTH"),
                 settings_manager.get("WINDOW_HEIGHT")))
            self._draw_background(
                background_color=theme.THEME_GAME_BACKGROUND_COLOR,
                image_name=theme.THEME_GAME_BACKGROUND_IMAGE,
                scale_mode=theme.THEME_GAME_BACKGROUND_SCALE_MODE,
                tint_color=theme.THEME_GAME_BACKGROUND_TINT_COLOR,
                blur_radius=theme.THEME_GAME_BACKGROUND_BLUR_RADIUS,
                surface=surface,
            )

            if settings_manager.get("SHOW_VALID_PLACEMENTS", True):
                tile_size = settings_manager.get("TILE_SIZE")
                highlight_color = theme.THEME_GAME_VALID_PLACEMENT_COLOR
                for (x, y) in self.valid_placements:
                    rect = pygame.Surface((tile_size, tile_size),
                                          pygame.SRCALPHA)
                    rect.fill(highlight_color)
                    surface.blit(rect, (x * tile_size - self.offset_x,
                                        y * tile_size - self.offset_y))

            return surface

        board_surface = self._render_cached("board_background", render_board)
        self.screen.blit(board_surface, (0, 0))

        if is_game_over:
            winner = max(players, key=lambda p: p.get_score())
            message = f"{winner.get_name()} wins with {winner.get_score()} points!"
            window_width = settings_manager.get("WINDOW_WIDTH")
            window_height = settings_manager.get("WINDOW_HEIGHT")
            winner_y = window_height // 3 - 40
            text_surface = self._get_cached_text(
                self.game_over_title_font,
                message,
                theme.THEME_TEXT_COLOR_LIGHT,
            )
            text_rect = text_surface.get_rect(center=(window_width // 2,
                                                      winner_y))
            self.screen.blit(text_surface, text_rect)

            sorted_players = sorted(players,
                                    key=lambda p:
                                    (-p.get_score(), p.get_name()))
            num_rows = len(sorted_players) + 1  # header + players
            row_height = 55
            table_width = 600
            table_height = num_rows * row_height + 20
            table_x = window_width // 2 - table_width // 2
            table_y = text_rect.bottom + 30
            col1_x = window_width // 2 - 150
            col2_x = window_width // 2 + 150

            draw_rect_alpha(
                self.screen,
                theme.THEME_GAME_OVER_TABLE_BG_COLOR,
                (table_x, table_y, table_width, table_height),
            )
            header_y = table_y + row_height // 2
            header_player = self._get_cached_text(
                self.game_over_table_font, "Player", theme.THEME_TEXT_COLOR_LIGHT
            )
            header_score = self._get_cached_text(
                self.game_over_table_font, "Score", theme.THEME_TEXT_COLOR_LIGHT
            )
            self.screen.blit(header_player,
                             header_player.get_rect(center=(col1_x, header_y)))
            self.screen.blit(header_score,
                             header_score.get_rect(center=(col2_x, header_y)))
            draw_line_alpha(
                self.screen,
                theme.THEME_GAME_OVER_TABLE_LINE_COLOR,
                (table_x + 10, table_y + row_height),
                (table_x + table_width - 10, table_y + row_height),
                2,
            )

            for i, player in enumerate(sorted_players):
                row_y = table_y + row_height * (i + 1) + row_height // 2
                name_surface = self._get_cached_text(
                    self.game_over_row_font,
                    player.get_name(),
                    theme.THEME_GAME_OVER_ROW_TEXT_COLOR,
                )
                score_surface = self._get_cached_text(
                    self.game_over_row_font,
                    str(player.get_score()),
                    theme.THEME_GAME_OVER_ROW_TEXT_COLOR,
                )
                self.screen.blit(name_surface,
                                 name_surface.get_rect(center=(col1_x, row_y)))
                self.screen.blit(
                    score_surface,
                    score_surface.get_rect(center=(col2_x, row_y)))
                if i < len(sorted_players) - 1:
                    draw_line_alpha(
                        self.screen,
                        theme.THEME_GAME_OVER_ROW_LINE_COLOR,
                        (table_x + 10, table_y + row_height * (i + 2)),
                        (table_x + table_width - 10,
                         table_y + row_height * (i + 2)),
                        1,
                    )

            esc_message = "Press ESC to return to menu"
            esc_message_surface = self._get_cached_text(
                self.game_over_hint_font, esc_message,
                theme.THEME_GAME_OVER_HINT_TEXT_COLOR)
            esc_message_rect = esc_message_surface.get_rect(
                center=(window_width // 2, table_y + table_height + 50))
            self.screen.blit(esc_message_surface, esc_message_rect)
            return

        if settings_manager.get("DEBUG"):
            tile_size = settings_manager.get("TILE_SIZE")
            for x in range(0, (game_board.get_grid_size() + 1) * tile_size,
                           tile_size):
                draw_line_alpha(
                    self.screen,
                    theme.THEME_GAME_DEBUG_GRID_COLOR,
                    (x - self.offset_x, 0 - self.offset_y),
                    (x - self.offset_x,
                     game_board.get_grid_size() * tile_size - self.offset_y),
                )
            for y in range(0, (game_board.get_grid_size() + 1) * tile_size,
                           tile_size):
                draw_line_alpha(
                    self.screen,
                    theme.THEME_GAME_DEBUG_GRID_COLOR,
                    (0 - self.offset_x, y - self.offset_y),
                    (game_board.get_grid_size() * tile_size - self.offset_x,
                     y - self.offset_y),
                )

        tile_size = settings_manager.get("TILE_SIZE")
        center_x, center_y = game_board.get_center_position()

        for y in range(game_board.grid_size):
            for x in range(game_board.grid_size):
                card = game_board.get_card(x, y)
                if card:
                    image_to_draw = card.get_rotated_image()
                    self.screen.blit(image_to_draw,
                                     (x * tile_size - self.offset_x,
                                      y * tile_size - self.offset_y))

                    last_placed_card = self.session.last_placed_card if hasattr(self.session, 'last_placed_card') else None
                    if last_placed_card is not None and card == last_placed_card:
                        highlight_rect = pygame.Rect(
                            x * tile_size - self.offset_x,
                            y * tile_size - self.offset_y,
                            tile_size, tile_size)
                        pygame.draw.rect(self.screen,
                                         theme.THEME_GAME_HIGHLIGHT_COLOR,
                                         highlight_rect, 5)

                    if x == center_x and y == center_y:
                        compass_surface = self._get_compass_surface(tile_size)
                        if compass_surface is not None:
                            compass_x = x * tile_size - self.offset_x + 5
                            compass_y = y * tile_size - self.offset_y + 5
                            self.screen.blit(
                                compass_surface, (compass_x, compass_y)
                            )

                if settings_manager.get("DEBUG"):
                    text_surface = self._get_cached_text(
                        self.font,
                        f"{x},{y}",
                        theme.THEME_TEXT_COLOR_LIGHT,
                    )
                    text_x = x * tile_size - self.offset_x + tile_size // 3
                    text_y = y * tile_size - self.offset_y + tile_size // 3
                    self.screen.blit(text_surface, (text_x, text_y))

        if settings_manager.get("DEBUG"):
            for structure in detected_structures:
                if structure.get_is_completed():
                    tint_color = structure.get_color()
                    structure_type = structure.get_structure_type()

                    card_edge_map = {}
                    for card, direction in structure.card_sides:
                        if direction is None:
                            continue
                        if card not in card_edge_map:
                            card_edge_map[card] = []
                        card_edge_map[card].append(direction)

                    for card, directions in card_edge_map.items():
                        card_position = [(x, y)
                                         for y in range(game_board.grid_size)
                                         for x in range(game_board.grid_size)
                                         if game_board.get_card(x, y) == card]
                        if card_position:
                            card_x, card_y = card_position[0]
                            rect = pygame.Surface((tile_size, tile_size),
                                                  pygame.SRCALPHA)
                            rect.fill(theme.THEME_TRANSPARENT_COLOR)
                            for direction in directions:
                                terrains_for_card = card.get_terrains(
                                ) if hasattr(card, 'get_terrains') else {}
                                square_size = tile_size // 3
                                # Corners
                                if direction == "NW":
                                    pygame.draw.rect(
                                        rect, tint_color,
                                        (0, 0, square_size, square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (0, 0, square_size, square_size), 2)
                                elif direction == "NE":
                                    pygame.draw.rect(
                                        rect, tint_color,
                                        (2 * square_size, 0, square_size,
                                         square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (2 * square_size, 0, square_size,
                                         square_size), 2)
                                elif direction == "SW":
                                    pygame.draw.rect(
                                        rect, tint_color,
                                        (0, 2 * square_size, square_size,
                                         square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (0, 2 * square_size, square_size,
                                         square_size), 2)
                                elif direction == "SE":
                                    pygame.draw.rect(
                                        rect, tint_color,
                                        (2 * square_size, 2 * square_size,
                                         square_size, square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (2 * square_size, 2 * square_size,
                                         square_size, square_size), 2)
                                # Center
                                elif direction == "C":
                                    center_x = tile_size // 2
                                    center_y = tile_size // 2
                                    square_x = center_x - square_size // 2
                                    square_y = center_y - square_size // 2
                                    pygame.draw.rect(
                                        rect, tint_color,
                                        (square_x, square_y, square_size,
                                         square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (square_x, square_y, square_size,
                                         square_size), 2)
                                # Edges
                                elif direction == "N":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("NW") is not None
                                        or terrains_for_card.get("NE")
                                        is not None)
                                    if edge_has_corners:
                                        mid_x = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (mid_x, 0, square_size,
                                             square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (mid_x, 0, square_size,
                                             square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (0, 0, tile_size, square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, 0, tile_size, square_size), 2)
                                elif direction == "S":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("SW") is not None
                                        or terrains_for_card.get("SE")
                                        is not None)
                                    if edge_has_corners:
                                        mid_x = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (mid_x, 2 * square_size,
                                             square_size, square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (mid_x, 2 * square_size,
                                             square_size, square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (0, 2 * square_size, tile_size,
                                             square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, 2 * square_size, tile_size,
                                             square_size), 2)
                                elif direction == "E":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("NE") is not None
                                        or terrains_for_card.get("SE")
                                        is not None)
                                    if edge_has_corners:
                                        mid_y = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (2 * square_size, mid_y,
                                             square_size, square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (2 * square_size, mid_y,
                                             square_size, square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (2 * square_size, 0, square_size,
                                             tile_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (2 * square_size, 0, square_size,
                                             tile_size), 2)
                                elif direction == "W":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("NW") is not None
                                        or terrains_for_card.get("SW")
                                        is not None)
                                    if edge_has_corners:
                                        mid_y = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (0, mid_y, square_size,
                                             square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, mid_y, square_size,
                                             square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, tint_color,
                                            (0, 0, square_size, tile_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, 0, square_size, tile_size), 2)

                            self.screen.blit(
                                rect, (card_x * tile_size - self.offset_x,
                                       card_y * tile_size - self.offset_y))

            # Draw hover highlight for structure placement
            if settings_manager.get("DEBUG"):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                hovered_structure = self._get_hovered_structure(
                    mouse_x, mouse_y)
                if hovered_structure:
                    hover_color = theme.THEME_GAME_STRUCTURE_HOVER_COLOR
                    structure_type = hovered_structure.get_structure_type()

                    card_edge_map = {}
                    for card, direction in hovered_structure.card_sides:
                        if direction is None:
                            continue
                        if card not in card_edge_map:
                            card_edge_map[card] = []
                        card_edge_map[card].append(direction)

                    for card, directions in card_edge_map.items():
                        card_position = [(x, y)
                                         for y in range(game_board.grid_size)
                                         for x in range(game_board.grid_size)
                                         if game_board.get_card(x, y) == card]
                        if card_position:
                            card_x, card_y = card_position[0]
                            rect = pygame.Surface((tile_size, tile_size),
                                                  pygame.SRCALPHA)
                            rect.fill(theme.THEME_TRANSPARENT_COLOR)
                            for direction in directions:
                                terrains_for_card = card.get_terrains(
                                ) if hasattr(card, 'get_terrains') else {}
                                square_size = tile_size // 3
                                if direction == "NW":
                                    pygame.draw.rect(
                                        rect, hover_color,
                                        (0, 0, square_size, square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (0, 0, square_size, square_size), 2)
                                elif direction == "NE":
                                    pygame.draw.rect(
                                        rect, hover_color,
                                        (2 * square_size, 0, square_size,
                                         square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (2 * square_size, 0, square_size,
                                         square_size), 2)
                                elif direction == "SW":
                                    pygame.draw.rect(
                                        rect, hover_color,
                                        (0, 2 * square_size, square_size,
                                         square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (0, 2 * square_size, square_size,
                                         square_size), 2)
                                elif direction == "SE":
                                    pygame.draw.rect(
                                        rect, hover_color,
                                        (2 * square_size, 2 * square_size,
                                         square_size, square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (2 * square_size, 2 * square_size,
                                         square_size, square_size), 2)
                                elif direction == "C":
                                    center_x = tile_size // 2
                                    center_y = tile_size // 2
                                    square_x = center_x - square_size // 2
                                    square_y = center_y - square_size // 2
                                    pygame.draw.rect(
                                        rect, hover_color,
                                        (square_x, square_y, square_size,
                                         square_size))
                                    pygame.draw.rect(
                                        rect, theme.THEME_TEXT_COLOR_LIGHT,
                                        (square_x, square_y, square_size,
                                         square_size), 2)
                                elif direction == "N":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("NW") is not None
                                        or terrains_for_card.get("NE")
                                        is not None)
                                    if edge_has_corners:
                                        mid_x = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (mid_x, 0, square_size,
                                             square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (mid_x, 0, square_size,
                                             square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (0, 0, tile_size, square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, 0, tile_size, square_size), 2)
                                elif direction == "S":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("SW") is not None
                                        or terrains_for_card.get("SE")
                                        is not None)
                                    if edge_has_corners:
                                        mid_x = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (mid_x, 2 * square_size,
                                             square_size, square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (mid_x, 2 * square_size,
                                             square_size, square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (0, 2 * square_size, tile_size,
                                             square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, 2 * square_size, tile_size,
                                             square_size), 2)
                                elif direction == "E":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("NE") is not None
                                        or terrains_for_card.get("SE")
                                        is not None)
                                    if edge_has_corners:
                                        mid_y = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (2 * square_size, mid_y,
                                             square_size, square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (2 * square_size, mid_y,
                                             square_size, square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (2 * square_size, 0, square_size,
                                             tile_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (2 * square_size, 0, square_size,
                                             tile_size), 2)
                                elif direction == "W":
                                    edge_has_corners = bool(
                                        terrains_for_card.get("NW") is not None
                                        or terrains_for_card.get("SW")
                                        is not None)
                                    if edge_has_corners:
                                        mid_y = (tile_size - square_size) // 2
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (0, mid_y, square_size,
                                             square_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, mid_y, square_size,
                                             square_size), 2)
                                    else:
                                        pygame.draw.rect(
                                            rect, hover_color,
                                            (0, 0, square_size, tile_size))
                                        pygame.draw.rect(
                                            rect, theme.THEME_TEXT_COLOR_LIGHT,
                                            (0, 0, square_size, tile_size), 2)

                            self.screen.blit(
                                rect, (card_x * tile_size - self.offset_x,
                                       card_y * tile_size - self.offset_y))

        tile_size = settings_manager.get("TILE_SIZE")
        figure_size = settings_manager.get("FIGURE_SIZE")
        for figure in placed_figures:
            if figure.card:
                card_position = [(x, y) for y in range(game_board.grid_size)
                                 for x in range(game_board.grid_size)
                                 if game_board.get_card(x, y) == figure.card]
                if card_position:
                    padding = tile_size * 0.1
                    figure_offset = figure_size / 2
                    base_x = card_position[0][0] * tile_size - self.offset_x
                    base_y = card_position[0][1] * tile_size - self.offset_y

                    if figure.position_on_card == "N":
                        figure_x, figure_y = base_x + tile_size / 2, base_y + padding + figure_offset
                    elif figure.position_on_card == "S":
                        figure_x, figure_y = base_x + tile_size / 2, base_y + tile_size - padding - figure_offset
                    elif figure.position_on_card == "E":
                        figure_x, figure_y = base_x + tile_size - padding - figure_offset, base_y + tile_size / 2
                    elif figure.position_on_card == "W":
                        figure_x, figure_y = base_x + padding + figure_offset, base_y + tile_size / 2
                    elif figure.position_on_card == "NW":
                        figure_x, figure_y = base_x + padding + figure_offset, base_y + padding + figure_offset
                    elif figure.position_on_card == "NE":
                        figure_x, figure_y = base_x + tile_size - padding - figure_offset, base_y + padding + figure_offset
                    elif figure.position_on_card == "SW":
                        figure_x, figure_y = base_x + padding + figure_offset, base_y + tile_size - padding - figure_offset
                    elif figure.position_on_card == "SE":
                        figure_x, figure_y = base_x + tile_size - padding - figure_offset, base_y + tile_size - padding - figure_offset
                    else:
                        figure_x, figure_y = base_x + tile_size / 2, base_y + tile_size / 2

                    self.screen.blit(figure.image,
                                     (figure_x - tile_size * 0.15,
                                      figure_y - tile_size * 0.15))

    def draw_side_panel(self, selected_card: typing.Any, remaining_cards: int,
                        current_player: typing.Any, placed_figures: list,
                        detected_structures: list) -> None:
        window_width = settings_manager.get("WINDOW_WIDTH")
        window_height = settings_manager.get("WINDOW_HEIGHT")
        sidebar_width = settings_manager.get("SIDEBAR_WIDTH")

        panel_x = window_width - sidebar_width
        sidebar_center_x = panel_x + sidebar_width // 2

        draw_rect_alpha(self.screen, theme.THEME_GAME_SIDEBAR_BG_COLOR,
                        (panel_x, 0, sidebar_width, window_height))
        padding = theme.THEME_LAYOUT_VERTICAL_GAP
        figure_gap = max(4, padding // 2)
        current_y = padding * 2
        scrollable_content_start_y = current_y

        if selected_card:
            image_to_draw = selected_card.get_rotated_image()

            card_rect = image_to_draw.get_rect()
            card_rect.centerx = sidebar_center_x
            card_rect.y = current_y
            self.screen.blit(image_to_draw, card_rect)
            current_y += card_rect.height + padding
            scrollable_content_start_y = current_y

        offset_y = self.sidebar_scroll_offset

        if settings_manager.get("DEBUG", False):
            network_mode = settings_manager.get("NETWORK_MODE")
            if network_mode == "local":
                status_text = "Local mode"
                status_color = theme.THEME_GAME_STATUS_LOCAL_COLOR
            else:
                player_index = settings_manager.get("PLAYER_INDEX")
                is_my_turn = current_player.get_index() == player_index
                status_text = "Your Turn" if is_my_turn else "Waiting..."
                status_color = (theme.THEME_GAME_STATUS_TURN_COLOR
                                if is_my_turn
                                else theme.THEME_GAME_STATUS_WAIT_COLOR)

            status_surface = self._get_cached_text(
                self.font, status_text, status_color)
            status_rect = status_surface.get_rect()
            status_rect.centerx = sidebar_center_x
            status_rect.y = current_y - offset_y
            if status_rect.bottom > scrollable_content_start_y and status_rect.top < window_height:
                self.screen.blit(status_surface, status_rect)
            current_y += status_rect.height + padding

        cards_surface = self._get_cached_text(
            self.font,
            f"Cards left: {remaining_cards}",
            theme.THEME_TEXT_COLOR_LIGHT,
        )
        cards_rect = cards_surface.get_rect()
        cards_rect.centerx = sidebar_center_x
        cards_rect.y = current_y - offset_y
        if cards_rect.bottom > scrollable_content_start_y and cards_rect.top < window_height:
            self.screen.blit(cards_surface, cards_rect)
        current_y += cards_rect.height + padding

        all_players = self.session.get_players()

        for i, player in enumerate(all_players):
            is_current_player = (player == current_player)

            figures = player.get_figures()
            name_text = player.get_name()
            try:
                color_string = player.get_color()
                player_color = theme.THEME_PLAYER_COLOR_MAP.get(
                    color_string, theme.THEME_TEXT_COLOR_LIGHT)
            except Exception as e:
                logger.error(f"Failed to get player color: {e}")
                player_color = theme.THEME_TEXT_COLOR_LIGHT
            name_surface = self._get_cached_text(
                self.font,
                name_text,
                player_color,
            )
            name_height = name_surface.get_height()

            score_color = theme.THEME_GAME_SCORE_TEXT_COLOR
            score_surface = self._get_cached_text(
                self.font,
                f"Score: {player.get_score()}",
                score_color,
            )
            score_height = score_surface.get_height()

            grid_height = 0
            if figures:
                figure_size = settings_manager.get("FIGURE_SIZE")
                figures_per_row = max(1, (sidebar_width - 20) //
                                      (figure_size + figure_gap))
                figures_per_row = min(figures_per_row, len(figures))
                total_rows = (len(figures) + figures_per_row -
                              1) // figures_per_row
                grid_height = (total_rows * figure_size
                               + (total_rows - 1) * figure_gap)

            player_section_height = (name_height + padding + score_height
                                     + (padding if figures else 0)
                                     + grid_height)

            if is_current_player:
                player_bg_rect = pygame.Rect(panel_x + 5,
                                             current_y - offset_y
                                             - (padding // 2),
                                             sidebar_width - 10,
                                             player_section_height + padding)
                if player_bg_rect.bottom > scrollable_content_start_y and player_bg_rect.top < window_height:
                    draw_rect_alpha(
                        self.screen,
                        theme.THEME_GAME_CURRENT_PLAYER_BG_COLOR,
                        player_bg_rect)
                    draw_rect_alpha(
                        self.screen,
                        theme.THEME_GAME_CURRENT_PLAYER_BORDER_COLOR,
                        player_bg_rect,
                        2)
            name_rect = name_surface.get_rect()
            name_rect.centerx = sidebar_center_x
            name_rect.y = current_y - offset_y
            if name_rect.bottom > scrollable_content_start_y and name_rect.top < window_height:
                self.screen.blit(name_surface, name_rect)
            current_y += name_rect.height + padding

            score_rect = score_surface.get_rect()
            score_rect.centerx = sidebar_center_x
            score_rect.y = current_y - offset_y
            if score_rect.bottom > scrollable_content_start_y and score_rect.top < window_height:
                self.screen.blit(score_surface, score_rect)
            current_y += score_rect.height + padding

            if figures:
                figure_size = settings_manager.get("FIGURE_SIZE")
                figures_padding = max(10, padding)
                available_width = sidebar_width - (2 * figures_padding)
                figures_per_row = max(1, available_width //
                                      (figure_size + figure_gap))
                figures_per_row = min(figures_per_row, len(figures))

                total_rows = (len(figures) + figures_per_row -
                              1) // figures_per_row
                actual_grid_width = (figures_per_row * figure_size
                                     + (figures_per_row - 1) * figure_gap)

                grid_start_x = sidebar_center_x - actual_grid_width // 2
                grid_start_y = current_y - offset_y

                if grid_start_y + total_rows * (
                        figure_size + figure_gap
                ) > scrollable_content_start_y and grid_start_y < window_height:
                    for j, figure in enumerate(figures):
                        row = j // figures_per_row
                        col = j % figures_per_row

                        fig_x = grid_start_x + col * (figure_size + figure_gap)
                        fig_y = grid_start_y + row * (figure_size + figure_gap)

                        if fig_y + figure_size > scrollable_content_start_y and fig_y < window_height:
                            self.screen.blit(figure.image, (fig_x, fig_y))

                current_y += grid_height + padding

            if i < len(all_players) - 1:
                current_y += padding

        if (current_player.get_is_ai()
                and hasattr(current_player, 'is_thinking')
                and current_player.is_thinking()
                and settings_manager.get("DEBUG", False)):
            current_y += padding

            thinking_text = f"AI is thinking..."
            thinking_surface = self._get_cached_text(
                self.font, thinking_text, theme.THEME_GAME_AI_THINKING_COLOR)
            thinking_rect = thinking_surface.get_rect()
            thinking_rect.centerx = sidebar_center_x
            thinking_rect.y = current_y - offset_y
            if thinking_rect.bottom > scrollable_content_start_y and thinking_rect.top < window_height:
                self.screen.blit(thinking_surface, thinking_rect)
            current_y += thinking_rect.height + padding

            progress = current_player.get_thinking_progress()
            self.ai_thinking_progress_bar.set_progress(progress)
            self.ai_thinking_progress_bar.rect.y = current_y - offset_y

            if self.ai_thinking_progress_bar.rect.bottom > scrollable_content_start_y and self.ai_thinking_progress_bar.rect.top < window_height:
                self.ai_thinking_progress_bar.draw(self.screen, y_offset=0)

            current_y += self.ai_thinking_progress_bar.rect.height + padding

        if settings_manager.get("DEBUG"):
            current_y += padding
            structure_surface = self._get_cached_text(
                self.font,
                f"Structures: {len(detected_structures)}",
                theme.THEME_TEXT_COLOR_LIGHT,
            )
            structure_rect = structure_surface.get_rect()
            structure_rect.centerx = sidebar_center_x
            structure_rect.y = current_y - offset_y
            if structure_rect.bottom > scrollable_content_start_y and structure_rect.top < window_height:
                self.screen.blit(structure_surface, structure_rect)
            current_y += structure_rect.height + padding

        max_scroll = max(0, current_y - window_height + padding * 2)
        self.sidebar_scroll_offset = min(self.sidebar_scroll_offset,
                                         max_scroll)

    def scroll(self, direction: str) -> None:
        """
        Scrolls the view of the board based on user input.
        :param direction: The direction to scroll ('up', 'down', 'left', 'right').
        """
        if direction == "up":
            self.offset_y -= self.scroll_speed
        elif direction == "down":
            self.offset_y += self.scroll_speed
        elif direction == "left":
            self.offset_x -= self.scroll_speed
        elif direction == "right":
            self.offset_x += self.scroll_speed

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEWHEEL and hasattr(
                    self, 'game_log') and self.game_log.visible:
                self.game_log.handle_scroll(event.y)
                return

        if not (hasattr(self, 'game_log') and self.game_log.visible):
            self._apply_sidebar_scroll(events)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.keys_pressed[event.key] = (event.type == pygame.KEYDOWN)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.game_log.toggle_visibility()
                elif event.key == pygame.K_ESCAPE:
                    self.switch_scene(GameState.MENU)

            allow_action = True
            network_mode = settings_manager.get("NETWORK_MODE")
            if network_mode in ("host", "client"):
                current_player = self.session.get_current_player()
                player_index = settings_manager.get("PLAYER_INDEX")
                if not current_player or current_player.get_index(
                ) != player_index or self.session.get_game_over():
                    allow_action = False
            elif network_mode == "local":
                current_player = self.session.get_current_player()
                if current_player and current_player.get_is_ai():
                    allow_action = False

            if allow_action:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    window_width = settings_manager.get("WINDOW_WIDTH")
                    sidebar_width = settings_manager.get("SIDEBAR_WIDTH")
                    panel_x = window_width - sidebar_width

                    if mouse_x < panel_x:
                        self._handle_mouse_click(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._execute_local_skip()

        self._handle_key_hold()

    def _handle_mouse_click(self, event: pygame.event.Event) -> None:
        x, y = event.pos
        tile_size = settings_manager.get("TILE_SIZE")
        grid_x, grid_y = (x + self.get_offset_x()) // tile_size, (
            y + self.get_offset_y()) // tile_size

        logger.debug(f"Registered {event.button}")

        if event.button == 1:
            direction = self._detect_click_direction(x, y, grid_x, grid_y)
            self._execute_local_turn(grid_x, grid_y, direction)

        if event.button == 3 and self.session.get_current_card():
            self._execute_local_rotate()

    def _execute_local_turn(self, x: int, y: int, direction: str) -> None:
        """Execute a turn locally and send command to network."""
        from network.command import PlaceCardCommand, PlaceFigureCommand
        from utils.settings_manager import settings_manager

        current_player = self.session.get_current_player()
        player_index = current_player.get_index() if current_player else 0

        if self.session.turn_phase == 1:
            command = PlaceCardCommand(
                player_index=player_index,
                x=x,
                y=y,
                card_rotation=self.session.get_current_card().rotation
                if self.session.get_current_card() else 0)
        else:
            command = PlaceFigureCommand(player_index=player_index,
                                         x=x,
                                         y=y,
                                         position=direction)

        success = self.session.execute_command(command)
        if success:
            if self.network and hasattr(self.network, 'send_command'):
                self.network.send_command(command)

            self._update_valid_placements()
            self.player_action_time = pygame.time.get_ticks() / 1000.0
            self.ai_turn_start_time = None

    def _execute_local_rotate(self) -> None:
        """Execute a card rotation locally and send command to network."""
        from network.command import RotateCardCommand
        from utils.settings_manager import settings_manager

        if not self.session.get_current_card():
            return

        current_player = self.session.get_current_player()
        player_index = current_player.get_index() if current_player else 0
        command = RotateCardCommand(player_index=player_index)

        success = self.session.execute_command(command)
        if success:
            if self.network and hasattr(self.network, 'send_command'):
                self.network.send_command(command)

            self._update_valid_placements()

    def _execute_local_skip(self) -> None:
        """Execute a skip action locally and send command to network."""
        from network.command import SkipActionCommand
        from utils.settings_manager import settings_manager

        current_player = self.session.get_current_player()
        player_index = current_player.get_index() if current_player else 0
        action_type = "card" if self.session.turn_phase == 1 else "figure"

        command = SkipActionCommand(player_index=player_index,
                                    action_type=action_type)

        success = self.session.execute_command(command)
        if success:
            if self.network and hasattr(self.network, 'send_command'):
                self.network.send_command(command)

            self._update_valid_placements()

    def _handle_key_hold(self) -> None:
        if self.keys_pressed.get(pygame.K_w) or self.keys_pressed.get(
                pygame.K_UP):
            self.scroll("up")
        if self.keys_pressed.get(pygame.K_s) or self.keys_pressed.get(
                pygame.K_DOWN):
            self.scroll("down")
        if self.keys_pressed.get(pygame.K_a) or self.keys_pressed.get(
                pygame.K_LEFT):
            self.scroll("left")
        if self.keys_pressed.get(pygame.K_d) or self.keys_pressed.get(
                pygame.K_RIGHT):
            self.scroll("right")

    def _detect_click_direction(self, mouse_x: int, mouse_y: int, grid_x: int,
                                grid_y: int) -> typing.Optional[str]:
        tile_size = settings_manager.get("TILE_SIZE")
        tile_screen_x = grid_x * tile_size - self.get_offset_x()
        tile_screen_y = grid_y * tile_size - self.get_offset_y()

        relative_x = mouse_x - tile_screen_x
        relative_y = mouse_y - tile_screen_y

        card = self.session.get_game_board().get_card(grid_x, grid_y)
        if not card:
            return None

        logger.debug(f"Retrieved card {card} at {grid_x};{grid_y}")

        supports_center = card.get_terrains().get("C") is not None

        third_size = tile_size // 3
        two_third_size = 2 * tile_size // 3

        terrains = card.get_terrains()
        if relative_x < third_size and relative_y < third_size and terrains.get(
                "NW") is not None:
            return "NW"
        if relative_x >= two_third_size and relative_y < third_size and terrains.get(
                "NE") is not None:
            return "NE"
        if relative_x < third_size and relative_y >= two_third_size and terrains.get(
                "SW") is not None:
            return "SW"
        if relative_x >= two_third_size and relative_y >= two_third_size and terrains.get(
                "SE") is not None:
            return "SE"

        if third_size < relative_x < two_third_size and third_size < relative_y < two_third_size:
            if supports_center:
                return "C"

        distances = {
            "N": relative_y,
            "S": tile_size - relative_y,
            "W": relative_x,
            "E": tile_size - relative_x
        }

        return min(distances, key=distances.get)

    def _get_hovered_structure(self, mouse_x: int,
                               mouse_y: int) -> typing.Optional[typing.Any]:
        """Get the structure that would be selected if placing a meeple at the hovered position."""

        tile_size = settings_manager.get("TILE_SIZE")
        grid_x, grid_y = (mouse_x + self.get_offset_x()) // tile_size, (
            mouse_y + self.get_offset_y()) // tile_size

        card = self.session.get_game_board().get_card(grid_x, grid_y)
        if not card:
            return None

        direction = self._detect_click_direction(mouse_x, mouse_y, grid_x,
                                                 grid_y)
        if not direction:
            return None

        for structure in self.session.get_structures():
            for structure_card, structure_direction in structure.card_sides:
                if structure_card == card and structure_direction == direction:
                    return structure

        return None

    def _update_game_session(self, new_session) -> None:
        """
        Update the game session and invalidate render cache.
        Called when the game session is updated from network.
        """
        self.session = new_session
        self._invalidate_render_cache()

    def update(self) -> None:
        fps = settings_manager.get("FPS")
        if self.session.get_game_over():
            self.clock.tick(fps)
            return

        current_player = self.session.get_current_player()

        if self.session.get_is_first_round() or not current_player.get_is_ai():
            self.clock.tick(fps)
            return

        if self.session.get_current_card() is None:
            self.clock.tick(fps)
            return

        if hasattr(current_player,
                   'is_thinking') and current_player.is_thinking():
            current_player.play_turn(self.session)
            self.clock.tick(fps)
            return

        if hasattr(current_player, 'play_turn'):
            logger.debug(f"Starting AI turn for {current_player.get_name()}")
            current_player.play_turn(self.session)
        else:
            logger.warning(
                f"Player {current_player.get_name()} is marked as AI but doesn't have play_turn method"
            )

        self.clock.tick(fps)

    def draw(self) -> None:
        self._update_valid_placements()
        self._draw_background(
            background_color=theme.THEME_GAME_BACKGROUND_COLOR,
            image_name=theme.THEME_GAME_BACKGROUND_IMAGE,
            scale_mode=theme.THEME_GAME_BACKGROUND_SCALE_MODE,
            tint_color=theme.THEME_GAME_BACKGROUND_TINT_COLOR,
            blur_radius=theme.THEME_GAME_BACKGROUND_BLUR_RADIUS,
        )
        self.draw_board(self.session.get_game_board(),
                        self.session.get_placed_figures(),
                        self.session.get_structures(),
                        self.session.get_is_first_round(),
                        self.session.get_game_over(),
                        self.session.get_players())

        if not self.session.get_game_over(
        ) and not self.session.get_is_first_round():
            self.draw_side_panel(self.session.get_current_card(),
                                 len(self.session.get_cards_deck()),
                                 self.session.get_current_player(),
                                 self.session.get_placed_figures(),
                                 self.session.get_structures())

        self.game_log.draw(self.screen)

        self.toast_manager.draw(self.screen)

    def refresh_theme(self, theme_name: str | None = None) -> None:
        """Refresh fonts and component styling after theme changes."""
        super().refresh_theme(theme_name)
        self.font = theme.get_font("body", theme.THEME_FONT_SIZE_BODY)
        self.game_over_title_font = theme.get_font(
            "title", theme.THEME_FONT_SIZE_GAME_OVER_TITLE
        )
        self.game_over_table_font = theme.get_font(
            "label", theme.THEME_FONT_SIZE_BUTTON
        )
        self.game_over_row_font = theme.get_font(
            "body", theme.THEME_FONT_SIZE_GAME_OVER_ROW
        )
        self.game_over_hint_font = theme.get_font(
            "body", theme.THEME_FONT_SIZE_BODY
        )
        self._text_surface_cache.clear()
        self.ai_thinking_progress_bar.set_font(self.font)
        self.ai_thinking_progress_bar.apply_theme()
        self.toast_manager.apply_theme()
        self._invalidate_render_cache()
