# tests/unit/syntax/test_themes.py

import pytest

pytest.importorskip("pytui.syntax.themes")


class TestThemes:
    def test_get_theme_default(self):
        from pytui.syntax.themes import get_theme

        theme = get_theme("default")
        assert "plain" in theme
        assert "keyword" in theme
        assert len(theme["plain"]) == 4
