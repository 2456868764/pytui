# pytui.lib.validate_dir_name - Aligns with OpenTUI lib/validate-dir-name.ts

import re

RESERVED_NAMES = [
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
]

# Windows: < > : " | ? * \ and control characters (0-31)
# Unix: null character and forward slash
INVALID_CHARS = re.compile(r'[<>:"|?*\/\\\x00-\x1f]')


def is_valid_directory_name(name: str) -> bool:
    """Returns True if the name is valid for a directory. Aligns with OpenTUI isValidDirectoryName()."""
    if not name or not isinstance(name, str):
        return False
    if not name.strip():
        return False
    if name.upper() in RESERVED_NAMES:
        return False
    if INVALID_CHARS.search(name):
        return False
    if name.endswith(".") or name.endswith(" "):
        return False
    if name in (".", ".."):
        return False
    return True
