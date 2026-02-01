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

    def test_grid_huge_pallet_fonts_registered(self):
        from pytui.components.ascii_font import ASCIIFont, GRID_FONT, HUGE_FONT, PALLET_FONT

        assert "grid" in ASCIIFont._fonts
        assert "huge" in ASCIIFont._fonts
        assert "pallet" in ASCIIFont._fonts
        assert ASCIIFont._fonts["grid"]["name"] == "grid"
        assert ASCIIFont._fonts["huge"]["name"] == "huge"
        assert ASCIIFont._fonts["pallet"]["name"] == "pallet"
        assert ASCIIFont._fonts["grid"] is GRID_FONT
        assert ASCIIFont._fonts["huge"] is HUGE_FONT
        assert ASCIIFont._fonts["pallet"] is PALLET_FONT

    def test_coordinate_to_character_index(self):
        from pytui.components.ascii_font import TINY_FONT, coordinate_to_character_index, measure_text

        text = "AB"
        w0, _ = measure_text("A", TINY_FONT)
        w1, _ = measure_text("AB", TINY_FONT)
        assert coordinate_to_character_index(-1, text, TINY_FONT) == 0
        assert coordinate_to_character_index(0, text, TINY_FONT) == 0
        assert coordinate_to_character_index(w0, text, TINY_FONT) in (0, 1)
        assert coordinate_to_character_index(w1, text, TINY_FONT) == 2
        assert coordinate_to_character_index(w1 + 10, text, TINY_FONT) == 2
        assert coordinate_to_character_index(0, "", TINY_FONT) == 0

    def test_default_selectable_and_camelCase(self, mock_context):
        from pytui.components.ascii_font import ASCIIFont

        af = ASCIIFont(mock_context, {"text": "Hi"})
        assert af.selectable is True
        af2 = ASCIIFont(mock_context, {"text": "x", "backgroundColor": "#000000", "selectionBg": "#333333"})
        assert af2.background_color is not None
        assert af2.selection_bg is not None

    def test_property_getters_setters(self, mock_context):
        from pytui.components.ascii_font import ASCIIFont

        af = ASCIIFont(mock_context, {"text": "A", "font": "tiny"})
        assert af.text == "A"
        assert af.font == "tiny"
        af.text = "AB"
        assert af.text == "AB"
        af.font = "block"
        assert af.font == "block"
        af.color = "#ff0000"
        af.background_color = "#000011"

    def test_should_start_selection_and_has_selection(self, mock_context):
        from pytui.components.ascii_font import ASCIIFont, measure_text

        af = ASCIIFont(mock_context, {"text": "AB", "font": "tiny"})
        w, h = measure_text("AB", af._get_font())
        af.x, af.y = 0, 0
        af.width, af.height = max(1, w), max(1, h)
        # should_start_selection(x, y) takes global coords (aligns with OpenTUI)
        assert af.should_start_selection(0, 0) is True
        assert af.should_start_selection(-1, 0) is False
        af.x, af.y = 10, 5
        assert af.should_start_selection(10, 5) is True
        assert af.should_start_selection(9, 5) is False
        assert af.has_selection() is False

    def test_on_selection_changed_and_get_selected_text(self, mock_context):
        from pytui.components.ascii_font import ASCIIFont, measure_text, get_character_positions

        af = ASCIIFont(mock_context, {"text": "Hello", "font": "tiny"})
        w, h = measure_text("Hello", af._get_font())
        af.x, af.y = 0, 0
        af.width, af.height = max(1, w), max(1, h)
        pos = get_character_positions("Hello", af._get_font())
        local_sel = {"anchorX": 0, "anchorY": 0, "focusX": pos[2], "focusY": 0, "isActive": True}
        changed = af.on_selection_changed(local_sel)
        assert changed is True
        assert af.has_selection() is True
        assert af.get_selected_text() == "He"
        af.on_selection_changed(None)
        assert af.has_selection() is False
        assert af.get_selected_text() == ""

    def test_on_selection_changed_accepts_core_selection(self, mock_context):
        from pytui.components.ascii_font import ASCIIFont, measure_text, get_character_positions
        from pytui.lib.selection import Selection

        af = ASCIIFont(mock_context, {"text": "Hi", "font": "tiny"})
        w, h = measure_text("Hi", af._get_font())
        af.x, af.y = 0, 0
        af.width, af.height = max(1, w), max(1, h)
        pos = get_character_positions("Hi", af._get_font())
        # Global selection: anchor (0,0), focus (pos[1], 0) -> "H"
        sel = Selection(None, 0, 0, pos[1], 0, is_active=True)
        changed = af.on_selection_changed(sel)
        assert changed is True
        assert af.has_selection() is True
        assert af.get_selected_text() == "H"

    def test_get_character_positions(self):
        from pytui.components.ascii_font import TINY_FONT, get_character_positions, measure_text

        pos = get_character_positions("AB", TINY_FONT)
        assert len(pos) == 3
        assert pos[0] == 0
        assert pos[-1] == measure_text("AB", TINY_FONT)[0]
