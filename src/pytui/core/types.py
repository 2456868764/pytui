# pytui.core.types - Aligns with OpenTUI core/types.ts
# TextAttributes, CursorStyle, WidthMethod, ViewportBounds, Highlight, LineInfo, CapturedSpan/Line/Frame.

from __future__ import annotations

from enum import IntEnum
from typing import Any, Literal, Protocol, TypedDict

# --- TextAttributes (aligns OpenTUI types.ts TextAttributes) ---
class TextAttributes:
    NONE = 0
    BOLD = 1 << 0   # 1
    DIM = 1 << 1   # 2
    ITALIC = 1 << 2   # 4
    UNDERLINE = 1 << 3   # 8
    BLINK = 1 << 4   # 16
    INVERSE = 1 << 5   # 32
    HIDDEN = 1 << 6   # 64
    STRIKETHROUGH = 1 << 7   # 128


ATTRIBUTE_BASE_BITS = 8
ATTRIBUTE_BASE_MASK = 0xFF


def get_base_attributes(attr: int) -> int:
    """Extract the base 8 bits of attributes from a u32 attribute value. Aligns OpenTUI getBaseAttributes."""
    return attr & ATTRIBUTE_BASE_MASK


CursorStyle = Literal["block", "line", "underline"]


class CursorStyleOptions(TypedDict, total=False):
    style: CursorStyle
    blinking: bool


class DebugOverlayCorner(IntEnum):
    top_left = 0
    top_right = 1
    bottom_left = 2
    bottom_right = 3


WidthMethod = Literal["wcwidth", "unicode"]


class ViewportBounds(TypedDict):
    x: int
    y: int
    width: int
    height: int


class Highlight(TypedDict, total=False):
    start: int
    end: int
    style_id: int
    priority: int | None
    hl_ref: int | None


class LineInfo(TypedDict):
    line_starts: list[int]
    line_widths: list[int]
    max_line_width: int
    line_sources: list[int]
    line_wraps: list[int]


class LineInfoProvider(Protocol):
    @property
    def line_info(self) -> LineInfo:
        ...

    @property
    def line_count(self) -> int:
        ...

    @property
    def virtual_line_count(self) -> int:
        ...

    @property
    def scroll_y(self) -> int:
        ...


class CapturedSpan(TypedDict):
    text: str
    fg: Any  # RGBA
    bg: Any  # RGBA
    attributes: int
    width: int


class CapturedLine(TypedDict):
    spans: list[CapturedSpan]


class CapturedFrame(TypedDict):
    cols: int
    rows: int
    cursor: tuple[int, int]
    lines: list[CapturedLine]
