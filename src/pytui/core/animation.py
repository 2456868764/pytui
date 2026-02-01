# pytui.core.animation - fully aligned with OpenTUI animation/Timeline.ts:
# TimelineOptions, AnimationOptions, JSAnimation, EasingFunctions, Timeline (add, once, call, sync,
# play, pause, restart, resetItems, update), TimelineEngine (register, unregister, clear, update),
# createTimeline.

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

# Align with OpenTUI EasingFunctions
EasingFunctions = Literal[
    "linear", "inQuad", "outQuad", "inOutQuad", "inExpo", "outExpo", "inOutSine",
    "outBounce", "outElastic", "inBounce", "inCirc", "outCirc", "inOutCirc",
    "inBack", "outBack", "inOutBack",
]


def _ease_linear(t: float) -> float:
    return t


def _ease_in_quad(t: float) -> float:
    return t * t


def _ease_out_quad(t: float) -> float:
    return t * (2 - t)


def _ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t


def _ease_in_expo(t: float) -> float:
    return 0 if t == 0 else math.pow(2, 10 * (t - 1))


def _ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - math.pow(2, -10 * t)


def _ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def _ease_out_bounce(t: float) -> float:
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def _ease_out_elastic(t: float) -> float:
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    if t == 1:
        return 1
    return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def _ease_in_bounce(t: float) -> float:
    return 1 - _ease_out_bounce(1 - t)


def _ease_in_circ(t: float) -> float:
    return 1 - math.sqrt(1 - t * t)


def _ease_out_circ(t: float) -> float:
    return math.sqrt(1 - math.pow(t - 1, 2))


def _ease_in_out_circ(t: float) -> float:
    if (t := t * 2) < 1:
        return -0.5 * (math.sqrt(1 - t * t) - 1)
    t -= 2
    return 0.5 * (math.sqrt(1 - t * t) + 1)


def _ease_in_back(t: float, s: float = 1.70158) -> float:
    return t * t * ((s + 1) * t - s)


def _ease_out_back(t: float, s: float = 1.70158) -> float:
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def _ease_in_out_back(t: float, s: float = 1.70158) -> float:
    s *= 1.525
    if (t := t * 2) < 1:
        return 0.5 * (t * t * ((s + 1) * t - s))
    t -= 2
    return 0.5 * (t * t * ((s + 1) * t + s) + 2)


EASING_FUNCTIONS: dict[str, Callable[[float], float]] = {
    "linear": _ease_linear,
    "inQuad": _ease_in_quad,
    "outQuad": _ease_out_quad,
    "inOutQuad": _ease_in_out_quad,
    "inExpo": _ease_in_expo,
    "outExpo": _ease_out_expo,
    "inOutSine": _ease_in_out_sine,
    "outBounce": _ease_out_bounce,
    "outElastic": _ease_out_elastic,
    "inBounce": _ease_in_bounce,
    "inCirc": _ease_in_circ,
    "outCirc": _ease_out_circ,
    "inOutCirc": _ease_in_out_circ,
    "inBack": _ease_in_back,
    "outBack": _ease_out_back,
    "inOutBack": _ease_in_out_back,
}


# Align with OpenTUI JSAnimation
@dataclass
class JSAnimation:
    targets: list[Any]
    delta_time: float
    progress: float
    current_time: float


# Align with OpenTUI TimelineOptions
class TimelineOptions:
    duration: float = 1000.0
    loop: bool = False
    autoplay: bool = True
    on_complete: Callable[[], None] | None = None
    on_pause: Callable[[], None] | None = None


# Align with OpenTUI AnimationOptions (for add/once)
AnimationOptions = dict[str, Any]  # duration, ease, onUpdate, onComplete, onStart, onLoop, loop, loopDelay, alternate, once, + numeric keys


def _get_prop(target: Any, key: str) -> Any:
    if isinstance(target, dict):
        return target.get(key)
    return getattr(target, key, None)


def _set_prop(target: Any, key: str, value: float) -> None:
    if isinstance(target, dict):
        target[key] = value
    else:
        setattr(target, key, value)


