"""Unit tests for core Carcassonne game logic.

These tests validate card placement rules, structure detection/completion,
scoring behavior (including tie handling), end-game scoring of incomplete
structures, and game state serialization/deserialization.
"""

import os
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.card import Card
from models.game_board import GameBoard
from models.game_session import GameSession
from models.player import Player
from models.structure import Structure


EDGE_TERRAINS = ["field", "road", "city"]


class DummyOwner:
    """Minimal owner stub used to validate score attribution and figure return."""

    def __init__(self, name: str, color: str = "blue"):
        """Create a dummy owner with score tracking."""
        self._name = name
        self._color = color
        self.score = 0
        self.returned = []

    def get_name(self):
        """Return owner name."""
        return self._name

    def add_score(self, score: int):
        """Accumulate owner score."""
        self.score += score

    def get_color_with_alpha(self, alpha: int = 150):
        """Return a deterministic RGBA color-like tuple."""
        return (10, 20, 30, alpha)

    def add_figure(self, figure):
        """Track figures returned to the owner."""
        self.returned.append(figure)


class DummyFigure:
    """Minimal figure stub used for scoring tests."""

    def __init__(self, owner):
        """Create a dummy figure bound to an owner."""
        self.owner = owner
        self._owner = owner
        self.card = None
        self.position_on_card = "N"
        self.removed = False

    def get_owner(self):
        """Return figure owner."""
        return self._owner

    def remove(self):
        """Mark the figure as removed from board."""
        self.removed = True


class DummyCityCard:
    """Minimal card-like object used for city coat-of-arms scoring tests."""

    def __init__(self, features=None):
        """Create dummy city card with optional features."""
        self._features = features or []

    def get_features(self):
        """Return card features."""
        return self._features


