# tests/unit/components/test_line_number.py

import pytest

pytest.importorskip("pytui.components.line_number")


class TestLineNumber:
    def test_line_count_and_scroll_offset(self, mock_context):
        from pytui.components.line_number import LineNumber

        ln = LineNumber(
            mock_context,
            {"line_count": 100, "scroll_offset": 5, "line_number_width": 4, "width": 4, "height": 3},
        )
        assert ln.line_count == 100
        assert ln.scroll_offset == 5

    def test_set_scroll_offset(self, mock_context):
        from pytui.components.line_number import LineNumber

        ln = LineNumber(
            mock_context,
            {"line_count": 10, "width": 4, "height": 5},
        )
        ln.request_render = lambda: None
        ln.set_scroll_offset(3)
        assert ln.scroll_offset == 3
        ln.set_scroll_offset(-1)
        assert ln.scroll_offset == 0

    def test_render_self_draws_numbers(self, mock_context, buffer_10x5):
        from pytui.components.line_number import LineNumber

        ln = LineNumber(
            mock_context,
            {"line_count": 10, "scroll_offset": 0, "line_number_width": 4, "width": 4, "height": 3},
        )
        ln.x, ln.y, ln.width, ln.height = 0, 0, 4, 3
        ln.render_self(buffer_10x5)
        # Line 1: "   1" (rjust 4)
        assert buffer_10x5.get_cell(3, 0).char == "1"
        assert buffer_10x5.get_cell(2, 0).char == " "
        # Line 2: "   2"
        assert buffer_10x5.get_cell(3, 1).char == "2"
        # Line 3: "   3"
        assert buffer_10x5.get_cell(3, 2).char == "3"
