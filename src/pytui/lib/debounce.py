# pytui.lib.debounce - Aligns with OpenTUI lib/debounce.ts
# Module-level map: scopeId -> (debounceId -> timer_id). DebounceController per scope.

import threading
from concurrent.futures import Future
from typing import Callable, TypeVar

R = TypeVar("R")

_TIMERS_MAP: dict[str | int, dict[str | int, threading.Timer]] = {}
_TIMERS_LOCK = threading.Lock()


class DebounceController:
    """Manages debounce timers for a specific scope. Aligns with OpenTUI DebounceController."""

    def __init__(self, scope_id: str | int) -> None:
        self._scope_id = scope_id
        with _TIMERS_LOCK:
            if scope_id not in _TIMERS_MAP:
                _TIMERS_MAP[scope_id] = {}

    def debounce(self, id: str | int, ms: float, fn: Callable[[], R]) -> Future[R]:
        """
        Schedules fn() to run after ms; any existing timer for this id is cleared.
        Returns a Future that completes with the result of fn(). Aligns with OpenTUI debounce().
        """
        scope_map = _TIMERS_MAP[self._scope_id]
        future: Future[R] = Future()

        def run_and_set() -> None:
            with _TIMERS_LOCK:
                if self._scope_id in _TIMERS_MAP and id in _TIMERS_MAP[self._scope_id]:
                    del _TIMERS_MAP[self._scope_id][id]
            try:
                result = fn()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

        with _TIMERS_LOCK:
            if id in scope_map:
                scope_map[id].cancel()
            timer = threading.Timer(ms / 1000.0, run_and_set)
            scope_map[id] = timer
        timer.start()
        return future

    def clear_debounce(self, id: str | int) -> None:
        """Clear a specific debounce timer in this scope. Aligns with OpenTUI clearDebounce()."""
        with _TIMERS_LOCK:
            scope_map = _TIMERS_MAP.get(self._scope_id)
            if scope_map and id in scope_map:
                scope_map[id].cancel()
                del scope_map[id]

    def clear(self) -> None:
        """Clear all debounce timers in this scope. Aligns with OpenTUI clear()."""
        with _TIMERS_LOCK:
            scope_map = _TIMERS_MAP.get(self._scope_id)
            if scope_map:
                for t in scope_map.values():
                    t.cancel()
                scope_map.clear()


def create_debounce(scope_id: str | int) -> DebounceController:
    """Creates a DebounceController for the given scope. Aligns with OpenTUI createDebounce()."""
    return DebounceController(scope_id)


def clear_debounce_scope(scope_id: str | int) -> None:
    """Clears all debounce timers for the given scope. Aligns with OpenTUI clearDebounceScope()."""
    with _TIMERS_LOCK:
        scope_map = _TIMERS_MAP.get(scope_id)
        if scope_map:
            for t in scope_map.values():
                t.cancel()
            scope_map.clear()


def clear_all_debounces() -> None:
    """Clears all active debounce timers across all scopes. Aligns with OpenTUI clearAllDebounces()."""
    with _TIMERS_LOCK:
        for scope_map in _TIMERS_MAP.values():
            for t in scope_map.values():
                t.cancel()
            scope_map.clear()
        _TIMERS_MAP.clear()
