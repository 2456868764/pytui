# pytui.utils.data_paths - 数据目录/缓存路径（tree-sitter 资源、字体等）


from __future__ import annotations

import os
from pathlib import Path


def get_data_dir(app_name: str = "pytui") -> Path:
    """返回应用数据目录（tree-sitter、字体等）。平台相关。"""
    if os.name == "nt":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(base) / app_name
    if os.environ.get("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"]) / app_name
    return Path.home() / ".local" / "share" / app_name


def get_cache_dir(app_name: str = "pytui") -> Path:
    """返回缓存目录。平台相关。"""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", os.path.expanduser("~")))
        return Path(base) / app_name / "cache"
    if os.environ.get("XDG_CACHE_HOME"):
        return Path(os.environ["XDG_CACHE_HOME"]) / app_name
    return Path.home() / ".cache" / app_name


def ensure_data_dir(app_name: str = "pytui") -> Path:
    """确保数据目录存在并返回路径。"""
    p = get_data_dir(app_name)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_cache_dir(app_name: str = "pytui") -> Path:
    """确保缓存目录存在并返回路径。"""
    p = get_cache_dir(app_name)
    p.mkdir(parents=True, exist_ok=True)
    return p
