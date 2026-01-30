# pytui.utils.validation - 参数校验与错误信息

from typing import Any


def validate_positive_int(value: Any, name: str = "value") -> int:
    """要求为正整数，否则抛出 ValueError 并附带清晰错误信息。"""
    if not isinstance(value, int):
        raise ValueError(f"{name} must be int, got {type(value).__name__}: {value!r}")
    if value < 1:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_non_negative_int(value: Any, name: str = "value") -> int:
    """要求为非负整数。"""
    if not isinstance(value, int):
        raise ValueError(f"{name} must be int, got {type(value).__name__}: {value!r}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


def validate_hex_color(value: Any, name: str = "color") -> str:
    """要求为 #rgb 或 #rrggbb 或 'transparent'。"""
    if not isinstance(value, str):
        raise ValueError(f"{name} must be str, got {type(value).__name__}: {value!r}")
    s = value.strip().lower()
    if s == "transparent":
        return s
    if s.startswith("#"):
        rest = s[1:]
        if len(rest) in (3, 6) and all(c in "0123456789abcdef" for c in rest):
            return value
    raise ValueError(f"{name} must be #rgb, #rrggbb, or 'transparent', got {value!r}")
