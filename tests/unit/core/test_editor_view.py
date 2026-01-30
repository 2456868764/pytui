# tests.unit.core.test_editor_view - EditorView viewport, cursor, selection

import pytest

pytest.importorskip("pytui.core.editor_view")


class TestEditorView:
    def test_cursor_and_scroll(self):
        from pytui.core.edit_buffer import EditBuffer
        from pytui.core.editor_view import EditorView

        buf = EditBuffer("a\nbc\ndef")
        view = EditorView(buf, view_width=10, view_height=2)
        assert view.cursor_pos == 0
        view.cursor_pos = 4
        assert view.cursor_line == 1
        assert view.cursor_col == 2
        view.scroll_y = 1
        assert view.get_visible_lines() == ["bc", "def"]

    def test_insert_delete_undo(self):
        from pytui.core.edit_buffer import EditBuffer
        from pytui.core.editor_view import EditorView

        buf = EditBuffer("ab")
        view = EditorView(buf, view_width=10, view_height=2)
        view.cursor_pos = 1
        view.insert("X")
        assert buf.text == "aXb"
        view.delete_backward()
        assert buf.text == "ab"
        view.undo()
        assert buf.text == "aXb"

    def test_selection(self):
        from pytui.core.edit_buffer import EditBuffer
        from pytui.core.editor_view import EditorView

        buf = EditBuffer("hello")
        view = EditorView(buf, view_width=10, view_height=2)
        view.set_selection(0, 3)
        assert view.get_selection_range() == (0, 3)
        view.insert("x")
        assert buf.text == "xlo"
        assert view.cursor_pos == 1
