# pytui.core.syntax_style - Aligns OpenTUI core/syntax-style.ts
# StyleDefinition, MergedStyle, ThemeTokenStyle, convertThemeToStyles, SyntaxStyle class (no native ptr)

from __future__ import annotations

from typing import Any, TypedDict

from pytui.lib.rgba import RGBA, parse_color
from pytui.lib.styled_text import create_text_attributes

# RGBA tuple (r, g, b, a) 0-255
ColorTuple = tuple[int, int, int, int]

# ColorInput: str (hex) or tuple/RGBA
ColorInput = str | ColorTuple | RGBA


class StyleDefinition(TypedDict, total=False):
    """Align OpenTUI StyleDefinition. fg/bg optional; attributes optional."""

    fg: ColorTuple | RGBA
    bg: ColorTuple | RGBA
    bold: bool
    italic: bool
    underline: bool
    dim: bool


class MergedStyle(TypedDict, total=False):
    """Align OpenTUI MergedStyle. fg, bg optional; attributes required (int bitmask)."""

    fg: ColorTuple | RGBA
    bg: ColorTuple | RGBA
    attributes: int


class ThemeTokenStyle(TypedDict, total=False):
    """Align OpenTUI ThemeTokenStyle. scope list + style dict."""

    scope: list[str]
    style: dict[str, Any]  # foreground?, background?, bold?, italic?, underline?, dim?


def _to_tuple(c: ColorInput) -> ColorTuple:
    """Normalize ColorInput to (r,g,b,a)."""
    if isinstance(c, (tuple, list)) and len(c) >= 4:
        return (int(c[0]), int(c[1]), int(c[2]), int(c[3]))
    if isinstance(c, (tuple, list)) and len(c) == 3:
        return (int(c[0]), int(c[1]), int(c[2]), 255)
    if hasattr(c, "r"):
        return (c.r, c.g, c.b, c.a)  # type: ignore[attr-defined]
    rgb = parse_color(c)
    return rgb.to_tuple() if hasattr(rgb, "to_tuple") else (rgb.r, rgb.g, rgb.b, rgb.a)


def convert_theme_to_styles(theme: list[ThemeTokenStyle]) -> dict[str, StyleDefinition]:
    """Convert theme to flat scope -> StyleDefinition. Aligns OpenTUI convertThemeToStyles(theme: ThemeTokenStyle[])."""
    flat: dict[str, StyleDefinition] = {}
    for token_style in theme:
        style_dict = token_style.get("style") or {}
        scope_list = token_style.get("scope") or []
        style_def: StyleDefinition = {}
        if style_dict.get("foreground") is not None:
            style_def["fg"] = _to_tuple(style_dict["foreground"])  # type: ignore[assignment]
        if style_dict.get("background") is not None:
            style_def["bg"] = _to_tuple(style_dict["background"])  # type: ignore[assignment]
        if "bold" in style_dict:
            style_def["bold"] = bool(style_dict["bold"])
        if "italic" in style_dict:
            style_def["italic"] = bool(style_dict["italic"])
        if "underline" in style_dict:
            style_def["underline"] = bool(style_dict["underline"])
        if "dim" in style_dict:
            style_def["dim"] = bool(style_dict["dim"])
        for scope in scope_list:
            flat[scope] = style_def
    return flat


# Built-in themes as list[ThemeTokenStyle]. Aligns OpenTUI (theme is ThemeTokenStyle[] only).
_DEFAULT_PLAIN: ColorTuple = (220, 220, 220, 255)

DEFAULT_THEME: list[ThemeTokenStyle] = [
    {"scope": ["keyword"], "style": {"foreground": (204, 120, 50, 255)}},
    {"scope": ["string"], "style": {"foreground": (206, 145, 120, 255)}},
    {"scope": ["comment"], "style": {"foreground": (106, 153, 85, 255)}},
    {"scope": ["number"], "style": {"foreground": (181, 206, 168, 255)}},
    {"scope": ["function"], "style": {"foreground": (220, 220, 170, 255)}},
    {"scope": ["plain"], "style": {"foreground": _DEFAULT_PLAIN}},
]

