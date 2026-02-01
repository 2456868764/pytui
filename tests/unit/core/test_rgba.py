# tests/unit/core/test_rgba.py

import pytest

pytest.importorskip("pytui.lib")


class TestRGBA:
    def test_from_ints(self):
        from pytui.lib import RGBA

        r = RGBA.from_ints(255, 0, 128, 255)
        assert r.r == 255 and r.g == 0 and r.b == 128 and r.a == 255

    def test_from_hex(self):
        from pytui.lib import RGBA

        r = RGBA.from_hex("#ff00ff")
        assert r.r == 255 and r.g == 0 and r.b == 255
        r2 = RGBA.from_hex("#f0f")
        assert r2.r == 255 and r2.g == 0 and r2.b == 255

    def test_from_values(self):
        from pytui.lib import RGBA

        r = RGBA.from_values(1.0, 0.0, 0.5)
        assert r.r == 255 and r.g == 0 and r.b == 128  # 0.5 * 255 rounded

    def test_to_tuple(self):
        from pytui.lib import RGBA

        r = RGBA(10, 20, 30, 40)
        assert r.to_tuple() == (10, 20, 30, 40)

    def test_eq(self):
        from pytui.lib import RGBA

        assert RGBA(1, 2, 3, 255) == RGBA(1, 2, 3, 255)
        assert RGBA(1, 2, 3, 255) != RGBA(1, 2, 3, 0)

    def test_from_array(self):
        from pytui.lib import RGBA

        r = RGBA.from_array([255, 0, 128, 255])
        assert r.r == 255 and r.g == 0 and r.b == 128 and r.a == 255
        r2 = RGBA.from_array([1.0, 0.0, 0.5, 1.0])
        assert r2.r == 255 and r2.g == 0 and r2.b == 128

    def test_map(self):
        from pytui.lib import RGBA

        r = RGBA(10, 20, 30, 255)
        assert r.map(lambda x: x + 1) == [11, 21, 31, 256]

    def test_str(self):
        from pytui.lib import RGBA

        s = str(RGBA(255, 0, 0, 255))
        assert "rgba" in s and "1.00" in s and "0.00" in s  # Aligns OpenTUI toString() 0-1 display

    def test_rgb_to_hex_hex_to_rgb(self):
        from pytui.lib import RGBA, hex_to_rgb, rgb_to_hex

        r = RGBA(255, 0, 255, 255)
        assert rgb_to_hex(r) == "#ff00ff"
        assert hex_to_rgb("#ff00ff").r == 255 and hex_to_rgb("#ff00ff").b == 255
