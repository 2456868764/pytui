# pytui.lib.data_paths - Aligns with OpenTUI lib/data-paths.ts
# get_data_dir, get_cache_dir, ensure_data_dir, ensure_cache_dir;
# DataPathsManager, get_data_paths (singleton).

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pytui.lib.env import env, register_env_var
from pytui.lib.singleton import singleton
from pytui.lib.validate_dir_name import is_valid_directory_name

def _register_xdg_env_vars() -> None:
    """Register XDG env vars (aligns with OpenTUI data-paths.ts); called on first use to avoid import-order issues."""
    try:
        register_env_var({
            "name": "XDG_CONFIG_HOME",
            "description": "Base directory for user-specific configuration files",
            "type": "string",
            "default": "",
        })
    except Exception:
        pass
    try:
        register_env_var({
            "name": "XDG_DATA_HOME",
            "description": "Base directory for user-specific data files",
            "type": "string",
            "default": "",
        })
    except Exception:
        pass


def get_data_dir(app_name: str = "pytui") -> Path:
    """Application data directory (tree-sitter, fonts, etc.). Aligns with platform/XDG."""
    if os.name == "nt":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(base) / app_name
    xdg = os.environ.get("XDG_DATA_HOME", "")
    if xdg:
        return Path(xdg) / app_name
    return Path.home() / ".local" / "share" / app_name


def get_cache_dir(app_name: str = "pytui") -> Path:
    """Cache directory. Platform/XDG aligned."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", os.path.expanduser("~")))
        return Path(base) / app_name / "cache"
    if os.environ.get("XDG_CACHE_HOME"):
        return Path(os.environ["XDG_CACHE_HOME"]) / app_name
    return Path.home() / ".cache" / app_name


def ensure_data_dir(app_name: str = "pytui") -> Path:
    """Ensure data dir exists and return path."""
    p = get_data_dir(app_name)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_cache_dir(app_name: str = "pytui") -> Path:
    """Ensure cache dir exists and return path."""
    p = get_cache_dir(app_name)
    p.mkdir(parents=True, exist_ok=True)
    return p


class DataPathsManager:
    """Manages app config/data paths; emits paths:changed. Aligns with OpenTUI DataPathsManager."""

    def __init__(self) -> None:
        self._app_name = "pytui"
        self._global_config_path: str | None = None
        self._global_config_file: str | None = None
        self._local_config_file: str | None = None
        self._global_data_path: str | None = None
        self._listeners: list[Any] = []

    def on(self, event: str, fn: Any) -> None:
        if event == "paths:changed":
            self._listeners.append(fn)

    def emit(self, event: str, paths: dict[str, str]) -> None:
        if event == "paths:changed":
            for fn in self._listeners:
                fn(paths)

    @property
    def app_name(self) -> str:
        return self._app_name

    @app_name.setter
    def app_name(self, value: str) -> None:
        if not is_valid_directory_name(value):
            raise ValueError(f'Invalid app name "{value}": must be a valid directory name')
        if self._app_name != value:
            self._app_name = value
            self._global_config_path = None
            self._global_config_file = None
            self._local_config_file = None
            self._global_data_path = None
            self.emit("paths:changed", self.to_object())

    @property
    def global_config_path(self) -> str:
        if self._global_config_path is None:
            _register_xdg_env_vars()
            home = str(Path.home())
            xdg = getattr(env, "XDG_CONFIG_HOME", "") or ""
            base = xdg or str(Path(home) / ".config")
            self._global_config_path = str(Path(base) / self._app_name)
        return self._global_config_path

    @property
    def global_config_file(self) -> str:
        if self._global_config_file is None:
            self._global_config_file = str(Path(self.global_config_path) / "init.py")
        return self._global_config_file

    @property
    def local_config_file(self) -> str:
        if self._local_config_file is None:
            self._local_config_file = str(Path.cwd() / f".{self._app_name}.py")
        return self._local_config_file

    @property
    def global_data_path(self) -> str:
        if self._global_data_path is None:
            _register_xdg_env_vars()
            home = str(Path.home())
            xdg = getattr(env, "XDG_DATA_HOME", "") or ""
            base = xdg or str(Path(home) / ".local" / "share")
            self._global_data_path = str(Path(base) / self._app_name)
        return self._global_data_path

    def to_object(self) -> dict[str, str]:
        """Return paths as dict. Aligns with OpenTUI toObject()."""
        return {
            "globalConfigPath": self.global_config_path,
            "globalConfigFile": self.global_config_file,
            "localConfigFile": self.local_config_file,
            "globalDataPath": self.global_data_path,
        }


def get_data_paths() -> DataPathsManager:
    """Singleton DataPathsManager. Aligns with OpenTUI getDataPaths()."""
    _register_xdg_env_vars()
    return singleton("data-paths-pytui", DataPathsManager)
