# tests/unit/utils/test_selection.py - Selection 与 ASCIIFontSelectionHelper 单元测试

import pytest

pytest.importorskip("pytui.lib.selection")


class TestSelection:
    def test_selection_anchor_focus(self):
        from pytui.lib.selection import Selection

        s = Selection(10, 5, 20, 8, is_active=True)
        assert s.anchor == (10, 5)
        assert s.focus == (20, 8)
        assert s.is_active is True

    def test_to_local(self):
        from pytui.lib.selection import Selection

        s = Selection(10, 5, 20, 8)
        local = s.to_local(2, 1)
        assert local.anchor_x == 8
        assert local.anchor_y == 4
        assert local.focus_x == 18
        assert local.focus_y == 7
        assert local.is_active is True

    def test_convert_global_to_local_selection_none(self):
        from pytui.lib.selection import convert_global_to_local_selection

        assert convert_global_to_local_selection(None, 0, 0) is None

    def test_convert_global_to_local_selection_inactive(self):
        from pytui.lib.selection import Selection, convert_global_to_local_selection

        s = Selection(1, 2, 3, 4, is_active=False)
        assert convert_global_to_local_selection(s, 0, 0) is None

    def test_convert_global_to_local_selection_active(self):
        from pytui.lib.selection import Selection, convert_global_to_local_selection

        s = Selection(5, 6, 7, 8)
        local = convert_global_to_local_selection(s, 1, 2)
        assert local is not None
        assert local.anchor_x == 4 and local.anchor_y == 4
        assert local.focus_x == 6 and local.focus_y == 6


class TestASCIIFontSelectionHelper:
    def test_has_selection_get_selection(self):
        from pytui.lib.selection import ASCIIFontSelectionHelper

        def text():
            return "Hi"

        def font():
            return {"name": "tiny", "lines": 2, "letterspace_size": 1, "chars": {"H": ["H"], "i": ["i"], " ": [" "]}}

        helper = ASCIIFontSelectionHelper(text, font)
        assert helper.has_selection() is False
        assert helper.get_selection() is None

    def test_coordinate_to_character_index(self):
        from pytui.lib.selection import ASCIIFontSelectionHelper

        def text():
            return "AB"

        def font():
            return {"name": "t", "lines": 1, "letterspace_size": 0, "chars": {"A": ["A"], "B": ["B"], " ": [" "]}}

        helper = ASCIIFontSelectionHelper(text, font)
        assert helper.coordinate_to_character_index(0, "AB") == 0
        assert helper.coordinate_to_character_index(1, "AB") in (0, 1)
        assert helper.coordinate_to_character_index(2, "AB") == 2

    def test_on_local_selection_changed_clears_when_none(self):
        from pytui.lib.selection import ASCIIFontSelectionHelper, LocalSelectionBounds

        def text():
            return "Hi"

        def font():
            return {"name": "t", "lines": 1, "letterspace_size": 0, "chars": {"H": ["H"], "i": ["i"], " ": [" "]}}

        helper = ASCIIFontSelectionHelper(text, font)
        helper._selection = (0, 1)
        changed = helper.on_local_selection_changed(None, 10, 5)
        assert changed is True
        assert helper.get_selection() is None

    def test_on_local_selection_changed_sets_range(self):
        from pytui.lib.selection import ASCIIFontSelectionHelper, LocalSelectionBounds

        def text():
            return "ABC"

        def font():
            return {
                "name": "t",
                "lines": 1,
                "letterspace_size": 0,
                "chars": {"A": ["A"], "B": ["B"], "C": ["C"], " ": [" "]},
            }

        helper = ASCIIFontSelectionHelper(text, font)
        bounds = LocalSelectionBounds(anchor_x=0, anchor_y=0, focus_x=2, focus_y=0, is_active=True)
        changed = helper.on_local_selection_changed(bounds, 10, 1)
        assert helper.get_selection() is not None
        start, end = helper.get_selection()
        assert 0 <= start < end <= 3
