# tests.unit.core.test_mouse

import pytest

pytest.importorskip("pytui.core.mouse")


class TestMouseHandler:
    def test_feed_sgr_mouse_emit(self):
        from pytui.core.mouse import MouseHandler

        h = MouseHandler()
        events = []
        h.on("mouse", lambda e: events.append(e))
        # SGR 1006: \x1b[<0;10;5M = left press at (10,5), 0-based (9,4)
        rest = h.feed(b"\x1b[<0;10;5M")
        assert len(events) == 1
        assert events[0]["x"] == 9
        assert events[0]["y"] == 4
        assert events[0]["release"] is False
        assert rest == b""

    def test_feed_mouse_then_unconsumed(self):
        from pytui.core.mouse import MouseHandler

        h = MouseHandler()
        events = []
        h.on("mouse", lambda e: events.append(e))
        rest = h.feed(b"\x1b[<0;1;1Ma")
        assert len(events) == 1
        assert rest == b"a"

    def test_clear(self):
        from pytui.core.mouse import MouseHandler

        h = MouseHandler()
        h.feed(b"\x1b[<")
        h.clear()
        rest = h.feed(b"0;1;1M")
        assert rest == b"0;1;1M"
