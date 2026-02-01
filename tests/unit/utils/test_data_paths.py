# tests/unit/utils/test_data_paths.py

import pytest

pytest.importorskip("pytui.lib.data_paths")


class TestDataPaths:
    def test_get_data_dir(self):
        from pytui.lib.data_paths import get_data_dir

        p = get_data_dir("pytui")
        assert "pytui" in str(p)

    def test_get_cache_dir(self):
        from pytui.lib.data_paths import get_cache_dir

        p = get_cache_dir("pytui")
        assert "pytui" in str(p)

    def test_ensure_dirs(self, tmp_path):
        import os
        from pytui.lib.data_paths import ensure_cache_dir, ensure_data_dir, get_cache_dir, get_data_dir

        # 使用 tmp_path 避免写入 ~/.local（沙箱可能无权限）
        data_root = tmp_path / "data"
        cache_root = tmp_path / "cache"
        data_root.mkdir()
        cache_root.mkdir()
        os.environ["XDG_DATA_HOME"] = str(data_root)
        os.environ["XDG_CACHE_HOME"] = str(cache_root)
        try:
            d = ensure_data_dir("pytui_test")
            assert d.is_dir()
            c = ensure_cache_dir("pytui_test")
            assert c.is_dir()
        finally:
            os.environ.pop("XDG_DATA_HOME", None)
            os.environ.pop("XDG_CACHE_HOME", None)
