# pytui.lib.renderable_validations - Aligns with OpenTUI lib/renderable.validations.ts
# validate_options, is_valid_percentage, is_margin_type, is_padding_type, is_position_type,
# is_position_type_type, is_overflow_type, is_dimension_type, is_flex_basis_type, is_size_type.
# Plus validate_positive_int, validate_non_negative_int, validate_hex_color (from utils/validation).

from typing import Any

PositionTypeString = str  # "relative" | "absolute"
OverflowString = str  # "visible" | "hidden" | "scroll"


def validate_options(id: str, options: Any) -> None:
    """Validate renderable options (width/height >= 0). Aligns with OpenTUI validateOptions()."""
    opts = options if isinstance(options, dict) else getattr(options, "__dict__", {})
    w = opts.get("width") if isinstance(opts, dict) else getattr(options, "width", None)
    h = opts.get("height") if isinstance(opts, dict) else getattr(options, "height", None)
    if isinstance(w, (int, float)) and w < 0:
        raise TypeError(f"Invalid width for Renderable {id}: {w}")
    if isinstance(h, (int, float)) and h < 0:
        raise TypeError(f"Invalid height for Renderable {id}: {h}")


def is_valid_percentage(value: Any) -> bool:
    """True if value is string ending with % and numeric part. Aligns with OpenTUI isValidPercentage()."""
    if isinstance(value, str) and value.endswith("%"):
        try:
            num = float(value[:-1])
            return True
        except ValueError:
            return False
    return False


def is_margin_type(value: Any) -> bool:
    """True if number, 'auto', or valid percentage. Aligns with OpenTUI isMarginType()."""
    if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
        return True
    if value == "auto":
        return True
    return is_valid_percentage(value)


def is_padding_type(value: Any) -> bool:
    """True if number or valid percentage. Aligns with OpenTUI isPaddingType()."""
    if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
        return True
    return is_valid_percentage(value)


def is_position_type(value: Any) -> bool:
    """True if number, 'auto', or valid percentage. Aligns with OpenTUI isPositionType()."""
    if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
        return True
    if value == "auto":
        return True
    return is_valid_percentage(value)


def is_position_type_type(value: Any) -> bool:
    """True if 'relative' or 'absolute'. Aligns with OpenTUI isPositionTypeType()."""
    return value == "relative" or value == "absolute"


def is_overflow_type(value: Any) -> bool:
    """True if 'visible', 'hidden', or 'scroll'. Aligns with OpenTUI isOverflowType()."""
    return value in ("visible", "hidden", "scroll")


def is_dimension_type(value: Any) -> bool:
    """True if position_type. Aligns with OpenTUI isDimensionType()."""
    return is_position_type(value)


def is_flex_basis_type(value: Any) -> bool:
    """True if undefined, 'auto', or number. Aligns with OpenTUI isFlexBasisType()."""
    if value is None or value == "auto":
        return True
    if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
        return True
    return False


def is_size_type(value: Any) -> bool:
    """True if undefined, number, or valid percentage. Aligns with OpenTUI isSizeType()."""
    if value is None:
        return True
    if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
        return True
    return is_valid_percentage(value)


def validate_positive_int(value: Any, name: str = "value") -> int:
    """Require positive int; else ValueError. Aligns with OpenTUI validatePositiveInt."""
    if not isinstance(value, int):
        raise ValueError(f"{name} must be int, got {type(value).__name__}: {value!r}")
    if value < 1:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_non_negative_int(value: Any, name: str = "value") -> int:
    """Require non-negative int. Aligns with OpenTUI validateNonNegativeInt."""
    if not isinstance(value, int):
        raise ValueError(f"{name} must be int, got {type(value).__name__}: {value!r}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


def validate_hex_color(value: Any, name: str = "color") -> str:
    """Require #rgb, #rrggbb, or 'transparent'. Aligns with OpenTUI validateHexColor."""
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
