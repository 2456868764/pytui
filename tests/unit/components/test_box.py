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
            {"width": 12, "height": 3, "border": True, "title": "OK"},
        )
        b.x, b.y, b.width, b.height = 0, 0, 12, 3
        b.render_self(buffer_40x20)
        # " OK " is 4 chars, centered in 12 -> start at 4
        assert buffer_40x20.get_cell(4, 0).char == " "
        assert buffer_40x20.get_cell(5, 0).char == "O"
        assert buffer_40x20.get_cell(6, 0).char == "K"
