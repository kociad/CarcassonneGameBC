import random
import logging
import typing
import utils.loggingConfig

from models.gameBoard import GameBoard
from models.card import Card
from models.player import Player
from models.structure import Structure
from models.aiPlayer import AIPlayer
from models.figure import Figure
import settings
from utils.settingsManager import settings_manager
from models.cardSets.setLoader import load_all_card_sets, load_card_set

logger = logging.getLogger(__name__)


class GameSession:
    """Manages the overall game state, including players, board, and card placement."""

    def __init__(self,
                 player_names: list[str],
                 no_init: bool = False,
                 lobby_completed: bool = True,
                 network_mode: str = 'local') -> None:
        """Initialize a new game session."""
        self.players = []
        self.current_player = None
        self.game_board = GameBoard()
        self.cards_deck = []
        self.current_card = None
        self.last_placed_card = None
        self.is_first_round = True
        self.game_over = False
        self.turn_phase = 1
        self.placed_figures = []
        self.structures = []
        self.structure_map = {}
        self.network_mode = network_mode
        self.lobby_completed = lobby_completed
        self.game_mode = None
        self.on_turn_ended = None
        self.on_show_notification = None
        self.on_command_executed = None

        self._candidate_positions = set()
        self._last_board_state = None

        self._structure_cache = {}
        self._structure_cache_valid = False
        self._last_board_hash = None

        self._validation_cache = {}
        self._validation_cache_valid = False

        self._neighbor_cache = {}
        self._neighbor_cache_valid = False

        if not no_init:
            self._generate_player_list(player_names)
            self.cards_deck = self._generate_cards_deck()
            self._shuffle_cards_deck(self.cards_deck)
            self._place_starting_card()

    def get_players(self) -> list:
        """Return the list of player objects."""
        return self.players

    def get_game_over(self) -> bool:
        """Return True if the game is over."""
        return self.game_over

    def get_current_card(self) -> typing.Any:
        """Return the currently drawn card."""
        return self.current_card

    def get_game_board(self) -> typing.Any:
        """Return the game board used by the current game session."""
        return self.game_board

    def get_cards_deck(self) -> typing.Any:
        """Return the cards deck assigned to the current game session."""
        return self.cards_deck

    def get_current_player(self) -> typing.Any:
        """Return the player currently having their turn."""
        return self.current_player

    def get_placed_figures(self) -> list:
        """Return the list of figures placed on the board."""
        return self.placed_figures

    def get_structures(self) -> list:
        """Return the list of detected structures."""
        return self.structures

    def set_turn_phase(self, phase: int) -> None:
        """Set the current turn phase."""
        self.turn_phase = phase

    def get_is_first_round(self) -> bool:
        """Return True if this is the first round."""
        return self.is_first_round

    def _generate_player_list(self, player_names: list[str]) -> None:
        """Generate a list of indexed players for the game."""
        logger.debug("Generating a list of players...")
        colors = ["blue", "red", "green", "pink", "yellow", "black"]
        random.shuffle(colors)
        if player_names:
            index = 0
            for player in player_names:
                color = colors.pop()
                if player.startswith("AI_"):
                    difficulty = "NORMAL"
                    if player.startswith("AI_EASY_"):
                        difficulty = "EASY"
                    elif player.startswith("AI_HARD_"):
                        difficulty = "HARD"
                    elif player.startswith("AI_EXPERT_"):
                        difficulty = "EXPERT"
                    elif player.startswith("AI_NORMAL_"):
                        difficulty = "NORMAL"

                    self.players.append(
                        AIPlayer(player, index, color, difficulty))
                else:
                    self.players.append(Player(player, color, index))
                index += 1
            self.current_player = self.players[len(self.players) - 1]
        logger.debug("Player list generated")

    def _generate_cards_deck(self) -> list:
        """Generate a deck of cards for the game by loading selected card sets."""
        logger.debug("Generating deck...")

        selected_card_sets = settings_manager.get("SELECTED_CARD_SETS",
                                               ["baseGame"])

        card_definitions = []
        card_distributions = {}

        for set_name in selected_card_sets:
            set_data = load_card_set(set_name)
            if set_data['definitions']:
                card_definitions.extend(set_data['definitions'])
                card_distributions.update(set_data['distributions'])
                logger.info(
                    f"Loaded selected card set: {set_name} with {len(set_data['definitions'])} card definitions"
                )

        cards = []
        for card in card_definitions:
            image = card["image"]
            terrains = card["terrains"]
            connections = card["connections"]
            features = card["features"]
            count = card_distributions.get(image, 1)
            cards.extend([
                Card(settings.TILE_IMAGES_PATH + image, terrains, connections,
                     features) for _ in range(count)
            ])

        logger.debug(
            f"Deck generated with {len(cards)} cards from {len(card_definitions)} card definitions"
        )
        return cards

    def _shuffle_cards_deck(self, deck: list) -> None:
        """Shuffle an existing deck of cards."""
        logger.debug("Shuffling deck...")
        random.shuffle(deck)
        logger.debug("Deck shuffled")

    def _place_starting_card(self) -> None:
        """Place the first card automatically at the center of the board."""
        logger.debug("Playing first turn...")
        center_x, center_y = self.game_board.get_center_position()
        if self.cards_deck:
            if self.play_card(center_x, center_y):
                self.is_first_round = False
                logger.debug(
                    "First turn played - starting card placed, moving to next player"
                )
                self.next_turn()
        else:
            logger.debug("Unable to play first round, no cards_deck available")

    def _draw_card(self) -> typing.Any:
        """Draw a card from the deck for the current player."""
        logger.debug("Drawing card...")
        if self.cards_deck:
            logger.debug("Card drawn")
            return self.cards_deck.pop(0)
        return None

    def next_turn(self) -> None:
        """Advance to the next player's turn."""
        if self.cards_deck:
            logger.debug("Advancing player turn...")
            current_index = self.current_player.get_index()
            next_index = (current_index + 1) % len(self.players)
            for player in self.players:
                if player.get_index() == next_index:
                    self.current_player = player
                    break
            logger.info(
                f"{self.current_player.get_name()}'s turn (Player {self.current_player.get_index() + 1})"
            )
            self.current_card = self._draw_card()
            if self.current_card:
                logger.info(
                    f"New card drawn - {len(self.cards_deck)} cards remaining")
                self.turn_phase = 1
                if self.on_turn_ended:
                    self.on_turn_ended()
            else:
                logger.debug("No card drawn, ending game")
                self.end_game()
        else:
            self.end_game()

    def play_card(self, x: int, y: int) -> bool:
        """Play the card placing part of the turn."""
        logger.debug("Playing card...")
        card = self.current_card
        if not card:
            if not self.cards_deck:
                logger.debug(
                    "Unable to play turn, no card is selected and no cards_deck is available"
                )
                return False
            card = self._draw_card()
        if not self.game_board.validate_card_placement(
                card, x, y) and not self.is_first_round:
            logger.debug(
                f"Player {self.current_player.get_name()} was unable to place card, placement is invalid"
            )
            if self.on_show_notification and not self.current_player.get_is_ai():
                self.on_show_notification(
                    "error",
                    "Cannot place card here - terrain doesn't match adjacent cards!"
                )
            return False
        self.game_board.place_card(card, x, y)
        self.last_placed_card = card
        self.current_card = None
        if not self.is_first_round:
            logger.info(
                f"Player {self.current_player.get_name()} placed a card at [{x - self.game_board.get_center()},{self.game_board.get_center() - y}]"
            )
        logger.debug(f"Last played card set to card {card} at {x};{y}")
        self._invalidate_candidate_cache()
        self._invalidate_structure_cache()
        self._invalidate_validation_cache()
        self._invalidate_neighbor_cache()

        for player in self.players:
            if hasattr(player, 'invalidate_evaluation_cache'):
                player.invalidate_evaluation_cache()
            if hasattr(player, 'invalidate_figure_cache'):
                player.invalidate_figure_cache()

        if hasattr(self, 'on_render_cache_invalidate'):
            self.on_render_cache_invalidate()

        self.detect_structures()
        return True

    def discard_current_card(self) -> None:
        """Discard the currently selected card and select a new one."""
        if self.current_card:
            self.current_card = self._draw_card()

    def play_ai_turn(self, player: typing.Any = None) -> None:
        """If the current player is AI, trigger their turn."""
        if player is None:
            player = self.current_player
        if isinstance(player, AIPlayer):
            player.play_turn(self)
            return

    def play_turn(self,
                 x: int,
                 y: int,
                 position: str = "C",
                 player: typing.Any = None) -> None:
        """Play a single complete game turn in two phases."""
        if player is None:
            player = self.current_player

        logger.debug(
            f"play_turn called - Phase: {self.turn_phase}, Player: {player.get_name()}, Position: ({x},{y})"
        )

        if self.turn_phase == 1:
            logger.debug("Turn Phase 1: Attempting to place card...")
            if self.play_card(x, y):
                self.turn_phase = 2
                logger.debug("Card placed successfully, moving to Phase 2")
            else:
                logger.debug("Card placement failed.")
            return
        elif self.turn_phase == 2:
            logger.debug("Turn Phase 2: Attempting to place figure...")
            figure_placed = self.play_figure(player, x, y, position)
            if figure_placed:
                logger.debug("Figure placed.")
                logger.debug("Checking completed structures...")
                for structure in self.structures:
                    structure.check_completion()
                    if structure.get_is_completed():
                        logger.debug(
                            f"Structure {structure.structure_type} is completed!"
                        )
                        self.score_structure(structure)
                self.next_turn()
            else:
                logger.debug("Figure not placed or skipped.")

    def execute_command(self, command) -> bool:
        """Execute a command received from the network."""
        try:
            logger.debug(
                f"Executing command {command.command_type} for player {command.player_index}"
            )

            if command.player_index != self.current_player.get_index():
                logger.warning(
                    f"Command from wrong player: {command.player_index} vs {self.current_player.get_index()}"
                )
                return False

            if command.command_type == "place_card":
                if self.current_card:
                    while self.current_card.rotation != command.card_rotation:
                        self.current_card.rotate()
                success = self.play_card(command.x, command.y)
                if success:
                    self.turn_phase = 2
                return success

            elif command.command_type == "place_figure":
                if self.turn_phase != 2:
                    logger.warning("Cannot place figure in phase 1")
                    return False
                figure_placed = self.play_figure(self.current_player, command.x,
                                               command.y, command.position)
                if figure_placed:
                    for structure in self.structures:
                        structure.check_completion()
                        if structure.get_is_completed():
                            self.score_structure(structure)
                    self.next_turn()
                return figure_placed

            elif command.command_type == "skip_action":
                if command.action_type == "card" and self.turn_phase == 1:
                    self.skip_current_action()
                    return True
                elif command.action_type == "figure" and self.turn_phase == 2:
                    self.skip_current_action()
                    return True
                else:
                    logger.warning(
                        f"Cannot skip {command.action_type} in phase {self.turn_phase}"
                    )
                    return False

            elif command.command_type == "rotate_card":
                if self.current_card and self.turn_phase == 1:
                    self.current_card.rotate()
                    return True
                else:
                    logger.warning("Cannot rotate card")
                    return False

            else:
                logger.warning(f"Unknown command type: {command.command_type}")
                return False

        except Exception as e:
            logger.exception(
                f"Error executing command {command.command_type}: {e}")
            return False
        finally:
            if self.on_command_executed:
                self.on_command_executed(command)

    def skip_current_action(self) -> None:
        """Skip the current phase action with official rules validation."""
        if self.turn_phase == 1:
            logger.debug("Attempting to skip card placement...")
            if self.can_place_card_anywhere(self.current_card):
                logger.debug(
                    f"Player {self.current_player.get_name()} was unable to skip card placement - card can be placed somewhere on the board"
                )
                if self.on_show_notification and not self.current_player.get_is_ai():
                    self.on_show_notification(
                        "warning",
                        "Cannot discard card - it can be placed on the board!")
            else:
                logger.info(
                    f"Player {self.current_player.get_name()} discarded card - no valid placement was found"
                )
                self.discard_current_card()
                if not self.cards_deck:
                    self.end_game()
        elif self.turn_phase == 2:
            logger.info(
                f"Player {self.current_player.get_name()} skipped meeple placement"
            )
            logger.debug("Finalizing turn...")
            for structure in self.structures:
                structure.check_completion()
                if structure.get_is_completed():
                    self.score_structure(structure)
            self.next_turn()
            self.turn_phase = 1

    def play_figure(self, player: typing.Any, x: int, y: int,
                   position: str) -> bool:
        """Place a figure on a valid card position."""
        logger.debug("Playing figure...")
        card = self.game_board.get_card(x, y)
        if card != self.last_placed_card:
            logger.debug(
                f"Player {player.get_name()} was unable to play figure on card {self.game_board.get_card(x,y)} at [{x},{y}], can only place figures on last played card"
            )
            if self.on_show_notification and not player.get_is_ai():
                self.on_show_notification(
                    "error",
                    "Cannot place meeple here - only on the card you just placed!"
                )
            return False
        if not card:
            logger.debug(
                f"Player {player.get_name()} was unable to place their meeple at [{x},{y}], no card was found."
            )
            if self.on_show_notification and not player.get_is_ai():
                self.on_show_notification("error",
                                        "No card found at this position!")
            return False
        structure = self.structure_map.get((x, y, position))
        if structure:
            if structure.figures:
                logger.debug(
                    f"Player {player.get_name()} was unable to place their meeple at [{x},{y}], position {position}, the structure is already occupied"
                )
                if self.on_show_notification and not player.get_is_ai():
                    self.on_show_notification(
                        "error",
                        "Cannot place meeple - this structure is already occupied!"
                    )
                return False
        if player.figures:
            logger.debug(
                f"Player {player.get_name()} has {len(player.figures)} figures before placement"
            )
            figure = player.get_figure()
            logger.debug(
                f"Player {player.get_name()} has {len(player.figures)} figures after get_figure()"
            )
            if figure.place(card, position):
                self.placed_figures.append(figure)
                logger.info(
                    f"Player {player.get_name()} placed a figure on {position} position at [{x - self.game_board.get_center()},{self.game_board.get_center() - y}]"
                )
                if structure:
                    structure.add_figure(figure)
                logger.debug(
                    f"Player {player.get_name()} has {len(player.figures)} figures after successful placement"
                )
                logger.debug("Figure played")
                return True
            else:
                player.add_figure(figure)
                logger.debug(
                    f"Player {player.get_name()} has {len(player.figures)} figures after failed placement (figure returned)"
                )
        logger.debug(
            f"Player {player.get_name()} was unable to place their meeple, player has no meeples left"
        )
        if self.on_show_notification and not player.get_is_ai():
            self.on_show_notification("error", "No meeples left to place!")
        return False

    def detect_structures(self) -> None:
        """Update structures based only on the last placed card."""
        logger.debug("Updating structures based on the last placed card...")
        if not self.last_placed_card:
            logger.debug("No card was placed. Skipping structure detection.")
            return

        current_board_hash = self._get_board_state_hash()
        if (self._structure_cache_valid
                and self._last_board_hash == current_board_hash
                and self._structure_cache):
            logger.debug("Using cached structure detection results")
            return

        position = self.game_board.get_card_position(self.last_placed_card)
        if not position:
            logger.debug("Last placed card position not found.")
            return

        x, y = position
        self.visited = set()

        for direction in self.last_placed_card.get_terrains().keys():
            cache_key = self._get_structure_cache_key(x, y, direction, "")
            if cache_key in self._structure_cache:
                del self._structure_cache[cache_key]

        for direction, terrain_type in self.last_placed_card.get_terrains().items(
        ):
            key = (x, y, direction)
            if not terrain_type or key in self.structure_map:
                continue

            cache_key = self._get_structure_cache_key(x, y, direction, terrain_type)
            if cache_key in self._structure_cache:
                logger.debug(f"Using cached structure for {cache_key}")
                cached_structure = self._structure_cache[cache_key]
                if cached_structure:
                    self.structure_map[key] = cached_structure
                    cached_structure.add_card_side(self.last_placed_card, direction)
                continue

            connected_sides = self.scan_connected_sides(x, y, direction,
                                                     terrain_type)
            connected_structures = {
                self.structure_map.get(side)
                for side in connected_sides if self.structure_map.get(side)
            }
            connected_structures.discard(None)

            if connected_structures:
                main_structure = connected_structures.pop()
                for s in connected_structures:
                    main_structure.merge(s)
                    self.structures.remove(s)
            else:
                main_structure = Structure(terrain_type.capitalize())
                self.structures.append(main_structure)

            self._structure_cache[cache_key] = main_structure

            for cx, cy, cdir in connected_sides:
                self.structure_map[(cx, cy, cdir)] = main_structure
                main_structure.add_card_side(self.game_board.get_card(cx, cy), cdir)

        self._structure_cache_valid = True
        self._last_board_hash = current_board_hash

    def find_connected_structures(self, x: int, y: int, direction: str,
                                terrain_type: str, structure_map: dict) -> list:
        """Find existing structures connected to the given card side."""
        neighbors = {
            "N": (x, y - 1, "S"),
            "S": (x, y + 1, "N"),
            "E": (x + 1, y, "W"),
            "W": (x - 1, y, "E")
        }
        connected = []
        for dir, (nx, ny, ndir) in neighbors.items():
            if direction == dir:
                s = structure_map.get((nx, ny, ndir))
                if s and s.get_structure_type().lower() == terrain_type:
                    logger.debug(
                        f"Existing structure detected at ({nx}, {ny}) {ndir}")
                    connected.append(s)
        return list(set(connected))

    def scan_connected_sides(self, x: int, y: int, direction: str,
                           terrain_type: str) -> set:
        """Collect all connected sides forming a continuous structure."""
        visited = set()
        stack = [(x, y, direction)]
        while stack:
            cx, cy, cdir = stack.pop()
            if (cx, cy, cdir) in visited:
                continue
            card = self.game_board.get_card(cx, cy)
            if not card:
                continue
            if card.get_terrains().get(cdir) != terrain_type:
                continue
            visited.add((cx, cy, cdir))
            connected_dirs = card.get_connections().get(
                cdir, []) if card.get_connections() else []
            for dir2 in connected_dirs:
                if (cx, cy, dir2) not in visited:
                    stack.append((cx, cy, dir2))
            neighbors = {
                "N": (cx, cy - 1, "S"),
                "S": (cx, cy + 1, "N"),
                "E": (cx + 1, cy, "W"),
                "W": (cx - 1, cy, "E")
            }
            if terrain_type == "field":
                edge_line_adjacents = {
                    "N": [((cx - 1, cy), "N"), ((cx + 1, cy), "N")],
                    "S": [((cx - 1, cy), "S"), ((cx + 1, cy), "S")],
                    "E": [((cx, cy - 1), "E"), ((cx, cy + 1), "E")],
                    "W": [((cx, cy - 1), "W"), ((cx, cy + 1), "W")],
                }
                if cdir in edge_line_adjacents:
                    for (nx, ny), ndir in edge_line_adjacents[cdir]:
                        neighbor = self.game_board.get_card(nx, ny)
                        if neighbor and neighbor.get_terrains().get(
                                ndir) == terrain_type:
                            if (nx, ny, ndir) not in visited:
                                stack.append((nx, ny, ndir))
            if cdir in neighbors:
                nx, ny, ndir = neighbors[cdir]
                neighbor = self.game_board.get_card(nx, ny)
                if neighbor and neighbor.get_terrains().get(
                        ndir) == terrain_type:
                    stack.append((nx, ny, ndir))
        return visited

    def score_structure(self, structure: typing.Any) -> None:
        """Score a completed structure by awarding points to the majority owner(s)."""
        if not structure.get_is_completed() and not self.game_over:
            logger.debug("Structure is not completed, skipping scoring.")
            return
        score = structure.get_score(game_session=self)
        owners = structure.get_majority_owners()
        if not owners:
            logger.debug(
                f"{structure.structure_type} was completed but there were no meeples to score"
            )
            return
        if not self.game_over:
            logger.info(f"{structure.structure_type} was completed")
        for owner in owners:
            logger.scoring(
                f"Player {owner.get_name()} scored {score} points from the {structure.structure_type}"
            )
            owner.add_score(score)

            if self.on_show_notification:
                message = f"Player {owner.get_name()} scored {score} points from {structure.structure_type}!"
                self.on_show_notification("success", message)

        structure.set_color(owners[0].get_color_with_alpha())
        for figure in structure.get_figures()[:]:
            structure.remove_figure(figure)
            figure.owner.add_figure(figure)
            logger.info(f"{figure.owner.get_name()}'s figure was returned")

    def end_game(self) -> None:
        """End the game and score all incomplete structures."""
        logger.info("GAME OVER - No more cards in deck!")
        logger.scoring("Remaining incomplete structures will now be scored...")
        logger.debug("=== END OF GAME TRIGGERED ===")

        if self.on_show_notification:
            self.on_show_notification(
                "info", "Game Over! Scoring remaining structures...")

        self.game_over = True
        for structure in self.structures:
            if not structure.get_is_completed():
                logger.debug(
                    f"Scoring incomplete {structure.structure_type}...")
                self.score_structure(structure)
        logger.debug("All meeples have been returned to players")
        self.placed_figures.clear()

        self._invalidate_candidate_cache()
        self._invalidate_structure_cache()
        self._invalidate_validation_cache()
        self._invalidate_neighbor_cache()

        for player in self.players:
            if hasattr(player, 'invalidate_evaluation_cache'):
                player.invalidate_evaluation_cache()
            if hasattr(player, 'invalidate_figure_cache'):
                player.invalidate_figure_cache()

        if hasattr(self, 'on_render_cache_invalidate'):
            self.on_render_cache_invalidate()

        self.show_final_results()
        if self.on_turn_ended:
            self.on_turn_ended()

    def show_final_results(self) -> None:
        """Display the final scores."""
        logger.scoring("=== FINAL SCORES ===")
        sorted_players = sorted(self.players,
                               key=lambda p: p.get_score(),
                               reverse=True)

        if sorted_players and self.on_show_notification:
            winner = sorted_players[0]
            self.on_show_notification(
                "success",
                f"Player {winner.get_name()} wins with {winner.get_score()} points!"
            )

        for i, player in enumerate(sorted_players):
            if i == 0:
                logger.scoring(
                    f"WINNER: {player.get_name()}: {player.get_score()} points")
            else:
                logger.scoring(
                    f"{player.get_name()}: {player.get_score()} points")

    def _get_board_state_hash(self) -> int:
        """Get a hash of the current board state for caching."""
        return len([(x, y) for y in range(self.game_board.get_grid_size())
                    for x in range(self.game_board.get_grid_size())
                    if self.game_board.get_card(x, y)])

    def _get_structure_cache_key(self, x: int, y: int, direction: str,
                              terrain_type: str) -> tuple:
        """Get a cache key for structure detection."""
        return (x, y, direction, terrain_type)

    def _get_validation_cache_key(self, card: typing.Any, x: int,
                               y: int) -> tuple:
        """Get a cache key for card validation."""
        return (id(card), x, y, card.rotation)

    def _update_candidate_positions(self) -> None:
        """Update the cached candidate positions based on current board state."""
        current_state = self._get_board_state_hash()
        if self._last_board_state == current_state:
            return

        self._last_board_state = current_state
        self._candidate_positions.clear()

        occupied_positions = set()
        for y in range(self.game_board.get_grid_size()):
            for x in range(self.game_board.get_grid_size()):
                if self.game_board.get_card(x, y):
                    occupied_positions.add((x, y))

        for x, y in occupied_positions:
            neighbors = self._get_neighbors_cached(x, y)
            for nx, ny in neighbors:
                if not self.game_board.get_card(nx, ny):
                    self._candidate_positions.add((nx, ny))

    def get_candidate_positions(self) -> set:
        """Get all candidate positions where a card could potentially be placed."""
        self._update_candidate_positions()
        return self._candidate_positions.copy()

    def _invalidate_candidate_cache(self) -> None:
        """Invalidate the candidate positions cache."""
        self._last_board_state = None
        self._candidate_positions.clear()

    def invalidate_candidate_cache(self) -> None:
        """Public method to invalidate the candidate positions cache."""
        self._invalidate_candidate_cache()

    def _invalidate_structure_cache(self) -> None:
        """Invalidate the structure detection cache."""
        self._structure_cache.clear()
        self._structure_cache_valid = False
        self._last_board_hash = None

    def invalidate_structure_cache(self) -> None:
        """Public method to invalidate the structure detection cache."""
        self._invalidate_structure_cache()

    def _invalidate_validation_cache(self) -> None:
        """Invalidate the card validation cache."""
        self._validation_cache.clear()
        self._validation_cache_valid = False

    def invalidate_validation_cache(self) -> None:
        """Public method to invalidate the card validation cache."""
        self._invalidate_validation_cache()

    def _get_neighbors_cached(self, x: int, y: int) -> set:
        """Get neighbor positions with caching."""
        if (x, y) in self._neighbor_cache:
            return self._neighbor_cache[(x, y)]

        neighbors = set()
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.game_board.get_grid_size()
                and 0 <= ny < self.game_board.get_grid_size()):
                neighbors.add((nx, ny))

        self._neighbor_cache[(x, y)] = neighbors
        return neighbors

    def _invalidate_neighbor_cache(self) -> None:
        """Invalidate the neighbor lookup cache."""
        self._neighbor_cache.clear()
        self._neighbor_cache_valid = False

    def invalidate_neighbor_cache(self) -> None:
        """Public method to invalidate the neighbor lookup cache."""
        self._invalidate_neighbor_cache()

    def validate_card_placement_cached(self, card: typing.Any, x: int,
                                    y: int) -> bool:
        """Validate card placement with caching."""
        if not card:
            return False

        cache_key = self._get_validation_cache_key(card, x, y)
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]

        result = self.game_board.validate_card_placement(card, x, y)

        self._validation_cache[cache_key] = result
        return result

    def get_valid_placements(self, card: typing.Any) -> set:
        """Get all valid placements for a specific card."""
        if not card:
            return set()

        candidates = self.get_candidate_positions()
        valid = set()

        original_rotation = card.rotation
        try:
            for x, y in candidates:
                for rotation in range(4):
                    if self.validate_card_placement_cached(card, x, y):
                        valid.add((x, y, card.rotation))
                    card.rotate()
        finally:
            while card.rotation != original_rotation:
                card.rotate()

        return valid

    def can_place_card_anywhere(self, card: typing.Any) -> bool:
        """Check if card can be placed anywhere on the board."""
        if not card:
            return False
        logger.debug("Checking if card can be placed anywhere on the board...")
        if self.is_first_round:
            logger.debug("First round - card can always be placed")
            return True

        valid_placements = self.get_valid_placements(card)
        logger.debug(f"Found {len(valid_placements)} valid placements")

        return len(valid_placements) > 0

    def get_random_valid_placement(self,
                                card: typing.Any) -> typing.Optional[tuple]:
        """Get a random valid placement for the given card."""
        if not card:
            return None

        valid_placements = list(self.get_valid_placements(card))
        if not valid_placements:
            return None

        x, y, rotation = random.choice(valid_placements)

        original_rotation = card.rotation
        while card.rotation != rotation:
            card.rotate()

        return (x, y, rotation)

    def serialize(self) -> dict:
        """Serialize the game session to a dictionary."""
        logger.debug("Serializing game state")
        return {
            "players": [player.serialize() for player in self.players],
            "deck": [card.serialize() for card in self.cards_deck],
            "board":
            self.game_board.serialize(),
            "current_card":
            self.current_card.serialize() if self.current_card else None,
            "last_placed_card_position":
            self.game_board.get_card_position(self.last_placed_card)
            if self.last_placed_card else None,
            "is_first_round":
            self.is_first_round,
            "turn_phase":
            self.turn_phase,
            "game_over":
            self.game_over,
            "current_player_index":
            self.current_player.get_index(),
            "placed_figures": [{
                **figure.serialize(), "card_position":
                self.game_board.get_card_position(figure.card)
            } for figure in self.placed_figures if figure.card],
            "structure_map":
            list(self.structure_map.keys()),
            "structures": [
                s.serialize() for s in self.structures
                if hasattr(s, 'serialize')
            ],
            "game_mode":
            self.game_mode,
            "lobby_completed":
            self.lobby_completed,
            "network_mode":
            self.network_mode
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'GameSession':
        """Deserialize a game session from a dictionary."""
        players = []
        for p in data.get("players", []):
            try:
                if p["name"].startswith("AI_"):
                    players.append(AIPlayer.deserialize(p))
                else:
                    players.append(Player.deserialize(p))
            except Exception as e:
                logger.warning(f"Skipping malformed player entry: {p} - {e}")
        lobby_completed = data.get("lobby_completed", True)
        network_mode = data.get("network_mode", 'local')
        session = cls([p.get_name() for p in players],
                      no_init=True,
                      lobby_completed=lobby_completed,
                      network_mode=network_mode)
        session.players = players
        try:
            session.current_player = players[int(
                data.get("current_player_index", 0))]
        except (IndexError, ValueError, TypeError) as e:
            logger.warning(
                f"Invalid current_player_index, defaulting to first: {e}")
            session.current_player = players[0] if players else None
        session.cards_deck = []
        for c in data.get("deck", []):
            try:
                session.cards_deck.append(Card.deserialize(c))
            except Exception as e:
                logger.warning(f"Skipping malformed card in deck: {c} - {e}")
        try:
            session.current_card = Card.deserialize(
                data["current_card"]) if data.get("current_card") else None
        except Exception as e:
            logger.warning(f"Failed to deserialize current_card - {e}")
            session.current_card = None
        try:
            session.game_board = GameBoard.deserialize(data.get("board", {}))
        except Exception as e:
            logger.warning(f"Failed to deserialize game_board - {e}")
            session.game_board = GameBoard()
        try:
            last_placed_card_pos = data.get("last_placed_card_position")
            if last_placed_card_pos:
                x, y = last_placed_card_pos
                session.last_placed_card = session.game_board.get_card(x, y)
            else:
                session.last_placed_card = None
        except Exception as e:
            logger.warning(
                f"Failed to deserialize last_placed_card position - {e}")
            session.last_placed_card = None
        try:
            session.is_first_round = bool(data.get("is_first_round", True))
            session.turn_phase = int(data.get("turn_phase", 1))
            session.game_over = bool(data.get("game_over", False))
        except Exception as e:
            logger.warning(f"Failed to parse basic session attributes - {e}")
        session.game_mode = data.get("game_mode", None)
        player_map = {p.get_index(): p for p in session.players}
        session.placed_figures = []
        for fdata in data.get("placed_figures", []):
            try:
                figure = Figure.deserialize(fdata, player_map,
                                            session.game_board)
                if figure:
                    session.placed_figures.append(figure)
            except Exception as e:
                logger.warning(f"Skipping malformed figure: {fdata} - {e}")
        session.structures = []
        for s in data.get("structures", []):
            try:
                structure = Structure.deserialize(s, session.game_board,
                                                  player_map,
                                                  session.placed_figures)
                if structure:
                    session.structures.append(structure)
            except Exception as e:
                logger.warning(f"Skipping malformed structure: {s} - {e}")
        session.structure_map = {}
        seen_keys = set()
        for structure in session.structures:
            for card, direction in structure.card_sides:
                pos = card.get_position()
                if pos and pos["X"] is not None and pos["Y"] is not None:
                    key = (pos["X"], pos["Y"], direction)
                    if key in seen_keys:
                        logger.warning(
                            f"Duplicate structure mapping detected during rebuild: {key}"
                        )
                    session.structure_map[key] = structure
                    seen_keys.add(key)
        fig_lookup = {
            (f.card, f.position_on_card): f
            for f in session.placed_figures
        }
        for structure in session.structures:
            updated_figures = []
            for fig in structure.get_figures():
                key = (fig.card, fig.position_on_card)
                updated_figures.append(fig_lookup.get(key, fig))
            structure.set_figures(updated_figures)
        return session
