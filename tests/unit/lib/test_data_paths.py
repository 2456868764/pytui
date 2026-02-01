# Phase 2: lib/data_paths (get_data_dir, get_cache_dir, DataPathsManager, get_data_paths)

import pytest

from pytui.lib.data_paths import (
    DataPathsManager,
    ensure_cache_dir,
    ensure_data_dir,
    get_cache_dir,
    get_data_paths,
    get_data_dir,
)


def test_get_data_dir():
    p = get_data_dir("pytui")
    assert "pytui" in str(p)


def test_get_cache_dir():
    p = get_cache_dir("pytui")
    assert "pytui" in str(p)


def test_ensure_dirs(tmp_path):
    import os
    os.environ["XDG_DATA_HOME"] = str(tmp_path / "data")
    os.environ["XDG_CACHE_HOME"] = str(tmp_path / "cache")
    try:
        d = ensure_data_dir("pytui_test")
        assert d.is_dir()
        c = ensure_cache_dir("pytui_test")
        assert c.is_dir()
    finally:
        os.environ.pop("XDG_DATA_HOME", None)
        os.environ.pop("XDG_CACHE_HOME", None)


def test_data_paths_manager_singleton():
    m1 = get_data_paths()
    m2 = get_data_paths()
    assert m1 is m2


def test_data_paths_manager_app_name():
    m = DataPathsManager()
    m.app_name = "test_app"
    assert m.app_name == "test_app"
    assert "test_app" in m.global_config_path
    assert "test_app" in m.global_data_path


def test_data_paths_manager_invalid_app_name():
    m = DataPathsManager()
    with pytest.raises(ValueError, match="Invalid app name"):
        m.app_name = "CON"


def test_data_paths_manager_to_object():
    m = DataPathsManager()
    m.app_name = "pytui"
    o = m.to_object()
    assert "globalConfigPath" in o
    assert "globalConfigFile" in o
    assert "localConfigFile" in o
    assert "globalDataPath" in o
