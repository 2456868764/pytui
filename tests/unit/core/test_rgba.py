# tests/unit/core/test_rgba.py

import pytest

pytest.importorskip("pytui.core.rgba")


class TestRGBA:
    def test_from_ints(self):
        from pytui.core.rgba import RGBA

        r = RGBA.from_ints(255, 0, 128, 255)
        assert r.r == 255 and r.g == 0 and r.b == 128 and r.a == 255

    def test_from_hex(self):
        from pytui.core.rgba import RGBA

        r = RGBA.from_hex("#ff00ff")
        assert r.r == 255 and r.g == 0 and r.b == 255
        r2 = RGBA.from_hex("#f0f")
        assert r2.r == 255 and r2.g == 0 and r2.b == 255

    def test_from_values(self):
        from pytui.core.rgba import RGBA

        r = RGBA.from_values(1.0, 0.0, 0.5)
        assert r.r == 255 and r.g == 0 and r.b == 128  # 0.5 * 255 rounded

    def test_to_tuple(self):
        from pytui.core.rgba import RGBA

        r = RGBA(10, 20, 30, 40)
        assert r.to_tuple() == (10, 20, 30, 40)

    def test_eq(self):
        from pytui.core.rgba import RGBA

        assert RGBA(1, 2, 3, 255) == RGBA(1, 2, 3, 255)
        assert RGBA(1, 2, 3, 255) != RGBA(1, 2, 3, 0)
