# tests/unit/components/test_textarea.py

import pytest

pytest.importorskip("pytui.components.textarea")


class TestTextarea:
    def test_scroll_y(self, mock_context):
        from pytui.components.textarea import Textarea

        t = Textarea(
            mock_context,
            {"content": "a\nb\nc\nd\ne", "width": 20, "height": 3},
        )
        t.set_scroll_y(2)
        assert t.scroll_y == 2

    def test_render_self_respects_scroll(self, mock_context, buffer_40x20):
        from pytui.components.textarea import Textarea

        t = Textarea(
            mock_context,
            {"content": "line1\nline2\nline3", "width": 20, "height": 3},
        )
        t.x, t.y, t.width, t.height = 0, 0, 20, 3
        t.scroll_y = 1
        t.render_self(buffer_40x20)
        # 第一行应为 line2
        assert buffer_40x20.get_cell(0, 0).char == "l"
        assert buffer_40x20.get_cell(4, 0).char == "2"

    def test_with_edit_buffer(self, mock_context, buffer_40x20):
        from pytui.core.edit_buffer import EditBuffer
        from pytui.components.textarea import Textarea

        buf = EditBuffer()
        buf.set_text("one\ntwo\nthree\nfour")
        t = Textarea(mock_context, {"buffer": buf, "width": 20, "height": 3})
        t.x, t.y, t.width, t.height = 0, 0, 20, 3
        t.set_scroll_y(1)
        t.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "t"
        assert buffer_40x20.get_cell(2, 0).char == "o"
        buf.insert(0, "x")
        assert t.undo() is True
        assert t.redo() is True
        assert t.undo() is True

    def test_with_editor_view(self, mock_context, buffer_40x20):
        from pytui.core.edit_buffer import EditBuffer
        from pytui.core.editor_view import EditorView
        from pytui.components.textarea import Textarea

        buf = EditBuffer()
        buf.set_text("a\nbc\nd")
        ev = EditorView(buf, view_width=10, view_height=2)
        ev.set_cursor_line_col(1, 1)
        t = Textarea(mock_context, {"editor_view": ev, "width": 10, "height": 2})
        t.x, t.y, t.width, t.height = 0, 0, 10, 2
        t.render_self(buffer_40x20)
        # 光标在 (1,1) 即 'c'
        assert buffer_40x20.get_cell(1, 1).char == "c"
        assert t.undo() is False
        buf.insert(0, "x")
        assert t.undo() is True
