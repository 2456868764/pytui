# tests/unit/components/test_edit_buffer_renderable.py
# 与 OpenTUI EditBufferRenderable 对齐的组件测试

import pytest

pytest.importorskip("pytui.components.edit_buffer_renderable")


class TestEditBufferRenderable:
    def test_init_creates_edit_buffer_and_editor_view(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(mock_context, {"width": 40, "height": 10})
        assert r.edit_buffer is not None
        assert r.editor_view is not None
        assert r.edit_buffer.text == ""
        assert r.plain_text == ""

    def test_initial_text_and_set_text(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(mock_context, {"text": "hello", "width": 40, "height": 5})
        assert r.plain_text == "hello"
        r.set_text("world")
        assert r.plain_text == "world"

    def test_replace_text_and_undo(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(mock_context, {"text": "a", "width": 40, "height": 5})
        r.replace_text("ab")
        assert r.plain_text == "ab"
        assert r.edit_buffer.undo() is True
        assert r.plain_text == "a"

    def test_clear(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(mock_context, {"text": "x", "width": 40, "height": 5})
        r.clear()
        assert r.plain_text == ""
        assert r.edit_buffer.line_count == 1

    def test_line_count_virtual_line_count_scroll_y(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context, {"text": "a\nb\nc\nd", "width": 40, "height": 3}
        )
        assert r.line_count == 4
        assert r.virtual_line_count == 4
        assert r.scroll_y == 0
        r.scroll_y = 1
        assert r.scroll_y == 1

    def test_logical_cursor_visual_cursor_cursor_offset(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context, {"text": "ab\ncd", "width": 40, "height": 3}
        )
        row, col = r.logical_cursor
        assert row == 0 and col == 0
        r.cursor_offset = 3
        assert r.cursor_offset == 3
        row, col = r.logical_cursor
        assert row == 1 and col == 0
        vrow, vcol = r.visual_cursor
        assert vcol == 0

    def test_text_color_background_color_properties(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context,
            {
                "text": "x",
                "text_color": "#ff0000",
                "background_color": "#000000",
                "width": 40,
                "height": 5,
            },
        )
        assert r.text_color == (255, 0, 0, 255)
        assert r.background_color == (0, 0, 0, 255)
        r.text_color = "#00ff00"
        assert r.text_color == (0, 255, 0, 255)

    def test_selection_bg_fg_selectable_wrap_mode(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context,
            {
                "text": "x",
                "selection_bg": "#4444aa",
                "selectable": True,
                "wrap_mode": "word",
                "width": 40,
                "height": 5,
            },
        )
        assert r.selection_bg == (68, 68, 170, 255)
        assert r.selectable is True
        assert r.wrap_mode == "word"
        r.wrap_mode = "none"
        assert r.wrap_mode == "none"

    def test_show_cursor_cursor_color_cursor_style(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context,
            {
                "text": "x",
                "show_cursor": True,
                "cursor_color": "#ffffff",
                "cursor_style": {"style": "block", "blinking": True},
                "width": 40,
                "height": 5,
            },
        )
        assert r.show_cursor is True
        assert r.cursor_style.get("style") == "block"
        r.show_cursor = False
        assert r.show_cursor is False

    def test_insert_text_get_selected_text_has_selection(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(mock_context, {"text": "ab", "width": 40, "height": 5})
        r.cursor_offset = 1
        r.insert_text("X")
        assert r.plain_text == "aXb"
        assert r.has_selection() is False
        assert r.get_selected_text() == ""

    def test_get_text_range_get_text_range_by_coords(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context, {"text": "hello\nworld", "width": 40, "height": 5}
        )
        assert r.get_text_range(0, 5) == "hello"
        assert r.get_text_range_by_coords(0, 0, 1, 2) == "hello\nwo"

    def test_add_highlight_get_line_highlights_clear_all_highlights(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context, {"text": "a\nb", "width": 40, "height": 5}
        )
        r.add_highlight(0, {"start": 0, "end": 1, "style_id": 1})
        hl = r.get_line_highlights(0)
        assert len(hl) == 1
        assert "hl_ref" in hl[0]
        r.clear_all_highlights()
        assert r.get_line_highlights(0) == []

    def test_render_self_draws_content(self, mock_context, buffer_40x20):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context, {"text": "hello", "width": 40, "height": 5}
        )
        r.x, r.y, r.width, r.height = 0, 0, 40, 5
        r.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "h"
        assert buffer_40x20.get_cell(4, 0).char == "o"

    def test_should_start_selection(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context, {"text": "x", "width": 40, "height": 5, "selectable": True}
        )
        r.x, r.y, r.width, r.height = 0, 0, 40, 5
        assert r.should_start_selection(5, 2) is True
        assert r.should_start_selection(50, 2) is False
        r.selectable = False
        assert r.should_start_selection(5, 2) is False

    def test_camelCase_options(self, mock_context):
        from pytui.components.edit_buffer_renderable import EditBufferRenderable

        r = EditBufferRenderable(
            mock_context,
            {
                "text": "x",
                "textColor": "#ffffff",
                "backgroundColor": "transparent",
                "showCursor": True,
                "wrapMode": "word",
                "scrollMargin": 0.2,
                "scrollSpeed": 16,
                "width": 40,
                "height": 5,
            },
        )
        assert r.text_color == (255, 255, 255, 255)
        assert r.show_cursor is True
        assert r.wrap_mode == "word"
        assert r.scroll_speed == 16
