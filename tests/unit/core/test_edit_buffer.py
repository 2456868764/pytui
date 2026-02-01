# tests.unit.core.test_edit_buffer - Aligns with OpenTUI packages/core/src/edit-buffer.test.ts
# EditBuffer create, setText, getText, getCursorPosition, setCursorToLineCol, moveCursor*, gotoLine, destroy.

import pytest

pytest.importorskip("pytui.core.edit_buffer")


class TestEditBuffer:
    @pytest.fixture
    def buffer(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer.create("wcwidth")
        yield buf
        buf.destroy()

    def test_set_text_and_get_text(self, buffer):
        buffer.set_text("Hello World")
        assert buffer.get_text() == "Hello World"

    def test_handle_empty_text(self, buffer):
        buffer.set_text("")
        assert buffer.get_text() == ""

    def test_handle_text_with_newlines(self, buffer):
        text = "Line 1\nLine 2\nLine 3"
        buffer.set_text(text)
        assert buffer.get_text() == text

    def test_handle_unicode_characters(self, buffer):
        text = "Hello 世界 🌟"
        buffer.set_text(text)
        assert buffer.get_text() == text

    def test_cursor_at_beginning_after_set_text(self, buffer):
        buffer.set_text("Hello World")
        cursor = buffer.get_cursor_position()
        assert cursor["row"] == 0
        assert cursor["col"] == 0

    def test_track_cursor_after_movements(self, buffer):
        buffer.set_text("Hello World")
        buffer.move_cursor_right()
        cursor = buffer.get_cursor_position()
        assert cursor["col"] == 1
        buffer.move_cursor_right()
        cursor = buffer.get_cursor_position()
        assert cursor["col"] == 2

    def test_multi_line_cursor_positions(self, buffer):
        buffer.set_text("Line 1\nLine 2\nLine 3")
        buffer.move_cursor_down()
        cursor = buffer.get_cursor_position()
        assert cursor["row"] == 1
        buffer.move_cursor_down()
        cursor = buffer.get_cursor_position()
        assert cursor["row"] == 2

    def test_move_cursor_left_and_right(self, buffer):
        buffer.set_text("ABCDE")
        buffer.set_cursor_to_line_col(0, 5)
        assert buffer.get_cursor_position()["col"] == 5
        buffer.move_cursor_left()
        assert buffer.get_cursor_position()["col"] == 4
        buffer.move_cursor_left()
        assert buffer.get_cursor_position()["col"] == 3

    def test_move_cursor_up_and_down(self, buffer):
        buffer.set_text("Line 1\nLine 2\nLine 3")
        buffer.move_cursor_down()
        assert buffer.get_cursor_position()["row"] == 1
        buffer.move_cursor_down()
        assert buffer.get_cursor_position()["row"] == 2
        buffer.move_cursor_up()
        assert buffer.get_cursor_position()["row"] == 1

    def test_goto_line(self, buffer):
        buffer.set_text("Line 1\nLine 2\nLine 3")
        buffer.goto_line(1)
        assert buffer.get_cursor_position()["row"] == 1
        buffer.goto_line(2)
        assert buffer.get_cursor_position()["row"] == 2

    def test_destroy_twice_no_op(self, buffer):
        buffer.destroy()
        buffer.destroy()

    def test_after_destroy_raises(self):
        from pytui.core.edit_buffer import EditBuffer

        buf = EditBuffer.create("wcwidth")
        buf.destroy()
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.get_text()
        with pytest.raises(RuntimeError, match="destroyed"):
            buf.get_cursor_position()

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
