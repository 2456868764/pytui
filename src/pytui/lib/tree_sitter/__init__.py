# pytui.lib.tree_sitter - Aligns with OpenTUI lib/tree-sitter

from __future__ import annotations

from pytui.lib.data_paths import get_data_paths
from pytui.lib.singleton import singleton

from pytui.lib.tree_sitter.client import TreeSitterClient
from pytui.lib.tree_sitter.languages import (
    COMMON_LANGUAGE_NAMES,
    get_language,
    get_parser,
    list_available_languages,
)
from pytui.lib.tree_sitter.download_utils import (
    DownloadResult,
    download_or_load,
    download_to_path,
    fetch_highlight_queries,
)
from pytui.lib.tree_sitter.parsers_config import add_default_parsers, get_default_parsers

# Align OpenTUI getParsers(): same as get_default_parsers
get_parsers = get_default_parsers
from pytui.lib.tree_sitter.resolve_ft import ext_to_filetype, path_to_filetype
from pytui.lib.tree_sitter.sync_highlight import highlight
from pytui.lib.tree_sitter.types import (
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
    TreeSitterClientOptions,
)

__all__ = [
    "TreeSitterClient",
    "get_tree_sitter_client",
    "add_default_parsers",
    "get_default_parsers",
    "get_parsers",
    "DownloadResult",
    "download_or_load",
    "download_to_path",
    "fetch_highlight_queries",
    "ext_to_filetype",
    "path_to_filetype",
    "COMMON_LANGUAGE_NAMES",
    "get_language",
    "get_parser",
    "list_available_languages",
    "highlight",
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
    "TreeSitterClientOptions",
]


def get_tree_sitter_client() -> TreeSitterClient:
    """Align with OpenTUI getTreeSitterClient(). Singleton client; subscribes to paths:changed -> set_data_path."""
    def factory() -> TreeSitterClient:
        data_paths_manager = get_data_paths()
        data_path = getattr(data_paths_manager, "global_data_path", None) or (
            data_paths_manager.to_object().get("globalDataPath") if hasattr(data_paths_manager, "to_object") else ""
        )
        opts: TreeSitterClientOptions = {"dataPath": data_path or ""}
        client = TreeSitterClient(opts)
        data_paths_manager.on("paths:changed", lambda paths: client.set_data_path(paths.get("globalDataPath", "")))
        return client
    return singleton("tree-sitter-client", factory)
