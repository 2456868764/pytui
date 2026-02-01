# Unit tests for tree-sitter caching - aligned with OpenTUI tree-sitter/cache.test.ts
# Stub-friendly: PyTUI client has no WASM/download; tests clear_cache and set_data_path semantics.

from __future__ import annotations

import pytest

from pytui.lib.tree_sitter import TreeSitterClient
from pytui.lib.tree_sitter.parsers_config import add_default_parsers


@pytest.mark.asyncio
class TestTreeSitterClientCaching:
    """Align OpenTUI cache.test.ts; stub does not create dirs or download WASM."""

    async def test_clear_cache_requires_initialized(self) -> None:
        """Align: clearCache when not initialized raises."""
        client = TreeSitterClient({"dataPath": "/tmp/cache-test"})
        with pytest.raises(RuntimeError, match="not initialized"):
            await client.clear_cache()
        await client.destroy()

    async def test_clear_cache_when_initialized_succeeds(self) -> None:
        """Align: clearCache when initialized is no-op (stub)."""
        client = TreeSitterClient({"dataPath": "/tmp/cache-test"})
        await client.initialize()
        await client.clear_cache()
        await client.destroy()

    async def test_set_data_path_updates_internal_path(self) -> None:
        """Align: setDataPath changes where client would resolve paths (stub: no fs)."""
        client = TreeSitterClient({"dataPath": "/tmp/initial"})
        await client.initialize()
        client.set_data_path("/tmp/new_path")
        # Stub does not create dirs; we only assert no exception and create_buffer still works
        add_default_parsers([{"filetype": "javascript", "wasm": "", "queries": {}}])
        has_parser = await client.create_buffer(1, "const x = 1;", "javascript")
        assert has_parser is True
        await client.remove_buffer(1)
        await client.destroy()
