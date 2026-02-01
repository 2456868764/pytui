# pytui.lib - Unified lib exports (aligns with OpenTUI lib/index.ts)
# Export order in __all__ follows OpenTUI index.ts: border, KeyHandler, ascii.font, RGBA,
# parse.keypress, scroll-acceleration, stdin-buffer, styled-text, parse.mouse, selection,
# env, tree-sitter-styled-text, tree-sitter, data-paths, extmarks, terminal-palette, then rest.
# Import order below follows dependency order to avoid cycles.

from __future__ import annotations

# --- OpenTUI index order 1: border ---
from pytui.lib.border import (
    VALID_BORDER_STYLES,
    BorderCharArrays,
    BorderCharacters,
    BorderChars,
    BorderSides,
    BorderSidesConfig,
    BorderStyle,
    border_chars_to_array,
    get_border_from_sides,
    get_border_sides,
    is_valid_border_style,
    parse_border_style,
)
# --- OpenTUI index order 3: ascii.font ---
from pytui.lib.ascii_font import (
    FONT_NAMES,
    coordinate_to_character_index,
    fonts,
    get_character_positions,
    measure_text,
)
from pytui.lib.singleton import destroy_singleton, has_singleton, singleton
from pytui.lib.validate_dir_name import is_valid_directory_name

# --- Env (uses singleton) ---
from pytui.lib.env import (
    clear_env_cache,
    env,
    generate_env_colored,
    generate_env_markdown,
    register_env_var,
)

# --- Data paths (uses env, singleton, validate_dir_name) ---
from pytui.lib.data_paths import (
    DataPathsManager,
    ensure_cache_dir,
    ensure_data_dir,
    get_cache_dir,
    get_data_dir,
    get_data_paths,
)

# --- RGBA, parse, scroll, stdin, styled-text, parse.mouse, selection ---
from pytui.lib.rgba import RGBA, hex_to_rgb, hsv_to_rgb, parse_color, parse_color_to_tuple, rgb_to_hex
from pytui.lib.parse_keypress import (
    KeyEventType,
    ParsedKey,
    non_alphanumeric_keys,
    parse_keypress,
)
from pytui.lib.scroll_acceleration import LinearScrollAccel, MacOSScrollAccel, ScrollAcceleration
from pytui.lib.stdin_buffer import StdinBuffer
from pytui.lib.styled_text import (
    StyledText,
    TextAttributes,
    create_text_attributes,
    is_styled_text,
    string_to_styled_text,
)
from pytui.lib.parse_mouse import MouseParser, RawMouseEvent, ScrollInfo
from pytui.lib.selection import (
    ASCIIFontSelectionHelper,
    LocalSelectionBounds,
    Selection,
    SelectionState,
    convert_global_to_local_selection,
)

# --- Tree-sitter-styled-text, tree-sitter (tree_sitter uses data_paths, singleton) ---
from pytui.lib.tree_sitter_styled_text import (
    ConcealOptions,
    SyntaxStyleProtocol,
    TreeSitterToStyledTextOptions,
    tree_sitter_to_styled_text,
    tree_sitter_to_text_chunks,
)
from pytui.lib.tree_sitter import (
    COMMON_LANGUAGE_NAMES,
    BufferState,
    Edit,
    FiletypeParserOptions,
    HighlightMeta,
    HighlightRange,
    HighlightResponse,
    InjectionMapping,
    ParsedBuffer,
    PerformanceStats,
    SimpleHighlight,
    TreeSitterClient,
    TreeSitterClientOptions,
    add_default_parsers,
    ext_to_filetype,
    get_default_parsers,
    get_language,
    get_parser,
    get_parsers,
    get_tree_sitter_client,
    highlight,
    list_available_languages,
    path_to_filetype,
)

# --- Data-paths, extmarks, terminal-palette (OpenTUI order) ---
from pytui.lib.extmarks import Extmark, ExtmarksStore
from pytui.lib.terminal_palette import (
    TerminalPalette,
    create_terminal_palette,
    detect_capability,
    get_palette_color,
)

# --- Optional / extra (clipboard, kitty, yoga.options, hast-styled-text) ---
from pytui.lib.clipboard import Clipboard, ClipboardTarget
from pytui.lib.parse_keypress_kitty import (
    KITTY_KEY_MAP,
    parse_kitty_keyboard,
)
from pytui.lib.yoga_options import (
    parse_align,
    parse_align_items,
    parse_display,
    parse_flex_direction,
    parse_justify,
    parse_overflow,
    parse_position_type,
    parse_wrap,
)
from pytui.lib.hast_styled_text import (
    HASTElement,
    HASTNode,
    HASTText,
    hast_to_styled_text,
)

# --- Remaining lib modules ---
from pytui.lib.bunfs import get_bunfs_root_path, is_bunfs_path, normalize_bunfs_path
from pytui.lib.debounce import (
    DebounceController,
    clear_all_debounces,
    clear_debounce_scope,
    create_debounce,
)
from pytui.lib.extmarks_history import ExtmarksHistory, ExtmarksSnapshot
from pytui.lib.key_handler import InternalKeyHandler, KeyEvent, KeyHandler, PasteEvent
from pytui.lib.keymapping import (
    KeyBinding,
    build_key_bindings_map,
    get_key_binding_key,
    merge_key_aliases,
    merge_key_bindings,
    key_binding_to_string,
)
from pytui.lib.objects_in_viewport import get_objects_in_viewport
from pytui.lib.output_capture import Capture, CapturedOutput, CapturedWritableStream
from pytui.lib.queue import ProcessQueue
from pytui.lib.renderable_validations import (
    is_dimension_type,
    is_flex_basis_type,
    is_margin_type,
    is_overflow_type,
    is_padding_type,
    is_position_type,
    is_position_type_type,
    is_size_type,
    is_valid_percentage,
    validate_hex_color,
    validate_non_negative_int,
    validate_options,
    validate_positive_int,
)
from pytui.lib.terminal_capability_detection import (
    is_capability_response,
    is_pixel_resolution_response,
    parse_pixel_resolution,
)

