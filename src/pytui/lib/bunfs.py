# pytui.lib.bunfs - Aligns with OpenTUI lib/bunfs.ts
# isBunfsPath, getBunfsRootPath, normalizeBunfsPath (Bun embedded FS; Python: pathlib-based)

from __future__ import annotations

import re
import sys
from pathlib import Path


def is_bunfs_path(path: str) -> bool:
    """Align with OpenTUI isBunfsPath. True if path contains '$bunfs' or matches B:[\\/]~BUN (any platform)."""
    if "$bunfs" in path:
        return True
    if re.match(r"^B:[\\/]~BUN", path, re.IGNORECASE):
        return True
    return False


def get_bunfs_root_path() -> str:
    """Align with OpenTUI getBunfsRootPath. Platform-specific Bun embedded root."""
    if sys.platform == "win32":
        return "B:\\~BUN\\root"
    return "/$bunfs/root"


def normalize_bunfs_path(file_name: str) -> str:
    """Align with OpenTUI normalizeBunfsPath. Flattens to root + basename so file exists at root."""
    root = get_bunfs_root_path()
    base = Path(file_name).name
    if sys.platform == "win32":
        return root.rstrip("\\") + "\\" + base
    return root.rstrip("/") + "/" + base
