"""Background AI worker service for turn-based move computation.

The worker accepts immutable turn snapshots and computes one move in a
single daemon thread.
"""

from __future__ import annotations

import copy
import queue
import threading
from typing import Any, Dict, Optional


class AIWorkerService:
    """Single-threaded asynchronous service for AI move computation.

    Input queue item shape:
        {"turn_id": Any, "ai_player": Any, "snapshot": Any}

    Output queue item shape:
        {"turn_id": Any, "result_move": Any}
        or
        {"turn_id": Any, "error": {"type": str, "message": str}}
    """

    _STOP_SENTINEL = object()

    def __init__(self) -> None:
        # Keep a tiny bounded queue so overloaded submissions can fail fast.
        self._input_queue: "queue.Queue[Any]" = queue.Queue(maxsize=1)
        self._output_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self._state_lock = threading.Lock()
        self._is_busy = False
        self._pending_turn_id: Optional[Any] = None

    def start(self) -> None:
        """Start the daemon worker thread if it is not already running."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._worker_loop,
            name="AIWorkerService",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 1.0) -> None:
        """Stop the worker thread and wait up to ``timeout`` seconds."""
        self._stop_event.set()

        # Wake the thread if it's blocked on queue.get.
        try:
            self._input_queue.put_nowait(self._STOP_SENTINEL)
        except queue.Full:
            # Worker will still observe ``_stop_event`` and exit shortly.
            pass

        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

        with self._state_lock:
            self._is_busy = False
            self._pending_turn_id = None

    def submit(self, turn_id: Any, ai_player: Any, snapshot: Any) -> bool:
        """Submit one turn for processing.

        Returns ``False`` if the worker is not running or currently busy.
        """
        if not (self._thread and self._thread.is_alive()):
            return False

        with self._state_lock:
            if self._is_busy:
                return False
            self._is_busy = True
            self._pending_turn_id = turn_id

        request = {
            "turn_id": turn_id,
            "ai_player": ai_player,
            # Defensive copy keeps each request isolated and stateless.
            "snapshot": copy.deepcopy(snapshot),
        }
        try:
            self._input_queue.put_nowait(request)
        except queue.Full:
            with self._state_lock:
                if self._pending_turn_id == turn_id:
                    self._is_busy = False
                    self._pending_turn_id = None
            return False
        return True

    def poll_result(self, turn_id: Any) -> Optional[Any]:
        """Return result for ``turn_id`` if available; otherwise ``None``.

        Stale results (turn_id mismatch) are ignored/discarded.
        """
        while True:
            try:
                item = self._output_queue.get_nowait()
            except queue.Empty:
                return None

            if item.get("turn_id") != turn_id:
                # Guardrail: stale/out-of-order result, discard silently.
                continue

            if "error" in item:
                return {"error": item["error"]}
            return item.get("result_move")

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                item = self._input_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if item is self._STOP_SENTINEL:
                break

            turn_id = item.get("turn_id")
            ai_player = item.get("ai_player")
            snapshot = item.get("snapshot")

            try:
                result_move = self._compute_best_move(ai_player, snapshot)
                payload: Dict[str, Any] = {
                    "turn_id": turn_id,
                    "result_move": result_move,
                }
            except Exception as exc:  # Guardrail: never crash worker thread.
                payload = {
                    "turn_id": turn_id,
                    "error": {
                        "type": exc.__class__.__name__,
                        "message": str(exc),
                    },
                }

            self._output_queue.put(payload)

            with self._state_lock:
                if self._pending_turn_id == turn_id:
                    self._is_busy = False
                    self._pending_turn_id = None

    @staticmethod
    def _compute_best_move(ai_player: Any, snapshot: Any) -> Any:
        """Compute the best move from a snapshot without GameSession mutation."""
        if callable(ai_player):
            return ai_player(snapshot)

        method = getattr(ai_player, "compute_move_from_snapshot", None)
        if callable(method):
            return method(snapshot)

        raise AttributeError(
            "ai_player must be callable or expose "
            "compute_move_from_snapshot(snapshot)"
        )
