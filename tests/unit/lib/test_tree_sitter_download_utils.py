# Unit tests for tree_sitter.download_utils - aligned with OpenTUI download-utils

from __future__ import annotations

import asyncio
import os
import tempfile

import pytest

from pytui.lib.tree_sitter.download_utils import (
    DownloadResult,
    download_or_load,
    download_to_path,
    fetch_highlight_queries,
)


@pytest.mark.asyncio
class TestDownloadUtils:
    async def test_download_or_load_local_path(self) -> None:
        """Load from local path returns content and file_path."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".scm") as f:
            f.write(b"; comment\n(identifier)")
            path = f.name
        try:
            result = await download_or_load(
                path,
                cache_dir=tempfile.gettempdir(),
                cache_subdir="queries",
                file_extension=".scm",
                use_hash_for_cache=False,
            )
            assert "error" not in result or result.get("error") is None
            assert result.get("content") == b"; comment\n(identifier)"
            assert result.get("file_path") == path
        finally:
            os.unlink(path)

    async def test_download_or_load_missing_local_returns_error(self) -> None:
        """Missing local path returns error."""
        result = await download_or_load(
            "/nonexistent/path/file.scm",
            cache_dir=tempfile.gettempdir(),
            cache_subdir="queries",
            file_extension=".scm",
        )
        assert "error" in result
        assert result["error"]

    async def test_download_to_path_local(self) -> None:
        """download_to_path copies local file to target."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".wasm") as f:
            f.write(b"\x00asm")
            src = f.name
        target = os.path.join(tempfile.gettempdir(), "tree-sitter-download-test-target.wasm")
        try:
            result = await download_to_path(src, target)
            assert "error" not in result or result.get("error") is None
            assert result.get("file_path") == target
            assert os.path.isfile(target)
            with open(target, "rb") as f:
                assert f.read() == b"\x00asm"
        finally:
            if os.path.exists(src):
                os.unlink(src)
            if os.path.exists(target):
                os.unlink(target)

    async def test_fetch_highlight_queries_local(self) -> None:
        """fetch_highlight_queries loads and concatenates local query files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".scm") as f:
            f.write("(keyword) @keyword")
            path1 = f.name
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".scm") as f:
            f.write("(string) @string")
            path2 = f.name
        try:
            out = await fetch_highlight_queries([path1, path2], tempfile.gettempdir(), "test")
            assert "keyword" in out
            assert "string" in out
        finally:
            os.unlink(path1)
            os.unlink(path2)
