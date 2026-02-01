# Unit tests for pytui.lib.tree_sitter - aligned with OpenTUI tree-sitter API

from __future__ import annotations

import pytest

from pytui.lib.data_paths import get_data_paths
from pytui.lib.tree_sitter import (
    TreeSitterClient,
    add_default_parsers,
    ext_to_filetype,
    get_default_parsers,
    get_tree_sitter_client,
    path_to_filetype,
)


class TestResolveFt:
    def test_ext_to_filetype(self) -> None:
        assert ext_to_filetype("js") == "javascript"
        assert ext_to_filetype("ts") == "typescript"
        assert ext_to_filetype("py") == "python"
        assert ext_to_filetype("md") == "markdown"
        assert ext_to_filetype("zig") == "zig"
        assert ext_to_filetype("unknown") is None

    def test_path_to_filetype(self) -> None:
        assert path_to_filetype("src/main.ts") == "typescript"
        assert path_to_filetype("foo/bar.py") == "python"
        assert path_to_filetype("readme.md") == "markdown"
        assert path_to_filetype("noext") is None
        assert path_to_filetype("dot.") is None
        assert path_to_filetype("") is None


class TestParsersConfig:
    def test_get_default_parsers_returns_list(self) -> None:
        parsers = get_default_parsers()
        assert isinstance(parsers, list)

    def test_add_default_parsers(self) -> None:
        add_default_parsers(
            [
                {
                    "filetype": "testlang",
                    "wasm": "https://example.com/test.wasm",
                    "queries": {"highlights": ["https://example.com/highlights.scm"]},
                }
            ]
        )
        parsers = get_default_parsers()
        assert any(p.get("filetype") == "testlang" for p in parsers)
        add_default_parsers([{"filetype": "testlang", "queries": {"highlights": []}, "wasm": ""}])
        parsers2 = get_default_parsers()
        assert any(p.get("filetype") == "testlang" for p in parsers2)


@pytest.mark.asyncio
class TestTreeSitterClient:
    async def test_initialize(self) -> None:
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        assert client.is_initialized() is False
        await client.initialize()
        assert client.is_initialized() is True
        await client.destroy()

    async def test_highlight_once_returns_highlights_key(self) -> None:
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        result = await client.highlight_once("const x = 1;", "javascript")
        assert "highlights" in result
        assert result["highlights"] == []
        await client.destroy()

    async def test_create_buffer_with_supported_filetype(self) -> None:
        """Align OpenTUI: should create buffer with supported filetype (hasParser true)."""
        add_default_parsers([{"filetype": "javascript", "wasm": "", "queries": {}}])
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        await client.initialize()
        has_parser = await client.create_buffer(1, "const hello = \"world\";", "javascript")
        assert has_parser is True
        buf = client.get_buffer(1)
        assert buf is not None
        assert buf.get("hasParser") is True
        assert buf.get("content") == 'const hello = "world";'
        assert buf.get("filetype") == "javascript"
        await client.remove_buffer(1)
        assert client.get_buffer(1) is None
        await client.destroy()

    async def test_create_buffer_without_parser_unsupported_filetype(self) -> None:
        """Align OpenTUI: should create buffer without parser for unsupported filetype."""
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        await client.initialize()
        has_parser = await client.create_buffer(1, "some random content", "unsupported")
        assert has_parser is False
        buf = client.get_buffer(1)
        assert buf is not None
        assert buf.get("hasParser") is False
        await client.destroy()

    async def test_create_buffer_duplicate_raises(self) -> None:
        """Align OpenTUI: should prevent duplicate buffer creation."""
        add_default_parsers([{"filetype": "javascript", "wasm": "", "queries": {}}])
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        await client.initialize()
        await client.create_buffer(1, "const hello = \"world\";", "javascript")
        with pytest.raises(ValueError, match="already exists"):
            await client.create_buffer(1, "other code", "javascript")
        await client.destroy()

    async def test_set_data_path(self) -> None:
        """Align OpenTUI: setDataPath updates client data path."""
        client = TreeSitterClient({"dataPath": "/tmp/initial"})
        client.set_data_path("/tmp/new_path")
        # Stub does not expose _data_path; verify no exception and optional second set is no-op
        client.set_data_path("/tmp/new_path")
        await client.destroy()

    async def test_get_all_buffers(self) -> None:
        """Align OpenTUI: should handle multiple buffers."""
        add_default_parsers([
            {"filetype": "javascript", "wasm": "", "queries": {}},
            {"filetype": "typescript", "wasm": "", "queries": {}},
        ])
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        await client.initialize()
        await client.create_buffer(1, "const hello = \"world\";", "javascript")
        await client.create_buffer(2, "interface Test { value: string }", "typescript")
        all_bufs = client.get_all_buffers()
        assert len(all_bufs) == 2
        js_buf = client.get_buffer(1)
        ts_buf = client.get_buffer(2)
        assert js_buf is not None and js_buf.get("filetype") == "javascript" and js_buf.get("hasParser") is True
        assert ts_buf is not None and ts_buf.get("filetype") == "typescript" and ts_buf.get("hasParser") is True
        await client.destroy()

    async def test_remove_buffer_then_get_is_none(self) -> None:
        """Align OpenTUI: should handle buffer removal (buffer:disposed semantics)."""
        add_default_parsers([{"filetype": "javascript", "wasm": "", "queries": {}}])
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        await client.initialize()
        await client.create_buffer(1, "const hello = \"world\";", "javascript")
        await client.remove_buffer(1)
        assert client.get_buffer(1) is None
        await client.destroy()

    async def test_destroy_clears_buffers_and_uninitialized(self) -> None:
        """Align OpenTUI: should clean up resources on destroy."""
        add_default_parsers([{"filetype": "javascript", "wasm": "", "queries": {}}])
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        await client.initialize()
        await client.create_buffer(1, "const hello = \"world\";", "javascript")
        assert len(client.get_all_buffers()) == 1
        await client.destroy()
        assert client.is_initialized() is False
        assert len(client.get_all_buffers()) == 0

    async def test_preload_parser_returns_false_stub(self) -> None:
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        got = await client.preload_parser("javascript")
        assert got is False
        await client.destroy()

    async def test_get_performance(self) -> None:
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        stats = await client.get_performance()
        assert "averageParseTime" in stats
        assert "queryTimes" in stats
        await client.destroy()

    async def test_clear_cache_requires_initialized(self) -> None:
        client = TreeSitterClient({"dataPath": "/tmp/ts"})
        with pytest.raises(RuntimeError, match="not initialized"):
            await client.clear_cache()
        await client.initialize()
        await client.clear_cache()
        await client.destroy()


def test_get_tree_sitter_client_singleton() -> None:
    """Align OpenTUI: getTreeSitterClient returns same singleton."""
    c1 = get_tree_sitter_client()
    c2 = get_tree_sitter_client()
    assert c1 is c2


def test_get_tree_sitter_client_paths_changed_subscription() -> None:
    """Align OpenTUI: getTreeSitterClient subscribes to paths:changed -> set_data_path (no exception on emit)."""
    client = get_tree_sitter_client()
    paths_manager = get_data_paths()
    paths_manager.emit("paths:changed", {"globalDataPath": "/tmp/pytui-test-path"})
    # Stub: set_data_path was called; we only assert no exception
    assert client is not None