def _capture_initial_values(item: dict) -> None:
    if not item.get("properties"):
        return
    if item.get("initial_values"):
        return
    initial_values: list[dict[str, float]] = []
    target_list = item["target"]
    props = item["properties"]
    for i in range(len(target_list)):
        target = target_list[i]
        target_initial: dict[str, float] = {}
        for key in props:
            val = _get_prop(target, key)
            if isinstance(val, (int, float)):
                target_initial[key] = float(val)
        initial_values.append(target_initial)
    item["initial_values"] = initial_values


def _apply_animation_at_progress(
    item: dict,
    progress: float,
    reversed: bool,
    timeline_time: float,
    delta_time: float = 0.0,
) -> None:
    props = item.get("properties")
    initial_values = item.get("initial_values")
    if not props or not initial_values:
        return
    ease_name = item.get("ease", "linear")
    easing_fn = EASING_FUNCTIONS.get(ease_name, _ease_linear)
    eased = easing_fn(max(0.0, min(1.0, progress)))
    final_progress = 1 - eased if reversed else eased
    target_list = item["target"]
    for i in range(len(target_list)):
        target = target_list[i]
        initial = initial_values[i] if i < len(initial_values) else {}
        for key, end_value in props.items():
            start_value = initial.get(key, end_value)
            new_value = start_value + (end_value - start_value) * final_progress
            _set_prop(target, key, new_value)
    on_update = item.get("on_update")
    if on_update:
        anim = JSAnimation(
            targets=target_list,
            delta_time=delta_time,
            progress=eased,
            current_time=timeline_time,
        )
        on_update(anim)


