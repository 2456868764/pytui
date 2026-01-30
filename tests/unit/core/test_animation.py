# tests.unit.core.test_animation - Timeline 单元测试

import pytest

pytest.importorskip("pytui.core.animation")


class TestTimeline:
    def test_elapsed_before_start_is_zero(self):
        from pytui.core.animation import Timeline

        t = Timeline()
        assert t.elapsed == 0.0

    def test_start_and_elapsed_increases(self):
        import time
        from pytui.core.animation import Timeline

        t = Timeline()
        t.start()
        time.sleep(0.05)
        assert t.elapsed >= 0.04
        t.stop()

    def test_pause_resume(self):
        import time
        from pytui.core.animation import Timeline

        t = Timeline()
        t.start()
        time.sleep(0.03)
        t.pause()
        e1 = t.elapsed
        time.sleep(0.05)
        assert t.elapsed == e1
        t.resume()
        time.sleep(0.02)
        assert t.elapsed >= e1 + 0.01

    def test_tick_callbacks(self):
        import time
        from pytui.core.animation import Timeline

        t = Timeline()
        seen = []

        def cb(elapsed: float) -> None:
            seen.append(elapsed)

        t.on_tick(cb)
        t.start()
        time.sleep(0.02)
        t.tick()
        assert len(seen) == 1
        assert seen[0] >= 0.01
        t.tick()
        assert len(seen) == 2
        t.remove_tick(cb)
        t.tick()
        assert len(seen) == 2
