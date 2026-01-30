# tests/unit/utils/test_scroll_acceleration.py

import pytest

pytest.importorskip("pytui.utils.scroll_acceleration")


class TestLinearScrollAccel:
    def test_tick_always_one(self):
        from pytui.utils.scroll_acceleration import LinearScrollAccel

        accel = LinearScrollAccel()
        assert accel.tick() == 1.0
        assert accel.tick() == 1.0
        accel.reset()
        assert accel.tick() == 1.0

    def test_reset_no_op(self):
        from pytui.utils.scroll_acceleration import LinearScrollAccel

        accel = LinearScrollAccel()
        accel.reset()
        assert accel.tick() == 1.0


class TestMacOSScrollAccel:
    def test_first_tick_returns_one(self):
        from pytui.utils.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel(threshold1=80, threshold2=40, multiplier1=2, multiplier2=4)
        assert accel.tick(1000.0) == 1.0

    def test_fast_ticks_increase_multiplier(self):
        from pytui.utils.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel(threshold1=100, threshold2=50, multiplier1=2, multiplier2=4)
        base = 1000.0
        assert accel.tick(base) == 1.0
        # 30ms between ticks -> fast
        assert accel.tick(base + 0.030) >= 1.0
        assert accel.tick(base + 0.060) >= 1.0

    def test_reset_clears_state(self):
        from pytui.utils.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel()
        accel.tick(1000.0)
        accel.tick(1000.05)
        accel.reset()
        assert accel.tick(1000.1) == 1.0

    def test_slow_ticks_after_timeout_return_one(self):
        from pytui.utils.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel(streak_timeout_ms=150)
        accel.tick(1000.0)
        accel.tick(1000.05)
        # 200ms later -> streak expired
        assert accel.tick(1000.25) == 1.0
