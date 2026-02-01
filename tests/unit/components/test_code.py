# tests/unit/components/test_code.py

import pytest

pytest.importorskip("pytui.components.code")


class TestCode:
    def test_render_self_shows_content(self, mock_context, buffer_40x20):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "x = 1", "width": 40, "height": 5})
        c.x, c.y, c.width, c.height = 0, 0, 40, 5
        c.render_self(buffer_40x20)
        found = False
        for y in range(5):
            for x in range(40):
                cell = buffer_40x20.get_cell(x, y)
                if cell and (cell.char == "x" or cell.char == "1"):
                    found = True
                    break
            if found:
                break
        assert found

    def test_filetype_alias_and_property(self, mock_context):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "", "filetype": "javascript"})
        assert c.language == "javascript"
        assert c.filetype == "javascript"
        c.filetype = "python"
        assert c.language == "python"

    def test_syntax_style_and_theme(self, mock_context):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "x", "syntax_style": "default"})
        assert c.syntax_style == "default"
        c.syntax_style = "dark"
        assert c.syntax_style == "dark"

    def test_conceal_draw_unstyled_streaming_defaults(self, mock_context):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "a"})
        assert c.conceal is True
        assert c.draw_unstyled_text is True
        assert c.streaming is False
        assert c.is_highlighting is False

    def test_get_line_highlights(self, mock_context):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "x = 1\ny = 2", "language": "python"})
        spans = c.get_line_highlights(0)
        assert isinstance(spans, list)
        assert all(isinstance(s, tuple) and len(s) == 2 for s in spans)
        text = "".join(s[0] for s in spans)
        assert "x" in text or "1" in text
        spans1 = c.get_line_highlights(1)
        text1 = "".join(s[0] for s in spans1)
        assert "y" in text1 or "2" in text1
        assert c.get_line_highlights(-1) == []
        assert c.get_line_highlights(10) == []

    def test_camelCase_aliases(self, mock_context):
        from pytui.components.code import Code

        c = Code(
            mock_context,
            {
                "content": "x",
                "syntaxStyle": "default",
                "drawUnstyledText": False,
                "streaming": True,
            },
        )
        assert c.syntax_style == "default"
        assert c.draw_unstyled_text is False
        assert c.streaming is True

    def test_content_getter_setter(self, mock_context):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "a"})
        assert c.content == "a"
        c.content = "b"
        assert c.content == "b"

    def test_fg_bg_text_buffer_options(self, mock_context):
        from pytui.components.code import Code

        c = Code(
            mock_context,
            {"content": "x", "fg": "#ff0000", "bg": "#000000", "wrap_mode": "word"},
        )
        assert c.fg == (255, 0, 0, 255)
        assert c.bg == (0, 0, 0, 255)
        assert c.wrap_mode == "word"
        c.fg = "#00ff00"
        assert c.fg == (0, 255, 0, 255)
        assert c.selectable is True

    def test_streaming_setter_clears_state(self, mock_context):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "x", "filetype": "python", "streaming": True})
        c.render_self(__import__("pytui.core.buffer", fromlist=["OptimizedBuffer"]).OptimizedBuffer(80, 24))
        c.streaming = False
        assert c.streaming is False
        assert c._last_highlights == []

    def test_get_line_highlights_after_render(self, mock_context, buffer_40x20):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "def f():\n    pass", "filetype": "python"})
        c.x, c.y, c.width, c.height = 0, 0, 40, 5
        c.render_self(buffer_40x20)
        hl0 = c.get_line_highlights(0)
        hl1 = c.get_line_highlights(1)
        assert isinstance(hl0, list) and all(isinstance(s, tuple) and len(s) == 2 for s in hl0)
        assert "def" in "".join(s[0] for s in hl0) or "f" in "".join(s[0] for s in hl0)
        assert "pass" in "".join(s[0] for s in hl1) or len(hl1) >= 1
