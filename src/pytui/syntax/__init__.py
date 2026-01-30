# pytui.syntax

from pytui.syntax.highlighter import highlight
from pytui.syntax.languages import get_language, get_parser
from pytui.syntax.style import SyntaxStyle, convert_theme_to_styles, get_default_styles
from pytui.syntax.themes import get_theme

__all__ = [
    "get_theme",
    "highlight",
    "get_language",
    "get_parser",
    "SyntaxStyle",
    "convert_theme_to_styles",
    "get_default_styles",
]
