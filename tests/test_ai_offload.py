"""Focused tests for AI offload worker/session integration behavior."""

import os
import sys
from unittest.mock import Mock

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.ai_player import AIPlayer
from models.ai_worker import AIWorkerService
from models.card import Card
from models.game_session import GameSession
from models.player import Player
from ui.game_scene import GameScene


@pytest.fixture(autouse=True)
def patch_pygame_image_ops(monkeypatch):
    """Keep tests headless and deterministic."""
    monkeypatch.setattr("pygame.image.load", lambda *_args, **_kwargs: object())
    monkeypatch.setattr("pygame.transform.scale", lambda image, _size: image)


def _make_card(terrains):
    return Card("fake.png", terrains, {}, [])


def _build_session_for_phase_one(current_player):
    session = GameSession([], no_init=True)
    other = Player("Other", "red", 1)
    session.players = [current_player, other]
    session.current_player = current_player
    session.is_first_round = False
    session.turn_phase = 1

    center_x, center_y = session.game_board.get_center_position()
    anchor = _make_card({"N": "field", "E": "field", "S": "field", "W": "field"})
    session.game_board.place_card(anchor, center_x, center_y)

    session.current_card = _make_card({"N": "field", "E": "field", "S": "field", "W": "field"})
    session.cards_deck = [_make_card({"N": "field", "E": "field", "S": "field", "W": "field"})]
    return session, (center_x + 1, center_y)


def test_worker_returns_decision_for_valid_snapshot():
    ai_worker = AIWorkerService()
    ai_worker.start()
    try:
        ai_decider = lambda snapshot: {
            "x": snapshot["valid_placements"][0]["x"],
            "y": snapshot["valid_placements"][0]["y"],
            "rotation": snapshot["valid_placements"][0]["rotation"],
            "skip_figure": True,
        }

        ai_player = AIPlayer("AI_Test", 0, "blue")
        session, _ = _build_session_for_phase_one(ai_player)
        session.get_valid_placements = lambda _card: {(1, 2, 0)}
        session.get_candidate_positions = lambda: {(0, 0)}
        snapshot = session.build_ai_snapshot(ai_player.get_index())

        assert ai_worker.submit("turn-1", ai_decider, snapshot)

        result = None
        import time
        for _ in range(50):
            result = ai_worker.poll_result("turn-1")
            if result is not None:
                break
            time.sleep(0.01)

        assert isinstance(result, dict)
        assert {"x", "y", "rotation"}.issubset(result)
    finally:
        ai_worker.stop()


def test_apply_ai_decision_mutates_only_on_main_thread_api():
    ai_player = AIPlayer("AI_MainThread", 0, "blue")
    session, expected = _build_session_for_phase_one(ai_player)

    decision = {
        "x": expected[0],
        "y": expected[1],
        "rotation": 0,
        "current_card_signature": session._build_card_signature(session.current_card),
    }

    assert session.apply_ai_decision(ai_player.get_index(), decision) is True
    assert session.game_board.get_card(*expected) is session.last_placed_card
    assert session.current_player.get_index() == 1
    assert session.turn_phase == 1


def test_stale_result_is_ignored():
    scene = GameScene.__new__(GameScene)
    scene._pending_ai_turn_id = "turn-live"
    scene._pending_ai_player_index = 0
    scene._pending_ai_started_at = None
    scene._ai_worker_timeout_seconds = 5.0
    scene._ai_offload_enabled = True
    scene.clock = Mock()

    worker = AIWorkerService()
    worker._output_queue.put({"turn_id": "turn-stale", "result_move": {"x": 99, "y": 99}})
    scene._ai_worker = worker

    player = Mock()
    player.get_index.return_value = 0
    player.get_is_ai.return_value = True
    player.is_thinking.return_value = False
    player.get_name.return_value = "AI"

    session = Mock()
    session.get_game_over.return_value = False
    session.get_current_player.return_value = player
    session.get_is_first_round.return_value = False
    session.get_current_card.return_value = object()
    session.apply_ai_decision = Mock()
    scene.session = session

    scene.update()

    session.apply_ai_decision.assert_not_called()
    player.play_turn.assert_not_called()


def test_invalid_decision_is_rejected_safely():
    human_like_player = Player("HumanLike", "blue", 0)
    session, valid_spot = _build_session_for_phase_one(human_like_player)

    result = session.apply_ai_decision(
        human_like_player.get_index(),
        {
            "x": valid_spot[0] + 10,
            "y": valid_spot[1] + 10,
            "rotation": 0,
            "current_card_signature": session._build_card_signature(session.current_card),
        },
    )

    assert result is False
    assert session.game_board.get_card(*valid_spot) is None


def test_feature_flag_off_uses_legacy_path():
    scene = GameScene.__new__(GameScene)
    scene._ai_offload_enabled = False
    scene._pending_ai_turn_id = None
    scene._pending_ai_player_index = None
    scene._pending_ai_started_at = None
    scene.clock = Mock()

    player = Mock()
    player.get_is_ai.return_value = True
    player.is_thinking.return_value = False
    player.get_name.return_value = "AI"

    session = Mock()
    session.get_game_over.return_value = False
    session.get_current_player.return_value = player
    session.get_is_first_round.return_value = False
    session.get_current_card.return_value = object()
    scene.session = session
    scene._ai_worker = Mock()

    scene.update()

    player.play_turn.assert_called_once_with(session)


def test_worker_error_triggers_fallback():
    scene = GameScene.__new__(GameScene)
    scene._pending_ai_turn_id = "turn-err"
    scene._pending_ai_player_index = 0
    scene._pending_ai_started_at = None
    scene._ai_worker_timeout_seconds = 5.0
    scene._ai_offload_enabled = True
    scene.clock = Mock()

    worker = Mock()
    worker.poll_result.return_value = {
        "error": {"type": "RuntimeError", "message": "boom"}
    }
    scene._ai_worker = worker

    player = Mock()
    player.get_index.return_value = 0
    player.get_is_ai.return_value = True
    player.is_thinking.return_value = False
    player.get_name.return_value = "AI"

    session = Mock()
    session.get_game_over.return_value = False
    session.get_current_player.return_value = player
    session.get_is_first_round.return_value = False
    session.get_current_card.return_value = object()
    session.apply_ai_decision = Mock()
    scene.session = session

    scene.update()

    player.play_turn.assert_called_once_with(session)
    session.apply_ai_decision.assert_not_called()
