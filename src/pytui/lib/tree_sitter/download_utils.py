# pytui.lib.tree_sitter.download_utils - Aligns with OpenTUI lib/tree-sitter/download-utils.ts
# WASM/query download and cache: download_or_load, download_to_path, fetch_highlight_queries.

from __future__ import annotations

import asyncio
import logging
import os
from typing import TypedDict
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

_LOG = logging.getLogger(__name__)


class DownloadResult(TypedDict, total=False):
    """Align with OpenTUI DownloadResult."""

    content: bytes
    file_path: str
    error: str


def _hash_url(url: str) -> str:
    """Align with OpenTUI DownloadUtils.hashUrl (djb2-style)."""
    h = 0
    for c in url:
        h = ((h << 5) - h + ord(c)) & 0xFFFFFFFF
    return hex(abs(h))[2:]


def _download_or_load_sync(
    source: str,
    cache_dir: str,
    cache_subdir: str,
    file_extension: str,
    use_hash_for_cache: bool = True,
    filetype: str | None = None,
) -> DownloadResult:
    """Blocking implementation; use download_or_load for async."""
    is_url = source.startswith("http://") or source.startswith("https://")
    if is_url:
        if use_hash_for_cache:
            h = _hash_url(source)
            cache_file_name = f"{filetype}-{h}{file_extension}" if filetype else f"{h}{file_extension}"
        else:
            cache_file_name = os.path.basename(source)
        cache_file = os.path.join(cache_dir, cache_subdir, cache_file_name)
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        if os.path.isfile(cache_file) and os.path.getsize(cache_file) > 0:
            try:
                with open(cache_file, "rb") as f:
                    content = f.read()
                _LOG.info("Loaded from cache: %s (%s)", cache_file, source)
                return {"content": content, "file_path": cache_file}
            except OSError:
                pass
        try:
            _LOG.info("Downloading from URL: %s", source)
            req = Request(source, headers={"User-Agent": "PyTUI-tree-sitter/1.0"})
            with urlopen(req, timeout=30) as resp:
                content = resp.read()
            try:
                with open(cache_file, "wb") as f:
                    f.write(content)
                _LOG.info("Cached: %s", source)
            except OSError as e:
                _LOG.warning("Failed to cache: %s", e)
            return {"content": content, "file_path": cache_file}
        except (HTTPError, URLError, OSError) as e:
            return {"error": f"Error downloading from {source}: {e}"}
    else:
        try:
            _LOG.info("Loading from local path: %s", source)
            with open(source, "rb") as f:
                content = f.read()
            return {"content": content, "file_path": source}
        except OSError as e:
            return {"error": f"Error loading from local path {source}: {e}"}


async def download_or_load(
    source: str,
    cache_dir: str,
    cache_subdir: str,
    file_extension: str,
    use_hash_for_cache: bool = True,
    filetype: str | None = None,
) -> DownloadResult:
    """Download from URL or load from local path, with caching. Aligns with OpenTUI DownloadUtils.downloadOrLoad."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: _download_or_load_sync(
            source, cache_dir, cache_subdir, file_extension, use_hash_for_cache, filetype
        ),
    )


def _download_to_path_sync(source: str, target_path: str) -> DownloadResult:
    """Blocking implementation."""
    is_url = source.startswith("http://") or source.startswith("https://")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if is_url:
        try:
            _LOG.info("Downloading from URL: %s", source)
            req = Request(source, headers={"User-Agent": "PyTUI-tree-sitter/1.0"})
            with urlopen(req, timeout=30) as resp:
                content = resp.read()
            with open(target_path, "wb") as f:
                f.write(content)
            _LOG.info("Downloaded: %s -> %s", source, target_path)
            return {"content": content, "file_path": target_path}
        except (HTTPError, URLError, OSError) as e:
            return {"error": f"Error downloading from {source}: {e}"}
    else:
        try:
            _LOG.info("Copying from local path: %s", source)
            with open(source, "rb") as f:
                content = f.read()
            with open(target_path, "wb") as f:
                f.write(content)
            return {"content": content, "file_path": target_path}
        except OSError as e:
            return {"error": f"Error copying from local path {source}: {e}"}


async def download_to_path(source: str, target_path: str) -> DownloadResult:
    """Download/save file to target path. Aligns with OpenTUI DownloadUtils.downloadToPath."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _download_to_path_sync(source, target_path))


def _fetch_highlight_query_sync(source: str, cache_dir: str, filetype: str) -> str:
    """Fetch one highlight query (blocking)."""
    result = _download_or_load_sync(source, cache_dir, "queries", ".scm", True, filetype)
    if result.get("error"):
        _LOG.error("Error fetching highlight query from %s: %s", source, result["error"])
        return ""
    content = result.get("content")
    if content:
        return content.decode("utf-8", errors="replace")
    return ""


async def fetch_highlight_queries(
    sources: list[str],
    cache_dir: str,
    filetype: str,
) -> str:
    """Fetch multiple highlight queries and concatenate. Aligns with OpenTUI DownloadUtils.fetchHighlightQueries."""
    loop = asyncio.get_event_loop()

    def _one(src: str) -> str:
        return _fetch_highlight_query_sync(src, cache_dir, filetype)

    results = await asyncio.gather(
        *[loop.run_in_executor(None, lambda s=src: _one(s)) for src in sources]
    )
    valid = [q.strip() for q in results if q and q.strip()]
    return "\n".join(valid)
