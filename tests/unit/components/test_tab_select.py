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
        assert t.selected is not None
        assert t.selected.name == "B"
        assert t.selected_name == "B"

    def test_select_next_prev(self, mock_context):
        from pytui.components.tab_select import TabSelect

        t = TabSelect(
            mock_context,
            {"tabs": ["X", "Y", "Z"], "width": 20, "height": 1, "wrap_selection": True},
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
        assert len(events) == 1
        assert events[0][0] == 1
        assert (events[0][1].name if hasattr(events[0][1], "name") else events[0][1]) == "b"

    def test_render_self_draws_tabs(self, mock_context, buffer_10x5):
        from pytui.components.tab_select import TabSelect

        t = TabSelect(
            mock_context,
            {"tabs": ["One", "Two"], "selected": 0, "width": 10, "height": 1},
        )
        t.x, t.y, t.width, t.height = 0, 0, 10, 1
        t.render_self(buffer_10x5)
        # Selected first tab name starts at x+1
        assert buffer_10x5.get_cell(1, 0).char == "O"

    def test_options_tab_select_option(self, mock_context):
        from pytui.components.tab_select import TabSelect, TabSelectOption

        opts = [
            TabSelectOption(name="A", description="First"),
            TabSelectOption(name="B", description="Second"),
        ]
        t = TabSelect(mock_context, {"options": opts, "width": 20, "height": 2})
        assert len(t.options) == 2
        assert t.get_selected_option().name == "A"
        t.move_right()
        assert t.get_selected_option().name == "B"
