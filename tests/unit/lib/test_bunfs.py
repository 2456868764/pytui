# Unit tests for pytui.lib.bunfs - aligned with OpenTUI lib/bunfs.test.ts

import sys

import pytest

from pytui.lib.bunfs import get_bunfs_root_path, is_bunfs_path


class TestBunfs:
    """Tests for bunfs module."""

    def test_is_bunfs_path_detects_dollar_bunfs_paths(self) -> None:
        assert is_bunfs_path("/$bunfs/root/file.wasm") is True

    def test_is_bunfs_path_detects_windows_b_paths(self) -> None:
        assert is_bunfs_path("B:\\~BUN\\root\\file.wasm") is True
        assert is_bunfs_path("B:/~BUN/root/file.wasm") is True

    def test_is_bunfs_path_ignores_regular_paths(self) -> None:
        assert is_bunfs_path("/usr/local/bin/file") is False
        assert is_bunfs_path("C:/Users/file.wasm") is False

    def test_get_bunfs_root_path(self) -> None:
        root = get_bunfs_root_path()
        if sys.platform == "win32":
            assert root == "B:\\~BUN\\root"
        else:
            assert root == "/$bunfs/root"

    def test_normalize_bunfs_path(self) -> None:
        from pytui.lib.bunfs import normalize_bunfs_path

        out = normalize_bunfs_path("/some/dir/file.wasm")
        if sys.platform == "win32":
            assert out == "B:\\~BUN\\root\\file.wasm"
        else:
            assert out == "/$bunfs/root/file.wasm"
