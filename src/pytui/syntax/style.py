# pytui.syntax.style - SyntaxStyle / convertThemeToStyles（主题→样式映射）


from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# RGBA tuple
ColorTuple = tuple[int, int, int, int]


@dataclass
class SyntaxStyle:
    """单类 token 的样式：前景、背景、粗体等。"""

    fg: ColorTuple = (220, 220, 220, 255)
    bg: ColorTuple = (0, 0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = False


def convert_theme_to_styles(theme: dict[str, ColorTuple]) -> dict[str, SyntaxStyle]:
    """将主题（token_type -> (r,g,b,a)）转为 token_type -> SyntaxStyle。"""
    return {
        token: SyntaxStyle(fg=color, bg=(0, 0, 0, 0))
        for token, color in theme.items()
    }


def get_default_styles() -> dict[str, SyntaxStyle]:
    """返回默认主题对应的 styles。"""
    from pytui.syntax.themes import get_theme

    return convert_theme_to_styles(get_theme("default"))