DARK_THEME: list[ThemeTokenStyle] = [
    {"scope": ["keyword"], "style": {"foreground": (197, 134, 192, 255)}},
    {"scope": ["string"], "style": {"foreground": (152, 195, 121, 255)}},
    {"scope": ["comment"], "style": {"foreground": (127, 132, 142, 255)}},
    {"scope": ["number"], "style": {"foreground": (209, 154, 102, 255)}},
    {"scope": ["function"], "style": {"foreground": (97, 175, 239, 255)}},
    {"scope": ["plain"], "style": {"foreground": _DEFAULT_PLAIN}},
]

_THEMES: dict[str, list[ThemeTokenStyle]] = {
    "default": DEFAULT_THEME,
    "dark": DARK_THEME,
}


def get_theme(name: str = "default") -> list[ThemeTokenStyle]:
    """Return built-in theme as ThemeTokenStyle[]. Aligns OpenTUI (theme is ThemeTokenStyle[])."""
    return list(_THEMES.get(name, _THEMES["default"]))


def get_theme_scope_colors(name: str = "default") -> dict[str, ColorTuple]:
    """Flat scope -> fg ColorTuple for code/diff/textarea (from convert_theme_to_styles + fg only)."""
    flat = convert_theme_to_styles(get_theme(name))
    return {
        scope: (style_def.get("fg") or _DEFAULT_PLAIN)
        for scope, style_def in flat.items()
    }


def get_default_styles() -> dict[str, StyleDefinition]:
    """Return default theme as flat scope -> StyleDefinition. Aligns OpenTUI."""
    return convert_theme_to_styles(get_theme("default"))


