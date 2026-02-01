# pytui.lib.tree_sitter.languages - get_language, get_parser, list_available_languages (from syntax/languages)

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Common language names (tree-sitter-languages or data_paths .so names)
COMMON_LANGUAGE_NAMES = (
    "python",
    "javascript",
    "typescript",
    "go",
    "rust",
    "json",
    "html",
    "css",
    "bash",
    "c",
    "cpp",
)


def _language_from_data_path(name: str) -> Any | None:
    """Load tree-sitter language from data_paths tree-sitter/languages .so/.dll."""
    try:
        from tree_sitter import Language as TSLanguage
    except ImportError:
        return None
    try:
        from pytui.lib.data_paths import get_data_dir
    except ImportError:
        return None
    ext = ".dll" if sys.platform == "win32" else ".so"
    lib_dir = get_data_dir() / "tree-sitter" / "languages"
    path = lib_dir / f"{name}{ext}"
    if not path.is_file():
        return None
    try:
        return TSLanguage(str(path), name)
    except (TypeError, OSError, Exception):
        return None


def get_language(name: str) -> Any | None:
    """Load tree-sitter language (e.g. python, javascript). Returns None if unavailable."""
    try:
        import tree_sitter  # noqa: F401
    except ImportError:
        return None
    try:
        import tree_sitter_languages as tsl

        if hasattr(tsl, "get_language"):
            try:
                lang = tsl.get_language(name)
                if lang is not None:
                    return lang
            except (TypeError, AttributeError):
                pass
    except ImportError:
        pass
    return _language_from_data_path(name)


def get_parser(language: str | None = None) -> Any | None:
    """Return configured Parser for language; None if unavailable."""
    lang_name = language or "python"
    try:
        import tree_sitter_languages as tsl

        if hasattr(tsl, "get_parser"):
            try:
                p = tsl.get_parser(lang_name)
                if p is not None:
                    return p
            except (TypeError, AttributeError):
                pass
    except ImportError:
        pass
    try:
        import tree_sitter
    except ImportError:
        return None
    lang = get_language(lang_name)
    if lang is None:
        return None
    parser = tree_sitter.Parser()
    if hasattr(parser, "set_language"):
        parser.set_language(lang)
    else:
        parser.language = lang  # type: ignore[attr-defined]
    return parser


def list_available_languages() -> list[str]:
    """Return list of available language names. Empty if tree-sitter not installed."""
    result: list[str] = []
    try:
        import tree_sitter  # noqa: F401
    except ImportError:
        return result
    for name in COMMON_LANGUAGE_NAMES:
        if get_language(name) is not None:
            result.append(name)
    return sorted(result)
