# pytui.lib.parse_mouse - Aligns with OpenTUI lib/parse.mouse.ts
# MouseParser, RawMouseEvent, ScrollInfo, MouseEventType

from __future__ import annotations

import re
from typing import Literal, TypedDict

MouseEventType = Literal["down", "up", "move", "drag", "drag-end", "drop", "over", "out", "scroll"]


class ScrollInfo(TypedDict):
    """Align with OpenTUI ScrollInfo."""
    direction: Literal["up", "down", "left", "right"]
    delta: int


class RawMouseEvent(TypedDict, total=False):
    """Align with OpenTUI RawMouseEvent."""
    type: MouseEventType
    button: int
    x: int
    y: int
    modifiers: dict[str, bool]
    scroll: ScrollInfo


_SGR_MOUSE = re.compile(rb"^\x1b\[<(\d+);(\d+);(\d+)([Mm])")
_BASIC_MOUSE_PREFIX = b"\x1b[M"
_SCROLL_DIRECTIONS: dict[int, Literal["up", "down", "left", "right"]] = {
    0: "up",
    1: "down",
    2: "left",
    3: "right",
}


class MouseParser:
    """Parse SGR 1006 and basic mouse sequences. Aligns with OpenTUI MouseParser."""

    def __init__(self) -> None:
        self._mouse_buttons_pressed: set[int] = set()

    def reset(self) -> None:
        """Align with OpenTUI MouseParser.reset()."""
        self._mouse_buttons_pressed.clear()

    def parse_mouse_event(self, data: bytes | str) -> RawMouseEvent | None:
        """Parse one complete mouse sequence from data. Returns RawMouseEvent or None. Aligns OpenTUI parseMouseEvent()."""
        if isinstance(data, str):
            data = data.encode("utf-8", errors="replace")
        ev, _ = self._parse_sgr(data)
        if ev is not None:
            return ev
        ev, _ = self._parse_basic(data)
        return ev

    def _parse_sgr(self, view: bytes) -> tuple[RawMouseEvent | None, int]:
        m = _SGR_MOUSE.match(view)
        if not m:
            return None, 0
        consumed = len(m.group(0))
        btn = int(m.group(1))
        x = int(m.group(2)) - 1
        y = int(m.group(3)) - 1
        press_release = m.group(4) == b"m"
        button = btn & 3
        is_scroll = (btn & 64) != 0
        is_motion = (btn & 32) != 0
        modifiers = {
            "shift": (btn & 4) != 0,
            "alt": (btn & 8) != 0,
            "ctrl": (btn & 16) != 0,
        }
        event: RawMouseEvent = {"x": x, "y": y, "modifiers": modifiers}
        if is_scroll and not press_release:
            event["type"] = "scroll"
            event["button"] = 0
            event["scroll"] = {"direction": _SCROLL_DIRECTIONS.get(button, "up"), "delta": 1}
            event["release"] = False
            event["motion"] = False
        elif is_motion:
            event["type"] = "drag" if self._mouse_buttons_pressed else "move"
            event["button"] = 0 if button == 3 else button
            event["release"] = False
            event["motion"] = True
        else:
            event["type"] = "up" if press_release else "down"
            event["button"] = 0 if button == 3 else button
            event["release"] = press_release  # backward compat
            event["motion"] = False
            if event["type"] == "down" and button != 3:
                self._mouse_buttons_pressed.add(button)
            elif event["type"] == "up":
                self._mouse_buttons_pressed.clear()
        return event, consumed

    def _parse_basic(self, view: bytes) -> tuple[RawMouseEvent | None, int]:
        if not view.startswith(_BASIC_MOUSE_PREFIX) or len(view) < 6:
            return None, 0
        button_byte = view[3] - 32
        x = view[4] - 33
        y = view[5] - 33
        button = button_byte & 3
        is_scroll = (button_byte & 64) != 0
        modifiers = {
            "shift": (button_byte & 4) != 0,
            "alt": (button_byte & 8) != 0,
            "ctrl": (button_byte & 16) != 0,
        }
        if is_scroll:
            ev: RawMouseEvent = {
                "type": "scroll",
                "button": 0,
                "x": x,
                "y": y,
                "modifiers": modifiers,
                "scroll": {"direction": _SCROLL_DIRECTIONS.get(button, "up"), "delta": 1},
            }
        else:
            ev = {
                "type": "up" if button == 3 else "down",
                "button": 0 if button == 3 else button,
                "x": x,
                "y": y,
                "modifiers": modifiers,
            }
        return ev, 6
