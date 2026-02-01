# tests/unit/components/test_box.py

import pytest

pytest.importorskip("pytui.components.box")


class TestBox:
    def test_border_on_off(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(mock_context, {"width": 10, "height": 5, "border": True})
        b.x, b.y, b.width, b.height = 0, 0, 10, 5
        b.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "┌"
        assert buffer_40x20.get_cell(9, 0).char == "┐"
        assert buffer_40x20.get_cell(0, 4).char == "└"
        assert buffer_40x20.get_cell(9, 4).char == "┘"

    def test_border_style_rounded(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {"width": 8, "height": 4, "border": True, "border_style": "rounded"},
        )
        b.x, b.y, b.width, b.height = 0, 0, 8, 4
        b.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "╭"
        assert buffer_40x20.get_cell(7, 0).char == "╮"

    def test_title_centered(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {
                "width": 12,
                "height": 3,
                "border": True,
                "title": "OK",
                "title_alignment": "center",
            },
        )
        b.x, b.y, b.width, b.height = 0, 0, 12, 3
        b.render_self(buffer_40x20)
        # " OK " is 4 chars, centered in 12 -> start at 4
        assert buffer_40x20.get_cell(4, 0).char == " "
        assert buffer_40x20.get_cell(5, 0).char == "O"
        assert buffer_40x20.get_cell(6, 0).char == "K"

    def test_title_alignment_left(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {
                "width": 12,
                "height": 3,
                "border": True,
                "title": "OK",
                "title_alignment": "left",
            },
        )
        b.x, b.y, b.width, b.height = 0, 0, 12, 3
        b.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(1, 0).char == " "
        assert buffer_40x20.get_cell(2, 0).char == "O"
        assert buffer_40x20.get_cell(3, 0).char == "K"

    def test_border_partial_sides(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {"width": 10, "height": 5, "border": ["top", "bottom"]},
        )
        b.x, b.y, b.width, b.height = 0, 0, 10, 5
        b.render_self(buffer_40x20)
        assert b.border_sides == {"top": True, "right": False, "bottom": True, "left": False}
        assert buffer_40x20.get_cell(0, 0).char == "┌"
        assert buffer_40x20.get_cell(9, 0).char == "┐"
        assert buffer_40x20.get_cell(0, 4).char == "└"
        assert buffer_40x20.get_cell(9, 4).char == "┘"
        assert buffer_40x20.get_cell(0, 2).char == " "  # no left border in middle

    def test_focused_border_color(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {
                "width": 6,
                "height": 3,
                "border": True,
                "border_color": "#ffffff",
                "focused_border_color": "#00AAFF",
            },
        )
        b.x, b.y, b.width, b.height = 0, 0, 6, 3
        b.focused = True
        b.render_self(buffer_40x20)
        cell = buffer_40x20.get_cell(0, 0)
        assert cell.fg == (0, 0xAA, 0xFF, 255)

    def test_should_fill_false(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {"width": 6, "height": 3, "should_fill": False, "background_color": "#ff0000"},
        )
        b.x, b.y, b.width, b.height = 0, 0, 6, 3
        b.render_self(buffer_40x20)
        # interior should not be filled with red when should_fill is False
        cell = buffer_40x20.get_cell(1, 1)
        assert cell.bg != (255, 0, 0, 255)

    def test_custom_border_chars(self, mock_context, buffer_40x20):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {
                "width": 6,
                "height": 3,
                "border": True,
                "custom_border_chars": {"tl": "@", "tr": "@", "bl": "@", "br": "@", "h": "#", "v": "#"},
            },
        )
        b.x, b.y, b.width, b.height = 0, 0, 6, 3
        b.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "@"
        assert buffer_40x20.get_cell(5, 0).char == "@"
        assert buffer_40x20.get_cell(1, 0).char == "#"

    def test_camelCase_aliases(self, mock_context):
        from pytui.components.box import Box

        b = Box(
            mock_context,
            {
                "width": 10,
                "height": 5,
                "backgroundColor": "#333",
                "borderStyle": "double",
                "titleAlignment": "right",
            },
        )
        assert b.background_color == (0x33, 0x33, 0x33, 255)
        assert b.border_style == "double"
        assert b.title_alignment == "right"

    def test_border_property(self, mock_context):
        from pytui.components.box import Box

        b = Box(mock_context, {"width": 10, "height": 5, "border": ["top", "left"]})
        assert b.border == ["top", "left"]
        b2 = Box(mock_context, {"width": 10, "height": 5, "border": True})
        assert b2.border is True

    def test_get_scissor_rect(self, mock_context):
        from pytui.components.box import Box

        b = Box(mock_context, {"width": 10, "height": 5, "border": True})
        b.x, b.y, b.width, b.height = 0, 0, 10, 5
        r = b.get_scissor_rect()
        assert r["x"] == 1 and r["y"] == 1
        assert r["width"] == 8 and r["height"] == 3
        b2 = Box(mock_context, {"width": 10, "height": 5, "border": False})
        b2.x, b2.y, b2.width, b2.height = 0, 0, 10, 5
        r2 = b2.get_scissor_rect()
        assert r2["x"] == 0 and r2["y"] == 0 and r2["width"] == 10 and r2["height"] == 5

    def test_property_setters(self, mock_context):
        from pytui.components.box import Box

        b = Box(mock_context, {"width": 10, "height": 5})
        b.title = "X"
        assert b.title == "X"
        b.border = True
        assert b.border is True
        b.border_style = "double"
        assert b.border_style == "double"
        b.background_color = "#111111"
        assert b.background_color is not None
        b.gap = 2
        assert b.gap == 2

    def test_gap_option(self, mock_context):
        from pytui.components.box import Box

        b = Box(mock_context, {"width": 10, "height": 5, "gap": 1})
        assert b.gap == 1
        b2 = Box(mock_context, {"width": 10, "height": 5, "rowGap": 2, "columnGap": 2})
        assert b2.row_gap == 2
        assert b2.column_gap == 2
