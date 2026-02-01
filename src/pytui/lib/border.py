# pytui.lib.border - Aligns with OpenTUI lib/border.ts
# BorderChars, BorderStyle, isValidBorderStyle, parseBorderStyle, getBorderSides, getBorderFromSides,
# borderCharsToArray, BorderCharArrays, BorderConfig, BoxDrawOptions.

from __future__ import annotations

import logging
from typing import Any, Literal

BorderStyle = Literal["single", "double", "rounded", "heavy"]
BorderSides = Literal["top", "right", "bottom", "left"]

VALID_BORDER_STYLES: tuple[BorderStyle, ...] = ("single", "double", "rounded", "heavy")


def is_valid_border_style(value: Any) -> bool:
    """Return True if value is a valid BorderStyle. Aligns with OpenTUI isValidBorderStyle()."""
    return value in VALID_BORDER_STYLES


def parse_border_style(
    value: Any,
    fallback: BorderStyle = "single",
) -> BorderStyle:
    """Parse border style; invalid values fall back to fallback. Aligns with OpenTUI parseBorderStyle().
    Logs a warning only for invalid non-None values."""
    if is_valid_border_style(value):
        return value
    if value is not None:
        logging.warning(
            'Invalid borderStyle "%s", falling back to "%s". Valid values are: %s',
            value,
            fallback,
            ", ".join(VALID_BORDER_STYLES),
        )
    return fallback


class BorderCharacters:
    """Border character set. Aligns with OpenTUI BorderCharacters."""

    __slots__ = (
        "top_left", "top_right", "bottom_left", "bottom_right",
        "horizontal", "vertical", "top_t", "bottom_t", "left_t", "right_t", "cross",
    )

    def __init__(
        self,
        top_left: str,
        top_right: str,
        bottom_left: str,
        bottom_right: str,
        horizontal: str,
        vertical: str,
        top_t: str,
        bottom_t: str,
        left_t: str,
        right_t: str,
        cross: str,
    ) -> None:
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.horizontal = horizontal
        self.vertical = vertical
        self.top_t = top_t
        self.bottom_t = bottom_t
        self.left_t = left_t
        self.right_t = right_t
        self.cross = cross


BorderChars: dict[BorderStyle, BorderCharacters] = {
    "single": BorderCharacters(
        top_left="┌", top_right="┐", bottom_left="└", bottom_right="┘",
        horizontal="─", vertical="│", top_t="┬", bottom_t="┴", left_t="├", right_t="┤", cross="┼",
    ),
    "double": BorderCharacters(
        top_left="╔", top_right="╗", bottom_left="╚", bottom_right="╝",
        horizontal="═", vertical="║", top_t="╦", bottom_t="╩", left_t="╠", right_t="╣", cross="╬",
    ),
    "rounded": BorderCharacters(
        top_left="╭", top_right="╮", bottom_left="╰", bottom_right="╯",
        horizontal="─", vertical="│", top_t="┬", bottom_t="┴", left_t="├", right_t="┤", cross="┼",
    ),
    "heavy": BorderCharacters(
        top_left="┏", top_right="┓", bottom_left="┗", bottom_right="┛",
        horizontal="━", vertical="┃", top_t="┳", bottom_t="┻", left_t="┣", right_t="┫", cross="╋",
    ),
}


class BorderSidesConfig:
    """Which sides have border. Aligns with OpenTUI BorderSidesConfig."""

    __slots__ = ("top", "right", "bottom", "left")

    def __init__(self, top: bool, right: bool, bottom: bool, left: bool) -> None:
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            return (
                self.top == other.get("top", False)
                and self.right == other.get("right", False)
                and self.bottom == other.get("bottom", False)
                and self.left == other.get("left", False)
            )
        return NotImplemented


def get_border_sides(border: bool | list[BorderSides]) -> BorderSidesConfig:
    """Convert border option to sides config. Aligns with OpenTUI getBorderSides()."""
    if border is True:
        return BorderSidesConfig(True, True, True, True)
    if isinstance(border, list):
        return BorderSidesConfig(
            top="top" in border,
            right="right" in border,
            bottom="bottom" in border,
            left="left" in border,
        )
    return BorderSidesConfig(False, False, False, False)


def get_border_from_sides(sides: BorderSidesConfig) -> bool | list[BorderSides]:
    """Convert sides config to border option. Aligns with OpenTUI getBorderFromSides()."""
    out: list[BorderSides] = []
    if sides.top:
        out.append("top")
    if sides.right:
        out.append("right")
    if sides.bottom:
        out.append("bottom")
    if sides.left:
        out.append("left")
    return out if out else False


def border_chars_to_array(chars: BorderCharacters | dict[str, str]) -> list[int]:
    """Code points for border chars [tl, tr, bl, br, h, v, topT, bottomT, leftT, rightT, cross].
    Aligns with OpenTUI borderCharsToArray(). Accepts BorderCharacters or dict with same keys."""
    def code(s: str) -> int:
        return ord(s[0]) if s else 0
    if isinstance(chars, dict):
        def get(*keys: str) -> str:
            for k in keys:
                if k in chars:
                    return chars[k]
            return ""
        return [
            code(get("top_left", "topLeft", "tl")),
            code(get("top_right", "topRight", "tr")),
            code(get("bottom_left", "bottomLeft", "bl")),
            code(get("bottom_right", "bottomRight", "br")),
            code(get("horizontal", "h")),
            code(get("vertical", "v")),
            code(get("top_t", "topT")),
            code(get("bottom_t", "bottomT")),
            code(get("left_t", "leftT")),
            code(get("right_t", "rightT")),
            code(get("cross")),
        ]
    return [
        code(chars.top_left),
        code(chars.top_right),
        code(chars.bottom_left),
        code(chars.bottom_right),
        code(chars.horizontal),
        code(chars.vertical),
        code(chars.top_t),
        code(chars.bottom_t),
        code(chars.left_t),
        code(chars.right_t),
        code(chars.cross),
    ]


# Pre-converted for performance (list of code points per style)
BorderCharArrays: dict[BorderStyle, list[int]] = {
    style: border_chars_to_array(chars) for style, chars in BorderChars.items()
}
