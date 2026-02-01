# pytui.core.mouse - MouseHandler uses lib.parse_mouse.MouseParser

from __future__ import annotations

from pyee import EventEmitter

from pytui.lib.parse_mouse import (
    MouseEventType,
    MouseParser,
    RawMouseEvent,
    ScrollInfo,
)


class MouseHandler(EventEmitter):
    """Parse SGR 1006 and basic mouse; emit 'mouse' with RawMouseEvent. Uses lib.parse_mouse.MouseParser."""

    def __init__(self) -> None:
        super().__init__()
        self._buffer = bytearray()
        self._parser = MouseParser()

    def reset(self) -> None:
        self._parser.reset()
        self._buffer.clear()

    def feed(self, data: bytes | str) -> bytes:
        if isinstance(data, str):
            data = data.encode("utf-8", errors="replace")
        self._buffer.extend(data)
        unconsumed = bytearray()
        i = 0
        while i < len(self._buffer):
            view = bytes(self._buffer[i:])
            ev, consumed = self._parser._parse_sgr(view)
            if ev is not None:
                self.emit("mouse", ev)
                i += consumed
                continue
            ev, consumed = self._parser._parse_basic(view)
            if ev is not None:
                self.emit("mouse", ev)
                i += consumed
                continue
            unconsumed.append(self._buffer[i])
            i += 1
        del self._buffer[:i]
        return bytes(unconsumed)

    def clear(self) -> None:
        self._buffer.clear()
