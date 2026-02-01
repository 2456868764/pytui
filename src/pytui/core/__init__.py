# pytui.core - Aligns OpenTUI packages/core/src/index.ts export order
# Renderable, types, utils, buffer, edit_buffer, editor_view, syntax_style, animation, lib, renderer, console, terminal

from pytui.core.renderable import (
    ADDED,
    BLURRED,
    FOCUSED,
    LAYOUT_CHANGED,
    REMOVED,
    RESIZED,
    LayoutEvents,
    Renderable,
    RenderableEvents,
)
from pytui.core import types
from pytui.core import utils
from pytui.core.ansi import ANSI
from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.text_buffer import TextBuffer
from pytui.core.text_buffer_view import TextBufferView
from pytui.core.edit_buffer import EditBuffer
from pytui.core.editor_view import EditorView
from pytui.core.syntax_style import (
    MergedStyle,
    StyleDefinition,
    SyntaxStyle,
    SyntaxStyleFromTheme,
    ThemeTokenStyle,
    convert_theme_to_styles,
    get_default_styles,
    get_theme,
)
from pytui.core.animation import (
    Timeline,
    TimelineOptions,
    JSAnimation,
    EASING_FUNCTIONS,
    engine,
    create_timeline,
)
from pytui.lib import (
    RGBA,
    TerminalPalette,
    create_terminal_palette,
    detect_capability,
    get_palette_color,
    hex_to_rgb,
    parse_color,
    rgb_to_hex,
)
from pytui.core.renderer import Renderer
from pytui.core.console import Console
from pytui.core.terminal import (
    Terminal,
    is_capability_response,
    is_pixel_resolution_response,
    parse_pixel_resolution,
)
from pytui.core.events import EventBus

__all__ = [
    # Renderable (OpenTUI index order)
    "Renderable",
    "LayoutEvents",
    "RenderableEvents",
    "LAYOUT_CHANGED",
    "ADDED",
    "REMOVED",
    "RESIZED",
    "FOCUSED",
    "BLURRED",
    "types",
    "utils",
    "ANSI",
    "Cell",
    "OptimizedBuffer",
    "TextBuffer",
    "TextBufferView",
    "EditBuffer",
    "EditorView",
    "MergedStyle",
    "StyleDefinition",
    "SyntaxStyle",
    "SyntaxStyleFromTheme",
    "ThemeTokenStyle",
    "convert_theme_to_styles",
    "get_default_styles",
    "get_theme",
    "Timeline",
    "TimelineOptions",
    "JSAnimation",
    "EASING_FUNCTIONS",
    "engine",
    "create_timeline",
    "RGBA",
    "hex_to_rgb",
    "rgb_to_hex",
    "detect_capability",
    "get_palette_color",
    "TerminalPalette",
    "create_terminal_palette",
    "Renderer",
    "Console",
    "Terminal",
    "is_capability_response",
    "is_pixel_resolution_response",
    "parse_pixel_resolution",
    "EventBus",
]
