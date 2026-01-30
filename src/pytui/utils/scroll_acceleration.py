# pytui.utils.scroll_acceleration - 滚动加速度曲线，供 Scrollbox 等使用

from __future__ import annotations

import time
from typing import Protocol


class ScrollAcceleration(Protocol):
    """滚动加速度协议：根据连续滚动 tick 返回本步应滚动的倍数。"""

    def tick(self, now: float | None = None) -> float:
        """记录一次滚动 tick，返回本步的乘数（>=1）。now 为当前时间（秒），默认 time.time()。"""
        ...

    def reset(self) -> None:
        """重置内部状态（如连续 tick 计数、时间窗口）。"""
        ...


class LinearScrollAccel:
    """线性滚动：每次 tick 返回 1，无加速。"""

    def tick(self, now: float | None = None) -> float:
        return 1.0

    def reset(self) -> None:
        pass


class MacOSScrollAccel:
    """类 macOS 滚动加速度：根据连续 tick 的时间间隔计算乘数，快速连续滚动时加速。"""

    def __init__(
        self,
        *,
        threshold1: float = 80.0,
        threshold2: float = 40.0,
        multiplier1: float = 2.0,
        multiplier2: float = 4.0,
        streak_timeout_ms: float = 150.0,
        min_interval_ms: float = 6.0,
    ) -> None:
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.multiplier1 = multiplier1
        self.multiplier2 = multiplier2
        self.streak_timeout_ms = streak_timeout_ms
        self.min_interval_ms = min_interval_ms
        self._last_tick_time: float = 0.0
        self._intervals: list[float] = []
        self._history_size = 3

    def tick(self, now: float | None = None) -> float:
        if now is None:
            now = time.time()
        t_ms = now * 1000.0
        if self._last_tick_time == 0:
            self._last_tick_time = t_ms
            return 1.0
        dt_ms = t_ms - self._last_tick_time
        if dt_ms > self.streak_timeout_ms:
            self._last_tick_time = t_ms
            self._intervals = []
            return 1.0
        if dt_ms < self.min_interval_ms:
            return 1.0
        self._last_tick_time = t_ms
        self._intervals.append(dt_ms)
        if len(self._intervals) > self._history_size:
            self._intervals.pop(0)
        avg = sum(self._intervals) / len(self._intervals)
        if avg <= self.threshold2:
            return self.multiplier2
        if avg <= self.threshold1:
            return self.multiplier1
        return 1.0

    def reset(self) -> None:
        self._last_tick_time = 0.0
        self._intervals = []