class GameLogicTests(unittest.TestCase):
    """Test suite for placement, structures, scoring, and persistence."""

    @classmethod
    def setUpClass(cls):
        """Patch pygame image loading/scaling for headless deterministic testing."""
        cls.load_patcher = patch("pygame.image.load", return_value=object())
        cls.scale_patcher = patch("pygame.transform.scale", side_effect=lambda img, size: img)
        cls.load_patcher.start()
        cls.scale_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop pygame patches created in setUpClass."""
        cls.load_patcher.stop()
        cls.scale_patcher.stop()

    def make_card(self, terrains, connections=None, features=None):
        """Create a test card with deterministic fake image path."""
        return Card("fake.png", terrains, connections or {}, features or [])

    def place_and_detect(self, session, card, x, y):
        """Place a card and run incremental structure detection."""
        session.game_board.place_card(card, x, y)
        session.last_placed_card = card
        session.detect_structures()

    def test_validate_card_placement_requires_neighbor(self):
        """Placement must fail when target cell has no occupied neighbor."""
        board = GameBoard(grid_size=5)
        card = self.make_card({"N": "field", "E": "field", "S": "field", "W": "field"})
        self.assertFalse(board.validate_card_placement(card, 2, 2))

    def test_validate_card_placement_rejects_all_mismatched_terrain_combinations(self):
        """Placement must fail for every distinct touching terrain mismatch pair."""
        for anchor_terrain in EDGE_TERRAINS:
            for candidate_terrain in EDGE_TERRAINS:
                if anchor_terrain == candidate_terrain:
                    continue
                with self.subTest(anchor=anchor_terrain, candidate=candidate_terrain):
                    board = GameBoard(grid_size=5)
                    anchor = self.make_card(
                        {"N": "field", "E": anchor_terrain, "S": "field", "W": "field"}
                    )
                    board.place_card(anchor, 2, 2)
                    candidate = self.make_card(
                        {"N": "field", "E": "field", "S": "field", "W": candidate_terrain}
                    )
                    self.assertFalse(board.validate_card_placement(candidate, 3, 2))

    def test_validate_card_placement_accepts_all_matching_terrain_combinations(self):
        """Placement must succeed for every possible touching terrain match."""
        for terrain in EDGE_TERRAINS:
            with self.subTest(terrain=terrain):
                board = GameBoard(grid_size=5)
                anchor = self.make_card(
                    {"N": "field", "E": terrain, "S": "field", "W": "field"}
                )
                board.place_card(anchor, 2, 2)
                candidate = self.make_card(
                    {"N": "field", "E": "field", "S": "field", "W": terrain}
                )
                self.assertTrue(board.validate_card_placement(candidate, 3, 2))

    def test_structure_detection_and_completion_road_edge_case(self):
        """Road remains incomplete with open end, then completes once closed."""
        session = GameSession([], no_init=True)
        board = session.game_board

        left = self.make_card(
            {"N": "field", "E": "road", "S": "field", "W": "field"},
            {"E": ["E"]},
        )
        middle = self.make_card(
            {"N": "field", "E": "road", "S": "field", "W": "road"},
            {"E": ["W"], "W": ["E"]},
        )
        right = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "road"},
            {"W": ["W"]},
        )

        board.place_card(left, 2, 2)
        session.last_placed_card = left
        session.detect_structures()

        board.place_card(middle, 3, 2)
        session.last_placed_card = middle
        session.detect_structures()

        structure = session.structure_map[(3, 2, "W")]
        structure.check_completion()
        self.assertFalse(structure.get_is_completed())

        board.place_card(right, 4, 2)
        session.last_placed_card = right
        session.detect_structures()

        structure = session.structure_map[(3, 2, "E")]
        structure.check_completion()
        self.assertTrue(structure.get_is_completed())

    def test_structure_detection_and_completion_city(self):
        """City becomes complete once all exposed city edges are connected."""
        session = GameSession([], no_init=True)

        left_city = self.make_card(
            {"N": "field", "E": "city", "S": "field", "W": "field"},
            {"E": ["E"]},
        )
        right_city = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "city"},
            {"W": ["W"]},
        )

        self.place_and_detect(session, left_city, 2, 2)
        city_structure = session.structure_map[(2, 2, "E")]
        self.assertEqual(city_structure.get_structure_type(), "City")
        city_structure.check_completion()
        self.assertFalse(city_structure.get_is_completed())

        self.place_and_detect(session, right_city, 3, 2)
        city_structure = session.structure_map[(2, 2, "E")]
        city_structure.check_completion()
        self.assertTrue(city_structure.get_is_completed())

    def test_structure_detection_and_completion_monastery_edge_case(self):
        """Monastery is incomplete with one missing neighbor and complete after final tile."""
        session = GameSession([], no_init=True)

        monastery = self.make_card(
            {
                "N": "field",
                "E": "field",
                "S": "field",
                "W": "field",
                "C": "monastery",
            },
            {
                "N": ["E", "S", "W"],
                "E": ["N", "S", "W"],
                "S": ["N", "E", "W"],
                "W": ["N", "E", "S"],
            },
        )
        self.place_and_detect(session, monastery, 2, 2)
        monastery_structure = session.structure_map[(2, 2, "C")]
        self.assertEqual(monastery_structure.get_structure_type(), "Monastery")
        monastery_structure.check_completion()
        self.assertFalse(monastery_structure.get_is_completed())

        fillers = {
            (1, 1), (2, 1), (3, 1),
            (1, 2),         (3, 2),
            (1, 3), (2, 3),
        }
        for x, y in fillers:
            self.place_and_detect(
                session,
                self.make_card({"N": "field", "E": "field", "S": "field", "W": "field"}),
                x,
                y,
            )

        monastery_structure.check_completion()
        self.assertFalse(monastery_structure.get_is_completed())

        self.place_and_detect(
            session,
            self.make_card({"N": "field", "E": "field", "S": "field", "W": "field"}),
            3,
            3,
        )
        monastery_structure.check_completion()
        self.assertTrue(monastery_structure.get_is_completed())

    def test_structure_detection_field_is_never_completed(self):
        """Field structures are detected but are never considered completed."""
        session = GameSession([], no_init=True)

        field_only = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "field"},
            {
                "N": ["E", "S", "W"],
                "E": ["N", "S", "W"],
                "S": ["N", "E", "W"],
                "W": ["N", "E", "S"],
            },
        )
        self.place_and_detect(session, field_only, 2, 2)

        field_structure = session.structure_map[(2, 2, "N")]
        self.assertEqual(field_structure.get_structure_type(), "Field")
        field_structure.check_completion()
        self.assertFalse(field_structure.get_is_completed())


    def test_structure_detection_merges_two_structures_and_keeps_figures(self):
        """Bridge placement should merge two structures and preserve both figures."""
        session = GameSession([], no_init=True)

        left = self.make_card(
            {"N": "field", "E": "road", "S": "field", "W": "field"},
            {"E": ["E"]},
        )
        right = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "road"},
            {"W": ["W"]},
        )
        bridge = self.make_card(
            {"N": "field", "E": "road", "S": "field", "W": "road"},
            {"E": ["W"], "W": ["E"]},
        )

        self.place_and_detect(session, left, 1, 2)
        self.place_and_detect(session, right, 3, 2)

        left_structure = session.structure_map[(1, 2, "E")]
        right_structure = session.structure_map[(3, 2, "W")]
        self.assertIsNot(left_structure, right_structure)

        left_figure = DummyFigure(DummyOwner("LeftOwner"))
        right_figure = DummyFigure(DummyOwner("RightOwner"))
        left_structure.set_figures([left_figure])
        right_structure.set_figures([right_figure])

        self.place_and_detect(session, bridge, 2, 2)

        merged_w = session.structure_map[(2, 2, "W")]
        merged_e = session.structure_map[(2, 2, "E")]
        self.assertIs(merged_w, merged_e)
        self.assertIs(session.structure_map[(1, 2, "E")], merged_w)
        self.assertIs(session.structure_map[(3, 2, "W")], merged_w)

        road_structures = [
            s for s in session.structures if s.get_structure_type() == "Road"
        ]
        self.assertEqual(len(road_structures), 1)
        self.assertEqual(len(merged_w.get_figures()), 2)
        self.assertCountEqual(merged_w.get_figures(), [left_figure, right_figure])

    def test_structure_detection_merges_road_and_merge_can_complete_and_score(self):
        """Merging two road fragments can complete the road and award points."""
        session = GameSession([], no_init=True)

        left_road = self.make_card(
            {"N": "field", "E": "road", "S": "field", "W": "field"},
            {"E": ["E"]},
        )
        right_road = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "road"},
            {"W": ["W"]},
        )
        bridge_road = self.make_card(
            {"N": "field", "E": "road", "S": "field", "W": "road"},
            {"E": ["W"], "W": ["E"]},
        )

        self.place_and_detect(session, left_road, 1, 2)
        self.place_and_detect(session, right_road, 3, 2)

        left_structure = session.structure_map[(1, 2, "E")]
        right_structure = session.structure_map[(3, 2, "W")]
        self.assertIsNot(left_structure, right_structure)

        owner_a = DummyOwner("RoadA")
        owner_b = DummyOwner("RoadB")
        left_structure.set_figures([DummyFigure(owner_a)])
        right_structure.set_figures([DummyFigure(owner_b)])

        self.place_and_detect(session, bridge_road, 2, 2)

        merged = session.structure_map[(2, 2, "W")]
        self.assertIs(merged, session.structure_map[(2, 2, "E")])
        self.assertIs(session.structure_map[(1, 2, "E")], merged)
        self.assertIs(session.structure_map[(3, 2, "W")], merged)

        merged.check_completion()
        self.assertTrue(merged.get_is_completed())
        session.score_structure(merged)
        self.assertEqual(owner_a.score, 3)
        self.assertEqual(owner_b.score, 3)

    def test_structure_detection_merges_city_and_merge_can_complete_and_score(self):
        """Merging two city fragments can complete the city and award points."""
        session = GameSession([], no_init=True)

        left_city = self.make_card(
            {"N": "field", "E": "city", "S": "field", "W": "field"},
            {"E": ["E"]},
        )
        right_city = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "city"},
            {"W": ["W"]},
        )
        bridge_city = self.make_card(
            {"N": "field", "E": "city", "S": "field", "W": "city"},
            {"E": ["W"], "W": ["E"]},
        )

        self.place_and_detect(session, left_city, 1, 2)
        self.place_and_detect(session, right_city, 3, 2)

        left_structure = session.structure_map[(1, 2, "E")]
        right_structure = session.structure_map[(3, 2, "W")]
        self.assertIsNot(left_structure, right_structure)

        owner_a = DummyOwner("CityA")
        owner_b = DummyOwner("CityB")
        left_structure.set_figures([DummyFigure(owner_a)])
        right_structure.set_figures([DummyFigure(owner_b)])

        self.place_and_detect(session, bridge_city, 2, 2)

        merged = session.structure_map[(2, 2, "W")]
        self.assertIs(merged, session.structure_map[(2, 2, "E")])
        self.assertIs(session.structure_map[(1, 2, "E")], merged)
        self.assertIs(session.structure_map[(3, 2, "W")], merged)

        merged.check_completion()
        self.assertTrue(merged.get_is_completed())
        session.score_structure(merged)
        self.assertEqual(owner_a.score, 6)
        self.assertEqual(owner_b.score, 6)

    def test_structure_detection_merges_field_structures(self):
        """Bridge placement should merge two field structures into one."""
        session = GameSession([], no_init=True)

        left_field = self.make_card(
            {"N": "city", "E": "field", "S": "city", "W": "city"},
            {"E": ["E"]},
        )
        right_field = self.make_card(
            {"N": "city", "E": "city", "S": "city", "W": "field"},
            {"W": ["W"]},
        )
        bridge_field = self.make_card(
            {"N": "city", "E": "field", "S": "city", "W": "field"},
            {"E": ["W"], "W": ["E"]},
        )

        self.place_and_detect(session, left_field, 1, 2)
        self.place_and_detect(session, right_field, 3, 2)

        left_structure = session.structure_map[(1, 2, "E")]
        right_structure = session.structure_map[(3, 2, "W")]
        self.assertIsNot(left_structure, right_structure)
        self.assertEqual(left_structure.get_structure_type(), "Field")
        self.assertEqual(right_structure.get_structure_type(), "Field")

        self.place_and_detect(session, bridge_field, 2, 2)
        merged = session.structure_map[(2, 2, "W")]

        self.assertIs(merged, session.structure_map[(2, 2, "E")])
        self.assertIs(session.structure_map[(1, 2, "E")], merged)
        self.assertIs(session.structure_map[(3, 2, "W")], merged)

        field_structures = [
            s for s in session.structures if s.get_structure_type() == "Field"
        ]
        self.assertEqual(len(field_structures), 1)

    def test_monastery_structures_stay_independent_when_adjacent(self):
        """Monasteries are center-only structures and should not merge with neighbors."""
        session = GameSession([], no_init=True)

        monastery_a = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "field", "C": "monastery"},
            {},
        )
        monastery_b = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "field", "C": "monastery"},
            {},
        )

        self.place_and_detect(session, monastery_a, 1, 2)
        self.place_and_detect(session, monastery_b, 2, 2)

        structure_a = session.structure_map[(1, 2, "C")]
        structure_b = session.structure_map[(2, 2, "C")]
        self.assertIsNot(structure_a, structure_b)

    def test_play_figure_only_allowed_on_last_placed_card(self):
        """Meeple placement must be rejected on any card except the last placed one."""
        session = GameSession([], no_init=True)
        player = Player("Alice", "blue", 0)
        session.players = [player]

        older = self.make_card({"N": "field", "E": "field", "S": "field", "W": "field"})
        newer = self.make_card({"N": "field", "E": "field", "S": "field", "W": "field"})

        self.place_and_detect(session, older, 1, 2)
        self.place_and_detect(session, newer, 2, 2)

        figures_before = len(player.get_figures())
        self.assertFalse(session.play_figure(player, 1, 2, "N"))
        self.assertEqual(len(player.get_figures()), figures_before)
        self.assertEqual(len(session.get_placed_figures()), 0)

    def test_play_figure_rejects_already_claimed_connected_terrain(self):
        """Meeple placement is rejected when the target structure is already claimed."""
        session = GameSession([], no_init=True)
        player_a = Player("Alice", "blue", 0)
        player_b = Player("Bob", "red", 1)
        session.players = [player_a, player_b]

        claimed_card = self.make_card(
            {"N": "field", "E": "field", "S": "field", "W": "field"},
            {"N": ["E", "S", "W"], "E": ["N", "S", "W"], "S": ["N", "E", "W"], "W": ["N", "E", "S"]},
        )
        self.place_and_detect(session, claimed_card, 2, 2)

        self.assertTrue(session.play_figure(player_a, 2, 2, "N"))

        figures_before_b = len(player_b.get_figures())
        self.assertFalse(session.play_figure(player_b, 2, 2, "E"))
        self.assertEqual(len(player_b.get_figures()), figures_before_b)
        self.assertEqual(len(session.get_placed_figures()), 1)

    def test_structure_detection_connects_corner_fields_via_orthogonal_neighbors(self):
        """Optional corner sides (NE/SW/etc.) connect through legal orthogonal neighbors."""
        session = GameSession([], no_init=True)

        origin = self.make_card(
            {
                "N": "city",
                "E": "city",
                "S": "city",
                "W": "city",
                "NE": "field",
            },
            {"NE": ["NE"]},
        )
        north_neighbor = self.make_card(
            {
                "N": "city",
                "E": "city",
                "S": "city",
                "W": "city",
                "SE": "field",
            },
            {"SE": ["SE"]},
        )
        east_neighbor = self.make_card(
            {
                "N": "city",
                "E": "city",
                "S": "city",
                "W": "city",
                "NW": "field",
            },
            {"NW": ["NW"]},
        )

        # Place neighbors in legal positions (N and E), not diagonally.
        self.place_and_detect(session, origin, 2, 2)
        origin_structure = session.structure_map[(2, 2, "NE")]

        self.place_and_detect(session, north_neighbor, 2, 1)
        north_structure = session.structure_map[(2, 1, "SE")]
        self.assertIs(origin_structure, north_structure)

        self.place_and_detect(session, east_neighbor, 3, 2)
        east_structure = session.structure_map[(3, 2, "NW")]
        self.assertIs(origin_structure, east_structure)

    def test_score_structure_city_completed_includes_coat_of_arms_bonus(self):
        """Completed city scoring should include coat-of-arms bonus points."""
        session = GameSession([], no_init=True)
        structure = Structure("City")
        structure.cards = [DummyCityCard(["coat"]), DummyCityCard([])]
        structure.is_completed = True

        owner = DummyOwner("CityScorer")
        structure.set_figures([DummyFigure(owner)])

        session.score_structure(structure)

        self.assertEqual(owner.score, 6)

    def test_score_structure_awards_all_majority_owners_on_tie(self):
        """When meeple majority ties, each tied owner receives full points."""
        session = GameSession([], no_init=True)
        structure = Structure("Road")
        structure.cards = [object(), object(), object()]
        structure.is_completed = True

        owner_a = DummyOwner("A")
        owner_b = DummyOwner("B")
        fig_a = DummyFigure(owner_a)
        fig_b = DummyFigure(owner_b)
        structure.set_figures([fig_a, fig_b])

        session.score_structure(structure)

        self.assertEqual(owner_a.score, 3)
        self.assertEqual(owner_b.score, 3)
        self.assertTrue(fig_a.removed)
        self.assertTrue(fig_b.removed)

    def test_end_game_scores_incomplete_structures(self):
        """End game should score incomplete structures using game-over scoring rules."""
        session = GameSession([], no_init=True)
        structure = Structure("City")
        structure.cards = [DummyCityCard(["coat"]), DummyCityCard([])]
        structure.is_completed = False

        owner = DummyOwner("Solo")
        figure = DummyFigure(owner)
        structure.set_figures([figure])

        session.structures = [structure]
        session.placed_figures = [figure]

        session.end_game()

        self.assertTrue(session.get_game_over())
        self.assertEqual(owner.score, 3)
        self.assertEqual(session.placed_figures, [])

    def test_game_session_serialization_deserialization_round_trip(self):
        """Serialized session should deserialize with equivalent core state (network-safe)."""
        session = GameSession([], no_init=True, lobby_completed=False, network_mode="remote")
        session.players = [Player("Alice", "blue", 0)]
        session.current_player = session.players[0]
        session.game_mode = "multiplayer"

        card = self.make_card({"N": "field", "E": "field", "S": "field", "W": "field"})
        session.game_board.place_card(card, 5, 5)
        session.last_placed_card = card

        payload = session.serialize()
        restored = GameSession.deserialize(payload)

        self.assertEqual(len(restored.players), 1)
        self.assertEqual(restored.players[0].get_name(), "Alice")
        self.assertIsNotNone(restored.game_board.get_card(5, 5))
        self.assertEqual(restored.network_mode, "remote")
        self.assertFalse(restored.lobby_completed)


if __name__ == "__main__":
    unittest.main()
