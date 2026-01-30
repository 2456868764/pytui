# pytui.utils

from pytui.utils.data_paths import ensure_cache_dir, ensure_data_dir, get_cache_dir, get_data_dir
from pytui.utils.diff import diff_lines
from pytui.utils.extmarks import Extmark, ExtmarksStore
from pytui.utils.scroll_acceleration import LinearScrollAccel, MacOSScrollAccel
from pytui.utils.validation import (
    validate_hex_color,
    validate_non_negative_int,
    validate_positive_int,
)

__all__ = [
    "diff_lines",
    "LinearScrollAccel",
    "MacOSScrollAccel",
    "validate_hex_color",
    "validate_non_negative_int",
    "validate_positive_int",
    "Extmark",
    "ExtmarksStore",
    "get_data_dir",
    "get_cache_dir",
    "ensure_data_dir",
    "ensure_cache_dir",
]
