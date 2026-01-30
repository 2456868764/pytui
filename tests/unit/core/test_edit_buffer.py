# tests.unit.core.test_edit_buffer - EditBuffer insert/delete/undo/redo

import pytest

pytest.importorskip("pytui.core.edit_buffer")


class TestEditBuffer:
    def test_init_empty(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer()
        assert buf.text == ""
        assert buf.get_lines() == [""]
        assert buf.line_count == 1

    def test_init_with_text(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("a\nb\nc")
        assert buf.text == "a\nb\nc"
        assert buf.get_lines() == ["a", "b", "c"]
        assert buf.line_count == 3

    def test_insert(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("ab")
        buf.insert(1, "X")
        assert buf.text == "aXb"
        buf.insert(0, "!")
        assert buf.text == "!aXb"
        buf.insert(10, "z")
        assert buf.text == "!aXbz"

    def test_delete(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("hello")
        deleted = buf.delete(1, 4)
        assert deleted == "ell"
        assert buf.text == "ho"
        assert buf.delete(0, 0) == ""
        assert buf.text == "ho"

    def test_undo_insert(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("ab")
        buf.insert(1, "X")
        assert buf.text == "aXb"
        assert buf.undo() is True
        assert buf.text == "ab"
        assert buf.undo() is False

    def test_undo_delete(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("hello")
        buf.delete(1, 4)
        assert buf.text == "ho"
        assert buf.undo() is True
        assert buf.text == "hello"

    def test_redo(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("ab")
        buf.insert(1, "X")
        buf.undo()
        assert buf.text == "ab"
        assert buf.redo() is True
        assert buf.text == "aXb"
        assert buf.redo() is False

    def test_redo_cleared_on_new_edit(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("a")
        buf.insert(1, "b")
        buf.undo()
        buf.insert(1, "c")
        assert buf.text == "ac"
        assert buf.redo() is False
        assert buf.text == "ac"

    def test_set_text_clears_history(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("a")
        buf.insert(1, "b")
        buf.set_text("x")
        assert buf.text == "x"
        assert buf.undo() is False

    def test_pos_to_line_col(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("a\nbc\n")
        assert buf.pos_to_line_col(0) == (0, 0)
        assert buf.pos_to_line_col(1) == (0, 1)
        assert buf.pos_to_line_col(2) == (1, 0)
        assert buf.pos_to_line_col(4) == (1, 2)
        assert buf.pos_to_line_col(5) == (2, 0)

    def test_line_col_to_pos(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer("a\nbc\n")
        assert buf.line_col_to_pos(0, 0) == 0
        assert buf.line_col_to_pos(0, 1) == 1
        assert buf.line_col_to_pos(1, 0) == 2
        assert buf.line_col_to_pos(1, 2) == 4
        assert buf.line_col_to_pos(2, 0) == 5
