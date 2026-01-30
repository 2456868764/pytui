# tests/unit/syntax/test_style.py

import pytest

pytest.importorskip("pytui.syntax.style")


class TestSyntaxStyle:
    def test_convert_theme_to_styles(self):
        from pytui.syntax.style import convert_theme_to_styles

        theme = {"keyword": (255, 0, 0, 255), "plain": (200, 200, 200, 255)}
        styles = convert_theme_to_styles(theme)
        assert "keyword" in styles
        assert styles["keyword"].fg == (255, 0, 0, 255)
        assert styles["plain"].fg == (200, 200, 200, 255)

    def test_get_default_styles(self):
        from pytui.syntax.style import get_default_styles

        s = get_default_styles()
        assert "keyword" in s
        assert "plain" in s
