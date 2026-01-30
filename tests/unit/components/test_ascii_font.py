# tests/unit/components/test_ascii_font.py

import pytest

pytest.importorskip("pytui.components.ascii_font")


class TestASCIIFont:
    def test_measure_text(self):
        from pytui.components.ascii_font import TINY_FONT, measure_text

        w, h = measure_text("Hi", TINY_FONT)
        assert w >= 2
        assert h == 2
        w2, _ = measure_text(" ", TINY_FONT)
        assert w2 >= 1

    def test_render_self(self, mock_context, buffer_40x20):
        from pytui.components.ascii_font import ASCIIFont, measure_text

        af = ASCIIFont(mock_context, {"text": "A", "font": "tiny"})
        af.x, af.y = 0, 0
        w, h = measure_text("A", af._get_font())
        af.width, af.height = max(1, w), max(1, h)
        af.render_self(buffer_40x20)
        # A 应绘制非空格字符
        found = False
        for dy in range(af.height):
            for dx in range(af.width):
                c = buffer_40x20.get_cell(dx, dy)
                if c and c.char and c.char != " ":
                    found = True
                    break
        assert found

    def test_register_font(self):
        from pytui.components.ascii_font import ASCIIFont, measure_text

        custom = {"name": "custom", "lines": 1, "letterspace_size": 0, "chars": {"X": ["X"], " ": [" "]}}
        ASCIIFont.register_font("one", custom)
        w, h = measure_text("X", custom)
        assert w == 1
        assert h == 1
