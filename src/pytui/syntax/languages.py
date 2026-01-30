# pytui.syntax.languages - 预编译 tree-sitter 语言包集成（可选）


from __future__ import annotations

from typing import Any


def get_language(name: str) -> Any | None:
    """加载 tree-sitter 语言（如 python、javascript）。未安装或未构建时返回 None。"""
    try:
        import tree_sitter  # noqa: F401
    except ImportError:
        return None
    try:
        import tree_sitter_languages as tsl

        if hasattr(tsl, "get_language"):
            try:
                return tsl.get_language(name)
            except (TypeError, AttributeError):
                pass
        return getattr(tsl, name, None)
    except ImportError:
        pass
    return None


def get_parser(language: str | None = None) -> Any | None:
    """返回配置好的 Parser；language 为 None 或不可用时返回 None。"""
    lang_name = language or "python"
    try:
        import tree_sitter_languages as tsl

        if hasattr(tsl, "get_parser"):
            try:
                return tsl.get_parser(lang_name)
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
