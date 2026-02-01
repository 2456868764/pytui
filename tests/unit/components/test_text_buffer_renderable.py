# tests/unit/components/test_text_buffer_renderable.py
# Aligns with OpenTUI renderables/TextBufferRenderable.ts - TextBufferRenderable API tests

import pytest

pytest.importorskip("pytui.components.text_buffer_renderable")


class TestTextBufferRenderable:
    def test_init_creates_text_buffer_and_view(self, mock_context):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 40, "height": 10})
        assert r.text_buffer is not None
        assert r.text_buffer_view is not None
        assert r.plain_text == ""
        assert r.text_length == 0

    def test_line_info_line_count_virtual_line_count(self, mock_context):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 40, "height": 5})
        r.text_buffer.set_text("a\nb\nc")
        assert r.line_count == 3
        assert r.virtual_line_count == 3
        info = r.line_info
        assert "line_starts" in info
        assert "max_line_width" in info
        assert len(info["line_starts"]) == 3

    def test_scroll_y_scroll_x(self, mock_context):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 10, "height": 3})
        # Use content so scroll_height > height and scroll_width > width for scroll tests
        r.text_buffer.set_text("line1\nline2\nline3\nline4\nline5")
        r.width = 10
        r.height = 3
        r._update_viewport()
        assert r.scroll_y == 0
        r.scroll_y = 1
        assert r.scroll_y == 1
        # scroll_x: need long line so scroll_width > width (e.g. 15 chars, width 10 -> max_sx=5)
        r.text_buffer.set_text("123456789012345\nline2\nline3")
        r._update_viewport()
        r.scroll_x = 2
        assert r.scroll_x == 2

    def test_get_selected_text_has_selection_get_selection(self, mock_context):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 40, "height": 5})
        r.text_buffer.set_text("hello world")
        assert r.has_selection() is False
        assert r.get_selection() is None
        assert r.get_selected_text() == ""
        r.text_buffer_view.set_selection(0, 5)
        assert r.has_selection() is True
        assert r.get_selection() == (0, 5)
        assert r.get_selected_text() == "hello"

    def test_plain_text_text_length(self, mock_context):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 40, "height": 5})
        r.text_buffer.set_text("abc")
        assert r.plain_text == "abc"
        assert r.text_length == 3

    def test_render_self_draws_lines(self, mock_context, buffer_10x5):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 10, "height": 3})
        r.text_buffer.set_text("Hi\nBye")
        r.x, r.y, r.width, r.height = 0, 0, 10, 3
        r._scroll_y = 0
        r.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "H"
        assert buffer_10x5.get_cell(1, 0).char == "i"
        assert buffer_10x5.get_cell(0, 1).char == "B"
        assert buffer_10x5.get_cell(1, 1).char == "y"
        assert buffer_10x5.get_cell(2, 1).char == "e"

    def test_destroy(self, mock_context):
        from pytui.components.text_buffer_renderable import TextBufferRenderable

        r = TextBufferRenderable(mock_context, {"width": 40, "height": 5})
        r.destroy()
        with pytest.raises(RuntimeError, match="destroyed"):
            r.text_buffer_view.line_info
        with pytest.raises(RuntimeError, match="destroyed"):
            r.text_buffer.get_plain_text()