def _evaluate_animation(item: dict, timeline_time: float, delta_time: float = 0.0) -> None:
    if timeline_time < item["start_time"]:
        return
    animation_time = timeline_time - item["start_time"]
    duration = item.get("duration", 0) or 0
    if timeline_time >= item["start_time"] and not item.get("started"):
        _capture_initial_values(item)
        on_start = item.get("on_start")
        if on_start:
            on_start()
        item["started"] = True
    if duration == 0:
        if not item.get("completed"):
            _apply_animation_at_progress(item, 1.0, False, timeline_time, delta_time)
            on_complete = item.get("on_complete")
            if on_complete:
                on_complete()
            item["completed"] = True
        return
    max_loops: float = 1
    if item.get("loop"):
        loop_val = item["loop"]
        max_loops = float(loop_val) if isinstance(loop_val, (int, float)) else float("inf")
    loop_delay = item.get("loop_delay", 0) or 0
    cycle_time = duration + loop_delay
    current_cycle = int(animation_time // cycle_time)
    time_in_cycle = animation_time % cycle_time
    on_loop = item.get("on_loop")
    prev_loop = item.get("current_loop", 0)
    if on_loop and prev_loop is not None and current_cycle > prev_loop and current_cycle < max_loops:
        on_loop()
    item["current_loop"] = current_cycle
    if item.get("on_complete") and not item.get("completed") and current_cycle == max_loops - 1 and time_in_cycle >= duration:
        final_reversed = (item.get("alternate") or False) and current_cycle % 2 == 1
        _apply_animation_at_progress(item, 1.0, final_reversed, timeline_time, delta_time)
        item["on_complete"]()
        item["completed"] = True
        return
    if current_cycle >= max_loops:
        if not item.get("completed"):
            final_reversed = (item.get("alternate") or False) and (max_loops - 1) % 2 == 1
            _apply_animation_at_progress(item, 1.0, final_reversed, timeline_time, delta_time)
            on_complete = item.get("on_complete")
            if on_complete:
                on_complete()
            item["completed"] = True
        return
    if time_in_cycle == 0 and animation_time > 0 and current_cycle < max_loops:
        current_cycle -= 1
        time_in_cycle = cycle_time
    if time_in_cycle >= duration:
        is_reversed = (item.get("alternate") or False) and current_cycle % 2 == 1
        _apply_animation_at_progress(item, 1.0, is_reversed, timeline_time, delta_time)
        return
    progress = time_in_cycle / duration
    is_reversed = (item.get("alternate") or False) and current_cycle % 2 == 1
    _apply_animation_at_progress(item, progress, is_reversed, timeline_time, delta_time)


def _evaluate_callback(item: dict, timeline_time: float) -> None:
    if not item.get("executed") and timeline_time >= item["start_time"] and item.get("callback"):
        item["callback"]()
        item["executed"] = True


def _evaluate_timeline_sync(item: dict, timeline_time: float, delta_time: float = 0.0) -> None:
    sub = item.get("timeline")
    if not sub:
        return
    if timeline_time < item["start_time"]:
        return
    if not item.get("timeline_started"):
        item["timeline_started"] = True
        sub.play()
        overshoot = timeline_time - item["start_time"]
        sub.update(overshoot)
        return
    sub.update(delta_time)


def _evaluate_item(item: dict, timeline_time: float, delta_time: float = 0.0) -> None:
    if item.get("type") == "animation":
        _evaluate_animation(item, timeline_time, delta_time)
    elif item.get("type") == "callback":
        _evaluate_callback(item, timeline_time)


class Timeline:
    """Fully aligned with OpenTUI Timeline: items, sub_timelines, add, once, call, sync,
    play, pause, restart, reset_items, update, state change listeners."""

    RESERVED_KEYS = frozenset({
        "duration", "ease", "onUpdate", "onComplete", "onStart", "onLoop",
        "loop", "loopDelay", "alternate", "once", "on_update", "on_complete",
        "on_start", "on_loop", "loop_delay",
    })

    def __init__(self, options: dict[str, Any] | TimelineOptions | None = None) -> None:
        opts = options or {}
        if isinstance(opts, TimelineOptions):
            opts = {
                "duration": opts.duration,
                "loop": opts.loop,
                "autoplay": opts.autoplay,
                "on_complete": opts.on_complete,
                "on_pause": opts.on_pause,
            }
        self.duration: float = float(opts.get("duration", 1000))
        self.loop: bool = opts.get("loop", False)
        self.autoplay: bool = opts.get("autoplay", True) is not False
        self._on_complete: Callable[[], None] | None = opts.get("on_complete", opts.get("onComplete"))
        self._on_pause: Callable[[], None] | None = opts.get("on_pause", opts.get("onPause"))
        self.current_time: float = 0.0
        self.is_playing: bool = False
        self.is_complete: bool = False
        self.synced: bool = False
        self._state_listeners: list[Callable[[Timeline], None]] = []
        self.items: list[dict] = []
        self.sub_timelines: list[dict] = []
        if self.autoplay:
            self.play()

    def add_state_change_listener(self, listener: Callable[[Timeline], None]) -> None:
        self._state_listeners.append(listener)

    def remove_state_change_listener(self, listener: Callable[[Timeline], None]) -> None:
        if listener in self._state_listeners:
            self._state_listeners.remove(listener)

    def _notify_state_change(self) -> None:
        for cb in self._state_listeners:
            cb(self)

    def add(
        self,
        target: Any,
        properties: AnimationOptions,
        start_time: float | int | str = 0,
    ) -> Timeline:
        resolved_start = 0.0 if isinstance(start_time, str) else float(start_time)
        animation_props: dict[str, float] = {}
        for key, value in properties.items():
            if key not in self.RESERVED_KEYS and isinstance(value, (int, float)):
                animation_props[key] = float(value)
        targets = target if isinstance(target, list) else [target]
        item: dict = {
            "type": "animation",
            "start_time": resolved_start,
            "target": targets,
            "properties": animation_props,
            "initial_values": [],
            "duration": float(properties.get("duration", 1000)),
            "ease": properties.get("ease", "linear"),
            "loop": properties.get("loop"),
            "loop_delay": float(properties.get("loop_delay", properties.get("loopDelay", 0))),
            "alternate": properties.get("alternate", False),
            "on_update": properties.get("on_update", properties.get("onUpdate")),
            "on_complete": properties.get("on_complete", properties.get("onComplete")),
            "on_start": properties.get("on_start", properties.get("onStart")),
            "on_loop": properties.get("on_loop", properties.get("onLoop")),
            "completed": False,
            "started": False,
            "current_loop": 0,
            "once": properties.get("once", False),
        }
        self.items.append(item)
        return self

    def once(self, target: Any, properties: AnimationOptions) -> Timeline:
        self.add(target, {**properties, "once": True}, self.current_time)
        return self

    def call(self, callback: Callable[[], None], start_time: float | int | str = 0) -> Timeline:
        resolved_start = 0.0 if isinstance(start_time, str) else float(start_time)
        self.items.append({
            "type": "callback",
            "start_time": resolved_start,
            "callback": callback,
            "executed": False,
        })
        return self

    def sync(self, timeline: Timeline, start_time: float = 0) -> Timeline:
        if timeline.synced:
            raise ValueError("Timeline already synced")
        self.sub_timelines.append({
            "type": "timeline",
            "start_time": float(start_time),
            "timeline": timeline,
        })
        timeline.synced = True
        return self

    def play(self) -> Timeline:
        if self.is_complete:
            return self.restart()
        for sub_item in self.sub_timelines:
            if sub_item.get("timeline_started") and sub_item.get("timeline"):
                sub_item["timeline"].play()
        self.is_playing = True
        self._notify_state_change()
        return self

    def pause(self) -> Timeline:
        for sub_item in self.sub_timelines:
            sub = sub_item.get("timeline")
            if sub:
                sub.pause()
        self.is_playing = False
        if self._on_pause:
            self._on_pause()
        self._notify_state_change()
        return self

    def reset_items(self) -> None:
        for item in self.items:
            if item.get("type") == "callback":
                item["executed"] = False
            elif item.get("type") == "animation":
                item["completed"] = False
                item["started"] = False
                item["current_loop"] = 0
        for sub_item in self.sub_timelines:
            sub_item["timeline_started"] = False
            sub = sub_item.get("timeline")
            if sub:
                sub.restart()
                sub.pause()

    def restart(self) -> Timeline:
        self.is_complete = False
        self.current_time = 0.0
        self.is_playing = True
        self.reset_items()
        self._notify_state_change()
        return self

    def update(self, delta_time: float) -> None:
        for sub_item in self.sub_timelines:
            _evaluate_timeline_sync(sub_item, self.current_time + delta_time, delta_time)
        if not self.is_playing:
            return
        self.current_time += delta_time
        for item in self.items:
            _evaluate_item(item, self.current_time, delta_time)
        i = len(self.items) - 1
        while i >= 0:
            item = self.items[i]
            if item.get("type") == "animation" and item.get("once") and item.get("completed"):
                self.items.pop(i)
            i -= 1
        if self.loop and self.current_time >= self.duration:
            overshoot = self.current_time % self.duration
            self.reset_items()
            self.current_time = 0.0
            if overshoot > 0:
                self.update(overshoot)
        elif not self.loop and self.current_time >= self.duration:
            self.current_time = self.duration
            self.is_playing = False
            self.is_complete = True
            if self._on_complete:
                self._on_complete()
            self._notify_state_change()


class TimelineEngine:
    """Align with OpenTUI TimelineEngine: register, unregister, clear, update."""

    def __init__(self) -> None:
        self._timelines: set[Timeline] = set()
        self.defaults = {"frame_rate": 60}

    def register(self, timeline: Timeline) -> None:
        if timeline not in self._timelines:
            self._timelines.add(timeline)
            timeline.add_state_change_listener(self._on_timeline_state_change)

    def unregister(self, timeline: Timeline) -> None:
        if timeline in self._timelines:
            self._timelines.discard(timeline)
            timeline.remove_state_change_listener(self._on_timeline_state_change)

    def _on_timeline_state_change(self, _timeline: Timeline) -> None:
        pass

    def clear(self) -> None:
        for t in list(self._timelines):
            t.remove_state_change_listener(self._on_timeline_state_change)
        self._timelines.clear()

    def update(self, delta_time: float) -> None:
        for t in self._timelines:
            if not t.synced:
                t.update(delta_time)


engine = TimelineEngine()


def create_timeline(options: dict[str, Any] | TimelineOptions | None = None) -> Timeline:
    """Align with OpenTUI createTimeline(): create Timeline, autoplay if not false, engine.register, return."""
    opts = options or {}
    if isinstance(opts, TimelineOptions):
        opts = {"duration": opts.duration, "loop": opts.loop, "autoplay": opts.autoplay}
    t = Timeline(opts)
    if opts.get("autoplay", True) is not False:
        t.play()
    engine.register(t)
    return t
