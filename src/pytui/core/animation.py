# pytui.core.animation - 简易时间轴：tick、回调或驱动 state


from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class Timeline:
    """简易时间轴：可 tick(dt) 或按帧驱动，回调在每 tick 时执行。与 renderer frame 事件解耦，可独立使用。"""

    def __init__(self) -> None:
        self._start_time: float = 0.0
        self._paused_at: float | None = None  # 暂停时的 elapsed，None 表示未暂停
        self._callbacks: list[Callable[[float], None]] = []
        self._running = False

    def start(self) -> None:
        """开始计时。"""
        self._start_time = time.time()
        self._paused_at = None
        self._running = True

    def stop(self) -> None:
        self._running = False

    def pause(self) -> None:
        if self._paused_at is not None:
            return
        self._paused_at = self.elapsed

    def resume(self) -> None:
        if self._paused_at is None:
            return
        self._start_time = time.time() - self._paused_at
        self._paused_at = None

    @property
    def elapsed(self) -> float:
        """当前已过秒数（暂停时返回暂停时的 elapsed）。"""
        if self._paused_at is not None:
            return self._paused_at
        if not self._running:
            return 0.0
        return time.time() - self._start_time

    def on_tick(self, callback: Callable[[float], None]) -> None:
        """注册每 tick 调用的回调，参数为 elapsed。"""
        self._callbacks.append(callback)

    def remove_tick(self, callback: Callable[[float], None]) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def tick(self) -> None:
        """执行一次 tick：用当前 elapsed 调用所有回调。"""
        e = self.elapsed
        for cb in self._callbacks:
            cb(e)
