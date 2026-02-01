# tests/unit/core/test_selection.py - core/selection 与 OpenTUI lib/selection 对齐测试

import pytest

pytest.importorskip("pytui.lib.selection")


class TestSelectionState:
    def test_get_range_clear_selection(self):
        from pytui.lib.selection import SelectionState

        s = SelectionState(10)
        s.set_selection(2, 5)
        assert s.get_range() == (2, 5)
        s.clear_selection()
        assert s.get_range() is None

    def test_set_cursor_clears_anchor(self):
        from pytui.lib.selection import SelectionState

        s = SelectionState(10)
        s.set_selection(1, 3)
        s.set_cursor(7)
        assert s.anchor is None and s.cursor == 7


class TestSelection:
    def test_anchor_focus_bounds(self):
        from pytui.lib.selection import Selection

        sel = Selection(None, 2, 1, 5, 4)
        assert sel.anchor == (2, 1)
        assert sel.focus == (5, 4)
        b = sel.bounds
        assert b["x"] == 2 and b["y"] == 1 and b["width"] == 4 and b["height"] == 4

    def test_is_start_is_active_is_selecting(self):
        from pytui.lib.selection import Selection

        sel = Selection(None, 0, 0, 1, 1, is_start=True, is_selecting=False)
        assert sel.is_start is True
        sel.is_start = False
        assert sel.is_start is False
        assert sel.is_selecting is False

    def test_to_local(self):
        from pytui.lib.selection import Selection

        sel = Selection(None, 10, 5, 20, 8)
        local = sel.to_local(10, 5)
        assert local.anchor_x == 0 and local.anchor_y == 0
        assert local.focus_x == 10 and local.focus_y == 3
        assert local.is_active is True

    def test_get_selected_text_empty(self):
        from pytui.lib.selection import Selection

        sel = Selection(None, 0, 0, 1, 1)
        assert sel.get_selected_text() == ""


class TestConvertGlobalToLocalSelection:
    def test_none_returns_none(self):
        from pytui.lib.selection import convert_global_to_local_selection

        assert convert_global_to_local_selection(None, 0, 0) is None

    def test_inactive_returns_none(self):
        from pytui.lib.selection import Selection, convert_global_to_local_selection

        sel = Selection(None, 1, 2, 3, 4, is_active=False)
        assert convert_global_to_local_selection(sel, 0, 0) is None

    def test_active_returns_local_bounds(self):
        from pytui.lib.selection import Selection, convert_global_to_local_selection

        sel = Selection(None, 5, 6, 7, 8)
        local = convert_global_to_local_selection(sel, 1, 2)
        assert local is not None
        assert local.anchor_x == 4 and local.anchor_y == 4
        assert local.focus_x == 6 and local.focus_y == 6
