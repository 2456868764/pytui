# tests/unit/components/test_tab_select.py

import pytest

pytest.importorskip("pytui.components.tab_select")


class TestTabSelect:
    def test_selected_property(self, mock_context):
        from pytui.components.tab_select import TabSelect

        t = TabSelect(
            mock_context,
            {"tabs": ["A", "B", "C"], "selected": 1, "width": 20, "height": 1},
        )
        assert t.selected == "B"

    def test_select_next_prev(self, mock_context):
        from pytui.components.tab_select import TabSelect

        t = TabSelect(
            mock_context,
            {"tabs": ["X", "Y", "Z"], "width": 20, "height": 1},
        )
        assert t.selected_index == 0
        t.select_next()
        assert t.selected_index == 1
        t.select_next()
        assert t.selected_index == 2
        t.select_next()
        assert t.selected_index == 0
        t.select_prev()
        assert t.selected_index == 2

    def test_selection_changed_emit(self, mock_context):
        from pytui.components.tab_select import TabSelect

        t = TabSelect(
            mock_context,
            {"tabs": ["a", "b"], "width": 20, "height": 1},
        )
        events = []
        t.on("selection_changed", lambda idx, label: events.append((idx, label)))
        t.select_index(1)
        assert events == [(1, "b")]

    def test_render_self_draws_tabs(self, mock_context, buffer_10x5):
        from pytui.components.tab_select import TabSelect

        t = TabSelect(
            mock_context,
            {"tabs": ["One", "Two"], "selected": 0, "width": 10, "height": 1},
        )
        t.x, t.y, t.width, t.height = 0, 0, 10, 1
        t.render_self(buffer_10x5)
        # Selected first tab is rendered as [One]
        assert buffer_10x5.get_cell(0, 0).char == "["
        assert buffer_10x5.get_cell(1, 0).char == "O"
