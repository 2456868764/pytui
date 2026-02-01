# tests/unit/components/test_select.py

import pytest

pytest.importorskip("pytui.components.select")


class TestSelect:
    def test_selected_property(self, mock_context):
        from pytui.components.select import Select

        s = Select(
            mock_context,
            {"options": ["a", "b", "c"], "selected": 1, "width": 10, "height": 3},
        )
        assert s.selected == "b"

    def test_select_next_prev(self, mock_context):
        from pytui.components.select import Select

        s = Select(
            mock_context,
            {"options": ["x", "y", "z"], "width": 10, "height": 3, "wrap_selection": True},
        )
        assert s.selected_index == 0
        s.select_next()
        assert s.selected_index == 1
        s.select_next()
        assert s.selected_index == 2
        s.select_next()
        assert s.selected_index == 0
        s.select_prev()
        assert s.selected_index == 2

    def test_render_self_draws_options(self, mock_context, buffer_10x5):
        from pytui.components.select import Select

        s = Select(
            mock_context,
            {"options": ["one", "two"], "width": 10, "height": 2, "show_description": False},
        )
        s.x, s.y, s.width, s.height = 0, 0, 10, 2
        s.render_self(buffer_10x5)
        # First option: "  one" (space space o n e)
        assert buffer_10x5.get_cell(2, 0).char == "o"
        assert buffer_10x5.get_cell(3, 0).char == "n"
        assert buffer_10x5.get_cell(2, 1).char == "t"
