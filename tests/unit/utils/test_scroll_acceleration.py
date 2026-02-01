# Aligns with OpenTUI MacOSScrollAccel: tick(now_ms), A/tau/max_multiplier opts.

import pytest

pytest.importorskip("pytui.lib.scroll_acceleration")


class TestLinearScrollAccel:
    def test_tick_always_one(self):
        from pytui.lib.scroll_acceleration import LinearScrollAccel

        accel = LinearScrollAccel()
        assert accel.tick() == 1.0
        assert accel.tick() == 1.0
        accel.reset()
        assert accel.tick() == 1.0

    def test_reset_no_op(self):
        from pytui.lib.scroll_acceleration import LinearScrollAccel

        accel = LinearScrollAccel()
        accel.reset()
        assert accel.tick() == 1.0


class TestMacOSScrollAccel:
    def test_first_tick_returns_one(self):
        from pytui.lib.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel()
        # now in ms (OpenTUI uses Date.now())
        assert accel.tick(1000.0) == 1.0

    def test_fast_ticks_increase_multiplier(self):
        from pytui.lib.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel()
        base_ms = 1000.0
        assert accel.tick(base_ms) == 1.0
        # 30ms between ticks -> faster scrolling, multiplier > 1
        assert accel.tick(base_ms + 30) >= 1.0
        assert accel.tick(base_ms + 60) >= 1.0

    def test_reset_clears_state(self):
        from pytui.lib.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel()
        accel.tick(1000.0)
        accel.tick(1010.0)  # 10ms later
        accel.reset()
        assert accel.tick(1020.0) == 1.0

    def test_slow_ticks_after_timeout_return_one(self):
        from pytui.lib.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel()
        accel.tick(1000.0)
        accel.tick(1010.0)
        # 200ms later -> streak expired (streakTimeout 150ms)
        assert accel.tick(1210.0) == 1.0
