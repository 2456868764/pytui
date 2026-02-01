# tests.unit.core.test_animation - Timeline unit tests (aligned with OpenTUI Timeline.ts)

import pytest

pytest.importorskip("pytui.core.animation")


class TestTimeline:
    def test_play_pause_current_time(self):
        from pytui.core.animation import Timeline

        t = Timeline({"autoplay": False})
        assert t.current_time == 0.0
        assert not t.is_playing
        t.play()
        assert t.is_playing
        t.update(100)
        assert t.current_time == 100
        t.pause()
        assert not t.is_playing
        t.update(50)
        assert t.current_time == 100

    def test_call_at_start_time(self):
        from pytui.core.animation import Timeline

        t = Timeline({"autoplay": False, "duration": 1000})
        seen = []
        t.call(lambda: seen.append(1), 0)
        t.call(lambda: seen.append(2), 50)
        t.play()
        t.update(0)
        assert len(seen) == 1
        t.update(50)
        assert len(seen) == 2

    def test_restart_resets_items(self):
        from pytui.core.animation import Timeline

        t = Timeline({"autoplay": False})
        seen = []
        t.call(lambda: seen.append(1), 0)
        t.play()
        t.update(10)
        assert len(seen) == 1
        t.restart()
        seen.clear()
        t.update(10)
        assert len(seen) == 1

    def test_add_animation_property(self):
        from pytui.core.animation import Timeline

        obj = {"x": 0}
        t = Timeline({"autoplay": False})
        t.add(obj, {"x": 100, "duration": 100}, 0)
        t.play()
        t.update(0)
        assert obj["x"] == 0
        t.update(50)
        assert 0 < obj["x"] < 100
        t.update(50)
        assert obj["x"] == 100

    def test_easing_linear(self):
        from pytui.core.animation import Timeline

        obj = {"v": 0}
        t = Timeline({"autoplay": False})
        t.add(obj, {"v": 1, "duration": 100, "ease": "linear"}, 0)
        t.play()
        t.update(50)
        assert obj["v"] == pytest.approx(0.5, abs=0.01)

    def test_loop_resets_current_time(self):
        from pytui.core.animation import Timeline

        t = Timeline({"autoplay": False, "duration": 100, "loop": True})
        t.call(lambda: None, 0)
        t.play()
        t.update(150)
        assert t.current_time == pytest.approx(50, abs=1)
        assert t.is_playing

    def test_no_loop_completes(self):
        from pytui.core.animation import Timeline

        completed = []
        t = Timeline({"autoplay": False, "duration": 100, "loop": False, "on_complete": lambda: completed.append(1)})
        t.play()
        t.update(100)
        assert t.is_complete
        assert t.current_time == 100
        assert len(completed) == 1

    def test_create_timeline_registers_and_autoplay(self):
        from pytui.core.animation import create_timeline, engine

        before = len(engine._timelines)
        t = create_timeline({"duration": 500, "autoplay": True})
        assert t in engine._timelines
        assert t.is_playing
        engine.unregister(t)
        assert t not in engine._timelines

    def test_sync_sub_timeline(self):
        from pytui.core.animation import Timeline

        parent = Timeline({"autoplay": False})
        child = Timeline({"autoplay": False})
        parent.sync(child, 10)
        assert child.synced
        parent.play()
        parent.update(15)
        assert child.current_time == 5
        parent.update(10)
        assert child.current_time == 15


class TestEasing:
    def test_linear(self):
        from pytui.core.animation import EASING_FUNCTIONS

        f = EASING_FUNCTIONS["linear"]
        assert f(0) == 0
        assert f(0.5) == 0.5
        assert f(1) == 1

    def test_in_quad(self):
        from pytui.core.animation import EASING_FUNCTIONS

        f = EASING_FUNCTIONS["inQuad"]
        assert f(0) == 0
        assert f(1) == 1
        assert 0 < f(0.5) < 0.5
