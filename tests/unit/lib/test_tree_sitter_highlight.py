# tests.unit.lib.test_tree_sitter_highlight - highlight() sync (migrated from syntax/highlighter)

import pytest
from unittest.mock import patch

pytest.importorskip("pytui.lib.tree_sitter")


class TestHighlight:
    def test_highlight_returns_spans_with_joined_text_equal_input(self):
        from pytui.lib.tree_sitter import highlight

        code = "def x(): pass"
        out = highlight(code)
        assert len(out) >= 1
        assert "".join(t for t, _ in out) == code

    def test_returns_plain_when_no_parser(self):
        from pytui.lib.tree_sitter import highlight

        code = "hello"
        with patch("pytui.lib.tree_sitter.languages.get_parser", return_value=None):
            out = highlight(code, "python")
        assert out == [(code, "plain")]
