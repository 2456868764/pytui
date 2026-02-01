# tests.unit.core.test_syntax_style - syntax_style (themes + style, migrated from syntax/)

import pytest

pytest.importorskip("pytui.core.syntax_style")


class TestThemes:
    def test_get_theme_default(self):
        from pytui.core.syntax_style import get_theme, get_theme_scope_colors

        theme = get_theme("default")
        assert isinstance(theme, list)
        scopes = [s for t in theme for s in t.get("scope", [])]
        assert "plain" in scopes
        assert "keyword" in scopes
        scope_colors = get_theme_scope_colors("default")
        assert "plain" in scope_colors
        assert "keyword" in scope_colors
        assert len(scope_colors["plain"]) == 4


class TestSyntaxStyle:
    def test_convert_theme_to_styles(self):
        from pytui.core.syntax_style import convert_theme_to_styles

        theme = [
            {"scope": ["keyword"], "style": {"foreground": (255, 0, 0, 255)}},
            {"scope": ["plain"], "style": {"foreground": (200, 200, 200, 255)}},
        ]
        styles = convert_theme_to_styles(theme)
        assert "keyword" in styles
        assert styles["keyword"]["fg"] == (255, 0, 0, 255)
        assert "plain" in styles
        assert styles["plain"]["fg"] == (200, 200, 200, 255)

    def test_get_default_styles(self):
        from pytui.core.syntax_style import get_default_styles

        s = get_default_styles()
        assert "keyword" in s
        assert "plain" in s


class TestSyntaxStyleClass:
    """Align OpenTUI SyntaxStyle class API."""

    def test_create(self):
        from pytui.core.syntax_style import SyntaxStyle

        s = SyntaxStyle.create()
        assert s.get_style_count() == 0
        assert s.get_registered_names() == []

    def test_register_style_get_style_get_style_id(self):
        from pytui.core.syntax_style import SyntaxStyle

        s = SyntaxStyle.create()
        sid = s.register_style("keyword", {"fg": (255, 0, 0, 255), "bold": True})
        assert sid is not None
        assert s.get_style_id("keyword") == sid
        style = s.get_style("keyword")
        assert style is not None
        assert style["fg"] == (255, 0, 0, 255)
        assert style["bold"] is True

    def test_get_style_scoped_fallback(self):
        from pytui.core.syntax_style import SyntaxStyle

        s = SyntaxStyle.create()
        s.register_style("keyword", {"fg": (255, 0, 0, 255)})
        assert s.get_style("keyword.builtin") is not None
        assert s.get_style("keyword.builtin")["fg"] == (255, 0, 0, 255)

    def test_merge_styles_and_cache(self):
        from pytui.core.syntax_style import SyntaxStyle

        s = SyntaxStyle.create()
        s.register_style("a", {"fg": (1, 2, 3, 255)})
        s.register_style("b", {"bold": True})
        m = s.merge_styles("a", "b")
        assert m["fg"] == (1, 2, 3, 255)
        assert m["attributes"] is not None
        assert s.get_cache_size() == 1
        s.clear_cache()
        assert s.get_cache_size() == 0

    def test_from_theme_from_styles(self):
        from pytui.core.syntax_style import SyntaxStyle, convert_theme_to_styles, get_theme

        theme_list = [{"scope": ["x"], "style": {"foreground": (10, 20, 30, 255)}}]
        s = SyntaxStyle.from_theme(theme_list)
        assert "x" in s.get_registered_names()
        assert s.get_style("x")["fg"] == (10, 20, 30, 255)
        flat = convert_theme_to_styles(get_theme("default"))
        s2 = SyntaxStyle.from_styles(flat)
        assert "keyword" in s2.get_registered_names()

    def test_destroy_clears_and_raises_on_use(self):
        import pytest
        from pytui.core.syntax_style import SyntaxStyle

        s = SyntaxStyle.create()
        s.register_style("k", {"fg": (0, 0, 0, 255)})
        s.destroy()
        with pytest.raises(RuntimeError, match="destroyed"):
            s.get_style("k")
