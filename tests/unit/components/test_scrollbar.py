# tests/unit/components/test_scrollbar.py

import pytest

pytest.importorskip("pytui.components.scrollbar")


class TestScrollBar:
    def test_scroll_value_property(self, mock_context):
        from pytui.components.scrollbar import ScrollBar

        sb = ScrollBar(
            mock_context,
            {"scroll_max": 10, "scroll_value": 3, "width": 1, "height": 5},
        )
        assert sb.scroll_value == 3

    def test_set_scroll_value_clamps_and_emits(self, mock_context):
        from pytui.components.scrollbar import ScrollBar

        sb = ScrollBar(
            mock_context,
            {"scroll_max": 5, "scroll_value": 0, "width": 1, "height": 5},
        )
        events = []
        sb.on("scroll", lambda v: events.append(v))
        sb.set_scroll_value(3)
        assert sb.scroll_value == 3
        assert events == [3]
        sb.set_scroll_value(10)
        # scroll_position clamped to scroll_size - viewport_size = 5 - 1 = 4
        assert sb.scroll_value == 4
        sb.set_scroll_value(-1)
        assert sb.scroll_value == 0

    def test_value_to_row_and_row_to_value(self, mock_context):
        from pytui.components.scrollbar import ScrollBar

        sb = ScrollBar(
            mock_context,
            {"scroll_max": 10, "scroll_value": 0, "viewport_size": 1, "width": 1, "height": 5},
        )
        sb.x, sb.y, sb.width, sb.height = 0, 0, 1, 5
        assert sb.value_to_row() == 0
        sb.scroll_position = 9  # max position when scroll_size=10, viewport_size=1
        assert sb.value_to_row() == 4
        assert sb.row_to_value(0) == 0
        assert sb.row_to_value(4) == 9

    def test_render_self_draws_track_and_thumb(self, mock_context, buffer_10x5):
        from pytui.components.scrollbar import ScrollBar

        sb = ScrollBar(
            mock_context,
            {"scroll_max": 5, "scroll_value": 0, "width": 1, "height": 5},
        )
        sb.x, sb.y, sb.width, sb.height = 0, 0, 1, 5
        sb.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "█"
        assert buffer_10x5.get_cell(0, 2).char == "│"
