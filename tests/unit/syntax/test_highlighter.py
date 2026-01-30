# tests/unit/syntax/test_highlighter.py

import pytest

pytest.importorskip("pytui.syntax.highlighter")


class TestHighlighter:
    def test_highlight_returns_spans_with_joined_text_equal_input(self):
        from pytui.syntax.highlighter import highlight

        code = "def x(): pass"
        out = highlight(code)
        assert len(out) >= 1
        assert "".join(t for t, _ in out) == code

    def test_returns_plain_when_no_parser(self):
        from unittest.mock import patch
        from pytui.syntax.highlighter import highlight

        code = "hello"
        with patch("pytui.syntax.languages.get_parser", return_value=None):
            out = highlight(code, "python")
        assert out == [(code, "plain")]
