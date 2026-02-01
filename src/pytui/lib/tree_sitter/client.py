# pytui.lib.tree_sitter.client - Aligns with OpenTUI lib/tree-sitter/client.ts
# TreeSitterClient stub (no WASM worker): API aligned with OpenTUI

from __future__ import annotations

import os
from typing import Any

from pytui.lib.bunfs import is_bunfs_path, normalize_bunfs_path
from pytui.lib.tree_sitter.parsers_config import get_default_parsers
from pytui.lib.tree_sitter.types import (
    BufferState,
    Edit,
    FiletypeParserOptions,
    PerformanceStats,
)


def _resolve_path(path: str, base_path: str = "") -> str:
    """Resolve URL, bunfs, or relative path. Aligns OpenTUI resolvePath."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if is_bunfs_path(path):
        return normalize_bunfs_path(os.path.basename(path))
    if base_path and not path.startswith("/") and ":" not in (path[:2] if len(path) >= 2 else path):
        return os.path.normpath(os.path.join(base_path, path))
    return path


class TreeSitterClient:
    """Stub TreeSitter client (no WASM worker). API aligned with OpenTUI TreeSitterClient."""

    def __init__(self, options: dict[str, Any]) -> None:
        self._initialized = False
        self._options = dict(options)
        self._data_path: str = options.get("dataPath", "")
        self._buffers: dict[int, dict[str, Any]] = {}

    def is_initialized(self) -> bool:
        """Align with OpenTUI isInitialized()."""
        return self._initialized

    async def initialize(self) -> None:
        """Align with OpenTUI initialize(). Registers default parsers."""
        if self._initialized:
            return
        self._initialized = True
        for parser in get_default_parsers():
            self.add_filetype_parser(parser)

    def set_data_path(self, data_path: str) -> None:
        """Align with OpenTUI setDataPath()."""
        if self._options.get("dataPath") == data_path:
            return
        self._options["dataPath"] = data_path
        self._data_path = data_path

    def add_filetype_parser(self, filetype_parser: FiletypeParserOptions | dict[str, Any]) -> None:
        """Align with OpenTUI addFiletypeParser(). Stub: no worker; resolves paths."""
        opts = dict(filetype_parser)
        opts["wasm"] = _resolve_path(opts.get("wasm", ""), self._data_path)
        q = opts.get("queries") or {}
        if isinstance(q, dict):
            highlights = [_resolve_path(p, self._data_path) for p in q.get("highlights", [])]
            injections = q.get("injections")
            resolved_queries: dict[str, Any] = {"highlights": highlights}
            if injections is not None:
                resolved_queries["injections"] = [_resolve_path(p, self._data_path) for p in injections]
            opts["queries"] = resolved_queries

    async def preload_parser(self, filetype: str) -> bool:
        """Align with OpenTUI preloadParser(). Stub: returns False (no parsers)."""
        await self.initialize()
        return False

    async def get_performance(self) -> PerformanceStats:
        """Align with OpenTUI getPerformance(). Stub: zero stats."""
        return {
            "averageParseTime": 0.0,
            "parseTimes": [],
            "averageQueryTime": 0.0,
            "queryTimes": [],
        }

    async def highlight_once(
        self,
        content: str,
        filetype: str,
    ) -> dict[str, Any]:
        """Align with OpenTUI highlightOnce(). Returns { highlights?, warning?, error? }. Stub: empty highlights."""
        await self.initialize()
        return {"highlights": []}

    async def create_buffer(
        self,
        id_: int,
        content: str,
        filetype: str,
        version: int = 1,
        auto_initialize: bool = True,
    ) -> bool:
        """Align with OpenTUI createBuffer(). Returns hasParser (true if filetype in default parsers)."""
        if not self._initialized:
            if not auto_initialize:
                return False
            await self.initialize()
        if id_ in self._buffers:
            raise ValueError(f"Buffer with id {id_} already exists")
        supported = [p.get("filetype") for p in get_default_parsers() if p.get("filetype")]
        has_parser = filetype in supported
        self._buffers[id_] = {
            "id": id_,
            "version": version,
            "content": content,
            "filetype": filetype,
            "hasParser": has_parser,
        }
        return has_parser

    async def update_buffer(
        self,
        id_: int,
        edits: list[Edit],
        new_content: str,
        version: int,
    ) -> None:
        """Align with OpenTUI updateBuffer(). Stub: updates stored content/version."""
        if not self._initialized:
            return
        buf = self._buffers.get(id_)
        if not buf or not buf.get("hasParser"):
            return
        self._buffers[id_] = {**buf, "content": new_content, "version": version}

    async def reset_buffer(self, buffer_id: int, version: int, content: str) -> None:
        """Align with OpenTUI resetBuffer(). Stub: updates stored content/version."""
        if not self._initialized:
            return
        buf = self._buffers.get(buffer_id)
        if not buf or not buf.get("hasParser"):
            return
        self._buffers[buffer_id] = {**buf, "content": content, "version": version}

    async def remove_buffer(self, buffer_id: int) -> None:
        """Align with OpenTUI removeBuffer()."""
        if not self._initialized:
            return
        self._buffers.pop(buffer_id, None)

    def dispose_buffer(self, id_: int) -> None:
        """Alias for remove_buffer (sync). OpenTUI uses removeBuffer; kept for backward compat."""
        self._buffers.pop(id_, None)

    def get_buffer(self, id_: int) -> BufferState | None:
        """Align with OpenTUI getBuffer()."""
        return self._buffers.get(id_)

    def get_buffer_state(self, id_: int) -> BufferState | None:
        """Get buffer state by id. Same as get_buffer."""
        return self.get_buffer(id_)

    def get_all_buffers(self) -> list[BufferState]:
        """Align with OpenTUI getAllBuffers()."""
        return list(self._buffers.values())

    async def clear_cache(self) -> None:
        """Align with OpenTUI clearCache(). Stub: no-op unless initialized."""
        if not self._initialized:
            raise RuntimeError("Cannot clear cache: client is not initialized")

    async def destroy(self) -> None:
        """Align with OpenTUI destroy()."""
        self._buffers.clear()
        self._initialized = False
