# Unit tests for extmarks with display-width (multi-width) semantics
# Aligned with OpenTUI extmarks-multiwidth.test.ts - lib-level only (ExtmarksStore).

from __future__ import annotations

import pytest

from pytui.lib.extmarks import Extmark, ExtmarksStore


class TestExtmarksMultiwidth:
    """ExtmarksStore uses display-width offsets; multi-width chars span multiple columns."""

    def test_highlight_after_multiwidth_display_offsets(self) -> None:
        """Align: highlight text AFTER multi-width chars uses display-width offsets.
        e.g. '前后端分离 @git-committer' - before '@' = 11 display cols (5*2 + 1 space).
        """
        store = ExtmarksStore()
        # Simulate: mention from display offset 11 to 25 (@git-committer)
        eid = store.add(11, 25, style_id=1)
        marks = store.get_in_range(0, 30)
        assert len(marks) == 1
        assert marks[0].start == 11
        assert marks[0].end == 25
        assert marks[0].style_id == 1

    def test_highlight_before_multiwidth(self) -> None:
        """Align: highlight text BEFORE multi-width chars (e.g. 'hello' at 0-5)."""
        store = ExtmarksStore()
        store.add(0, 5, style_id=1)
        marks = store.get_in_range(0, 10)
        assert len(marks) == 1
        assert marks[0].start == 0
        assert marks[0].end == 5

    def test_highlight_between_multiwidth(self) -> None:
        """Align: highlight BETWEEN multi-width chars (display offsets 3-7 for 'test')."""
        store = ExtmarksStore()
        store.add(3, 7, style_id=1)
        marks = store.get_in_range(0, 10)
        assert len(marks) == 1
        assert marks[0].start == 3
        assert marks[0].end == 7

    def test_multiple_highlights_multiwidth(self) -> None:
        """Align: multiple highlights with display-width offsets (@user1, @user2)."""
        store = ExtmarksStore()
        # Simulate two mentions at different display offsets
        store.add(6, 12, style_id=1)   # @user1
        store.add(18, 24, style_id=1)  # @user2
        marks = store.get_in_range(0, 30)
        assert len(marks) == 2
        marks_sorted = sorted(marks, key=lambda m: m.start)
        assert marks_sorted[0].start == 6 and marks_sorted[0].end == 12
        assert marks_sorted[1].start == 18 and marks_sorted[1].end == 24

    def test_get_in_range_overlap_multiwidth_offsets(self) -> None:
        """get_in_range returns marks overlapping [start, end) by display offset."""
        store = ExtmarksStore()
        store.add(10, 20, style_id=1)
        assert len(store.get_in_range(0, 15)) == 1
        assert len(store.get_in_range(15, 25)) == 1
        assert len(store.get_in_range(0, 10)) == 0
        assert len(store.get_in_range(20, 30)) == 0
