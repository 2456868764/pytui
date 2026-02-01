# pytui.lib.scroll_acceleration - Aligns with OpenTUI lib/scroll-acceleration.ts
# ScrollAcceleration protocol, LinearScrollAccel, MacOSScrollAccel (A, tau, maxMultiplier).

from __future__ import annotations

import math
import time
from typing import Protocol


class ScrollAcceleration(Protocol):
    """Protocol: tick(now?) -> multiplier, reset(). Aligns with OpenTUI ScrollAcceleration."""

    def tick(self, now: float | None = None) -> float:
        """Record a scroll tick; return multiplier (>=1). now in ms; default time.time()*1000."""
        ...

    def reset(self) -> None:
        """Reset internal state."""
        ...


class LinearScrollAccel:
    """Linear: tick always returns 1. Aligns with OpenTUI LinearScrollAccel."""

    def tick(self, now: float | None = None) -> float:
        return 1.0

    def reset(self) -> None:
        pass


class MacOSScrollAccel:
    """macOS-inspired scroll acceleration. Aligns with OpenTUI MacOSScrollAccel (A, tau, maxMultiplier)."""

    _history_size = 3
    _streak_timeout = 150  # ms
    _min_tick_interval = 6  # ms
    _reference_interval = 100  # ms

    def __init__(
        self,
        *,
        A: float = 0.8,
        tau: float = 3.0,
        max_multiplier: float = 6.0,
    ) -> None:
        self._A = A
        self._tau = tau
        self._max_multiplier = max_multiplier
        self._last_tick_time: float = 0.0
        self._velocity_history: list[float] = []  # per-instance

    def tick(self, now: float | None = None) -> float:
        if now is None:
            now = time.time() * 1000.0  # ms
        dt = (now - self._last_tick_time) if self._last_tick_time else float("inf")

        if dt == float("inf") or dt > self._streak_timeout:
            self._last_tick_time = now
            self._velocity_history = []
            return 1.0

        if dt < self._min_tick_interval:
            return 1.0

        self._last_tick_time = now
        self._velocity_history.append(dt)
        if len(self._velocity_history) > self._history_size:
            self._velocity_history.pop(0)

        avg_interval = sum(self._velocity_history) / len(self._velocity_history)
        velocity = self._reference_interval / avg_interval
        x = velocity / self._tau
        multiplier = 1.0 + self._A * (math.exp(x) - 1.0)
        return min(multiplier, self._max_multiplier)

    def reset(self) -> None:
        self._last_tick_time = 0.0
        self._velocity_history = []
