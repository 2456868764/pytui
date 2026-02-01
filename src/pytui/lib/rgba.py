# pytui.lib.rgba - Aligns with OpenTUI lib/RGBA.ts
# RGBA, hexToRgb, rgbToHex, parseColor, hsvToRgb. Internal storage 0-255 (Python); API matches OpenTUI (fromValues 0-1).

from __future__ import annotations

from typing import Callable, Sequence, Union

# CSS color names -> #rrggbb (OpenTUI RGBA.ts CSS_COLOR_NAMES)
_CSS_COLOR_NAMES: dict[str, str] = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#008000",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "silver": "#C0C0C0",
    "gray": "#808080",
    "grey": "#808080",
    "maroon": "#800000",
    "olive": "#808000",
    "lime": "#00FF00",
    "aqua": "#00FFFF",
    "teal": "#008080",
    "navy": "#000080",
    "fuchsia": "#FF00FF",
    "purple": "#800080",
    "orange": "#FFA500",
    "brightblack": "#666666",
    "brightred": "#FF6666",
    "brightgreen": "#66FF66",
    "brightblue": "#6666FF",
    "brightyellow": "#FFFF66",
    "brightcyan": "#66FFFF",
    "brightmagenta": "#FF66FF",
    "brightwhite": "#FFFFFF",
}


class RGBA:
    """RGBA color. Storage r,g,b,a 0-255. Aligns with OpenTUI RGBA (OpenTUI uses 0-1 Float32Array)."""

    __slots__ = ("r", "g", "b", "a")

    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255) -> None:
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.a = max(0, min(255, a))

    @classmethod
    def from_hex(cls, value: str) -> RGBA:
        """From hex string. Aligns OpenTUI RGBA.fromHex()."""
        return hex_to_rgb(value)

    @classmethod
    def from_array(cls, arr: Sequence[Union[int, float]]) -> RGBA:
        """From [r,g,b,a] (0-255 int or 0-1 float). Aligns OpenTUI RGBA.fromArray()."""
        if len(arr) < 4:
            return cls(0, 0, 0, 255)
        r, g, b, a = arr[0], arr[1], arr[2], arr[3]
        if isinstance(r, float) and 0 <= r <= 1:
            return cls.from_values(float(r), float(g), float(b), float(a))
        return cls(int(r), int(g), int(b), int(a))

    @classmethod
    def from_ints(cls, r: int, g: int, b: int, a: int = 255) -> RGBA:
        """From 0-255 ints. Aligns OpenTUI RGBA.fromInts()."""
        return cls(r, g, b, a)

    @classmethod
    def from_values(cls, r: float, g: float, b: float, a: float = 1.0) -> RGBA:
        """From 0-1 float. Aligns OpenTUI RGBA.fromValues()."""
        return cls(
            int(round(r * 255)),
            int(round(g * 255)),
            int(round(b * 255)),
            int(round(a * 255)),
        )

    def to_tuple(self) -> tuple[int, int, int, int]:
        """(r, g, b, a) 0-255. Aligns OpenTUI toInts()."""
        return (self.r, self.g, self.b, self.a)

    def to_ints(self) -> tuple[int, int, int, int]:
        """Alias for to_tuple(). Aligns OpenTUI toInts()."""
        return self.to_tuple()

    def map(self, fn: Callable[[int], int]) -> list[int]:
        """Apply fn to r,g,b,a. Aligns OpenTUI map()."""
        return [fn(self.r), fn(self.g), fn(self.b), fn(self.a)]

    def __str__(self) -> str:
        """Aligns OpenTUI toString() – rgba(r,g,b,a) with 0-1 values for display."""
        return f"rgba({self.r / 255:.2f}, {self.g / 255:.2f}, {self.b / 255:.2f}, {self.a / 255:.2f})"

    def equals(self, other: RGBA | None) -> bool:
        """Aligns OpenTUI equals()."""
        if other is None:
            return False
        return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RGBA):
            return False
        return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def __repr__(self) -> str:
        return f"RGBA({self.r},{self.g},{self.b},{self.a})"


def hex_to_rgb(hex_str: str) -> RGBA:
    """Aligns OpenTUI hexToRgb(). Invalid hex defaults to magenta."""
    hex_str = hex_str.replace("#", "").strip()
    if len(hex_str) == 3:
        hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2
    elif len(hex_str) == 4:
        hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2 + hex_str[3] * 2
    if len(hex_str) not in (6, 8) or not all(c in "0123456789AaBbCcDdEeFf" for c in hex_str):
        return RGBA.from_values(1, 0, 1, 1)
    r = int(hex_str[0:2], 16) / 255
    g = int(hex_str[2:4], 16) / 255
    b = int(hex_str[4:6], 16) / 255
    a = int(hex_str[6:8], 16) / 255 if len(hex_str) == 8 else 1.0
    return RGBA.from_values(r, g, b, a)


def rgb_to_hex(rgb: RGBA) -> str:
    """Aligns OpenTUI rgbToHex() – #rrggbb or #rrggbbaa."""
    if rgb.a == 255:
        return f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"
    return f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}{rgb.a:02x}"


def hsv_to_rgb(h: float, s: float, v: float) -> RGBA:
    """Aligns OpenTUI hsvToRgb()."""
    r = g = b = 0.0
    i = int(h / 60) % 6
    f = h / 60 - int(h / 60)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return RGBA.from_values(r, g, b, 1.0)


ColorInput = Union[str, RGBA, None]


def parse_color(color: ColorInput) -> RGBA:
    """Aligns OpenTUI parseColor(): string (transparent, CSS name, hex) or RGBA pass-through."""
    if color is None:
        return RGBA.from_values(0, 0, 0, 0)
    if isinstance(color, RGBA):
        return color
    s = str(color).strip()
    if not s or s.lower() == "transparent":
        return RGBA.from_values(0, 0, 0, 0)
    lower = s.lower()
    if lower in _CSS_COLOR_NAMES:
        return hex_to_rgb(_CSS_COLOR_NAMES[lower])
    return hex_to_rgb(s)


def parse_color_to_tuple(color: ColorInput) -> tuple[int, int, int, int]:
    """Parse color to (r, g, b, a) tuple for Cell fg/bg. Uses parse_color().to_tuple()."""
    return parse_color(color).to_tuple()