# __all__ order matches OpenTUI lib/index.ts: border, KeyHandler, ascii.font, RGBA, parse.keypress,
# scroll-acceleration, stdin-buffer, styled-text, parse.mouse, selection, env, tree-sitter-styled-text,
# tree-sitter, data-paths, extmarks, terminal-palette; then PyTUI-only/extra modules.
__all__ = [
    # 1. border
    "VALID_BORDER_STYLES",
    "BorderCharArrays",
    "BorderCharacters",
    "BorderChars",
    "BorderSides",
    "BorderSidesConfig",
    "BorderStyle",
    "border_chars_to_array",
    "get_border_from_sides",
    "get_border_sides",
    "is_valid_border_style",
    "parse_border_style",
    # 2. KeyHandler
    "InternalKeyHandler",
    "KeyEvent",
    "KeyHandler",
    "PasteEvent",
    # 3. ascii.font
    "FONT_NAMES",
    "coordinate_to_character_index",
    "fonts",
    "get_character_positions",
    "measure_text",
    # 5. RGBA (4 = hast-styled-text, skipped)
    "RGBA",
    "hex_to_rgb",
    "hsv_to_rgb",
    "parse_color",
    "parse_color_to_tuple",
    "rgb_to_hex",
    # 6. parse.keypress
    "KeyEventType",
    "ParsedKey",
    "non_alphanumeric_keys",
    "parse_keypress",
    # 7. scroll-acceleration
    "LinearScrollAccel",
    "MacOSScrollAccel",
    "ScrollAcceleration",
    # 8. stdin-buffer
    "StdinBuffer",
    # 9. styled-text
    "StyledText",
    "TextAttributes",
    "create_text_attributes",
    "is_styled_text",
    "string_to_styled_text",
    # 11. parse.mouse (10 = yoga.options, skipped)
    "MouseParser",
    "RawMouseEvent",
    "ScrollInfo",
    # 12. selection
    "ASCIIFontSelectionHelper",
    "LocalSelectionBounds",
    "Selection",
    "SelectionState",
    "convert_global_to_local_selection",
    # 13. env
    "clear_env_cache",
    "env",
    "generate_env_colored",
    "generate_env_markdown",
    "register_env_var",
    # 14. tree-sitter-styled-text
    "ConcealOptions",
    "SyntaxStyleProtocol",
    "TreeSitterToStyledTextOptions",
    "tree_sitter_to_styled_text",
    "tree_sitter_to_text_chunks",
    # 15. tree-sitter
    "COMMON_LANGUAGE_NAMES",
    "BufferState",
    "Edit",
    "FiletypeParserOptions",
    "HighlightMeta",
    "HighlightRange",
    "HighlightResponse",
    "InjectionMapping",
    "ParsedBuffer",
    "PerformanceStats",
    "SimpleHighlight",
    "TreeSitterClient",
    "TreeSitterClientOptions",
    "add_default_parsers",
    "ext_to_filetype",
    "get_default_parsers",
    "get_parsers",
    "get_language",
    "get_parser",
    "get_tree_sitter_client",
    "highlight",
    "list_available_languages",
    "path_to_filetype",
    # 16. data-paths
    "DataPathsManager",
    "ensure_cache_dir",
    "ensure_data_dir",
    "get_cache_dir",
    "get_data_dir",
    "get_data_paths",
    # 17. extmarks
    "Extmark",
    "ExtmarksStore",
    # 18. terminal-palette
    "TerminalPalette",
    "create_terminal_palette",
    "detect_capability",
    "get_palette_color",
    # Optional: clipboard, parse_keypress_kitty, yoga_options, hast_styled_text
    "Clipboard",
    "ClipboardTarget",
    "KITTY_KEY_MAP",
    "parse_kitty_keyboard",
    "parse_align",
    "parse_align_items",
    "parse_display",
    "parse_flex_direction",
    "parse_justify",
    "parse_overflow",
    "parse_position_type",
    "parse_wrap",
    "HASTElement",
    "HASTNode",
    "HASTText",
    "hast_to_styled_text",
    # PyTUI-only / extra (singleton, validate_dir_name, bunfs, debounce, ...)
    "destroy_singleton",
    "has_singleton",
    "singleton",
    "is_valid_directory_name",
    "get_bunfs_root_path",
    "is_bunfs_path",
    "normalize_bunfs_path",
    "DebounceController",
    "clear_all_debounces",
    "clear_debounce_scope",
    "create_debounce",
    "ExtmarksHistory",
    "ExtmarksSnapshot",
    "KeyBinding",
    "build_key_bindings_map",
    "get_key_binding_key",
    "merge_key_aliases",
    "merge_key_bindings",
    "key_binding_to_string",
    "get_objects_in_viewport",
    "Capture",
    "CapturedOutput",
    "CapturedWritableStream",
    "ProcessQueue",
    "is_dimension_type",
    "is_flex_basis_type",
    "is_margin_type",
    "is_overflow_type",
    "is_padding_type",
    "is_position_type",
    "is_position_type_type",
    "is_size_type",
    "is_valid_percentage",
    "validate_hex_color",
    "validate_non_negative_int",
    "validate_options",
    "validate_positive_int",
    "is_capability_response",
    "is_pixel_resolution_response",
    "parse_pixel_resolution",
]
