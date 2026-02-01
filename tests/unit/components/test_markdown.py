# tests/unit/components/test_markdown.py
# Aligns with OpenTUI renderables/Markdown.ts - MarkdownRenderable API tests

import pytest

pytest.importorskip("pytui.components.markdown")


class TestMarkdownRenderable:
    def test_init_empty_content(self, mock_context):
        from pytui.components.markdown import MarkdownRenderable

        m = MarkdownRenderable(mock_context, {})
        assert m.content == ""
        assert m.conceal is True
        assert m.streaming is False
        assert len(m.get_children()) == 0

    def test_init_with_content(self, mock_context):
        from pytui.components.markdown import MarkdownRenderable

        m = MarkdownRenderable(mock_context, {"content": "# Hello"})
        assert m.content == "# Hello"
        assert len(m.get_children()) == 1

    def test_content_setter_triggers_update(self, mock_context):
        from pytui.components.markdown import MarkdownRenderable

        m = MarkdownRenderable(mock_context, {"content": "a"})
        m.request_render = lambda: None
        m.content = "b"
        assert m.content == "b"
        assert len(m.get_children()) == 1

    def test_syntax_style_setter(self, mock_context):
        from pytui.components.markdown import MarkdownRenderable

        m = MarkdownRenderable(mock_context, {"content": "x"})
        m.request_render = lambda: None
        m.syntax_style = "monokai"
        assert m.syntax_style == "monokai"

    def test_conceal_streaming_setters(self, mock_context):
        from pytui.components.markdown import MarkdownRenderable

        m = MarkdownRenderable(mock_context, {"content": "x", "conceal": False, "streaming": True})
        assert m.conceal is False
        assert m.streaming is True

    def test_clear_cache(self, mock_context):
        from pytui.components.markdown import MarkdownRenderable

        m = MarkdownRenderable(mock_context, {"content": "foo"})
        m.request_render = lambda: None
        m.clear_cache()
        assert len(m.get_children()) == 1
