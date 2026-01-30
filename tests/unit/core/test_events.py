# tests/unit/core/test_events.py

import pytest

pytest.importorskip("pytui.core.events")


class TestEventBus:
    def test_on_emit(self):
        from pytui.core.events import EventBus

        bus = EventBus()
        out = []
        bus.on("x", lambda a, b: out.append((a, b)))
        bus.emit("x", 1, 2)
        assert out == [(1, 2)]

    def test_once(self):
        from pytui.core.events import EventBus

        bus = EventBus()
        out = []
        bus.once("y", lambda: out.append(1))
        bus.emit("y")
        bus.emit("y")
        assert out == [1]

    def test_remove_listener(self):
        from pytui.core.events import EventBus

        bus = EventBus()
        out = []

        def handler():
            out.append(1)

        bus.on("z", handler)
        bus.emit("z")
        bus.remove_listener("z", handler)
        bus.emit("z")
        assert out == [1]