class SyntaxStyle:
    """Align OpenTUI SyntaxStyle class. No native ptr; same API: registerStyle, getStyle, mergeStyles, etc."""

    def __init__(self, lib: Any = None, ptr: Any = None) -> None:
        """Constructor(lib, ptr). Aligns OpenTUI; lib/ptr ignored in Python (no native)."""
        self._destroyed = False
        self._name_cache: dict[str, int] = {}
        self._style_defs: dict[str, StyleDefinition] = {}
        self._merged_cache: dict[str, MergedStyle] = {}
        self._next_id = 0

    @classmethod
    def create(cls) -> "SyntaxStyle":
        """Static create(). Aligns OpenTUI SyntaxStyle.create()."""
        return cls()

    @classmethod
    def from_theme(cls, theme: list[ThemeTokenStyle]) -> "SyntaxStyle":
        """Static fromTheme(theme). Aligns OpenTUI SyntaxStyle.fromTheme()."""
        inst = cls.create()
        flat = convert_theme_to_styles(theme)
        for name, style_def in flat.items():
            inst.register_style(name, style_def)
        return inst

    @classmethod
    def from_styles(cls, styles: dict[str, StyleDefinition]) -> "SyntaxStyle":
        """Static fromStyles(styles). Aligns OpenTUI SyntaxStyle.fromStyles()."""
        inst = cls.create()
        for name, style_def in styles.items():
            inst.register_style(name, style_def)
        return inst

    def _guard(self) -> None:
        if self._destroyed:
            raise RuntimeError("NativeSyntaxStyle is destroyed")

    def register_style(self, name: str, style: StyleDefinition) -> int:
        """registerStyle(name, style). Aligns OpenTUI; returns numeric id."""
        self._guard()
        attrs = create_text_attributes(
            bold=style.get("bold", False),
            italic=style.get("italic", False),
            underline=style.get("underline", False),
            dim=style.get("dim", False),
        )
        self._next_id += 1
        self._name_cache[name] = self._next_id
        self._style_defs[name] = dict(style)
        return self._next_id

    def resolve_style_id(self, name: str) -> int | None:
        """resolveStyleId(name). Aligns OpenTUI."""
        self._guard()
        return self._name_cache.get(name)

    def get_style_id(self, name: str) -> int | None:
        """getStyleId(name). Tries base name if scoped. Aligns OpenTUI."""
        self._guard()
        vid = self.resolve_style_id(name)
        if vid is not None:
            return vid
        if "." in name:
            return self.resolve_style_id(name.split(".")[0])
        return None

    @property
    def ptr(self) -> Any:
        """ptr property. Aligns OpenTUI; returns None in Python (no native)."""
        self._guard()
        return None

    def get_style_count(self) -> int:
        """getStyleCount(). Aligns OpenTUI."""
        self._guard()
        return len(self._style_defs)

    def clear_name_cache(self) -> None:
        """clearNameCache(). Aligns OpenTUI."""
        self._name_cache.clear()

    def get_style(self, name: str) -> StyleDefinition | None:
        """getStyle(name). Returns StyleDefinition or None; tries base scope if name contains '.'. Aligns OpenTUI."""
        self._guard()
        if name in self._style_defs:
            return dict(self._style_defs[name])
        if "." in name:
            base = name.split(".")[0]
            if base in self._style_defs:
                return dict(self._style_defs[base])
        return None

    def merge_styles(self, *style_names: str) -> MergedStyle:
        """mergeStyles(...styleNames). Aligns OpenTUI."""
        self._guard()
        cache_key = ":".join(style_names)
        if cache_key in self._merged_cache:
            return self._merged_cache[cache_key]
        style_def: StyleDefinition = {}
        for name in style_names:
            s = self.get_style(name)
            if not s:
                continue
            if s.get("fg") is not None:
                style_def["fg"] = s["fg"]
            if s.get("bg") is not None:
                style_def["bg"] = s["bg"]
            if "bold" in s:
                style_def["bold"] = s["bold"]
            if "italic" in s:
                style_def["italic"] = s["italic"]
            if "underline" in s:
                style_def["underline"] = s["underline"]
            if "dim" in s:
                style_def["dim"] = s["dim"]
        attrs = create_text_attributes(
            bold=style_def.get("bold", False),
            italic=style_def.get("italic", False),
            underline=style_def.get("underline", False),
            dim=style_def.get("dim", False),
        )
        merged: MergedStyle = {
            "fg": style_def.get("fg"),
            "bg": style_def.get("bg"),
            "attributes": attrs,
        }
        self._merged_cache[cache_key] = merged
        return merged

    def clear_cache(self) -> None:
        """clearCache(). Aligns OpenTUI."""
        self._guard()
        self._merged_cache.clear()

    def get_cache_size(self) -> int:
        """getCacheSize(). Aligns OpenTUI."""
        self._guard()
        return len(self._merged_cache)

    def get_all_styles(self) -> dict[str, StyleDefinition]:
        """getAllStyles(). Aligns OpenTUI; returns dict (Map equivalent)."""
        self._guard()
        return {k: dict(v) for k, v in self._style_defs.items()}

    def get_registered_names(self) -> list[str]:
        """getRegisteredNames(). Aligns OpenTUI."""
        self._guard()
        return list(self._style_defs.keys())

    def destroy(self) -> None:
        """destroy(). Aligns OpenTUI."""
        if self._destroyed:
            return
        self._destroyed = True
        self._name_cache.clear()
        self._style_defs.clear()
        self._merged_cache.clear()


# Backward compat: tree_sitter_styled_text expects get_style(name) -> dict with fg, bg, bold, italic, underline, dim
class SyntaxStyleFromTheme(SyntaxStyle):
    """SyntaxStyle from built-in theme name; get_style(name) for tree_sitter_styled_text. Backward compat."""

    def __init__(self, theme_name: str = "default") -> None:
        super().__init__()
        theme_list = get_theme(theme_name)
        flat = convert_theme_to_styles(theme_list)
        for name, style_def in flat.items():
            self.register_style(name, style_def)
