# pytui.lib.styled_text - Aligns with OpenTUI lib/styled-text.ts
# StyledText, TextChunk, stringToStyledText, isStyledText, createTextAttributes, StyleAttrs.

from __future__ import annotations

from typing import Any

# Brand for is_styled_text. Aligns OpenTUI BrandedStyledText.
_STYLED_TEXT_MARKER = "__styled_text__"


class TextAttributes:
    """Align with OpenTUI types.ts TextAttributes."""
    NONE = 0
    BOLD = 1 << 0
    DIM = 1 << 1
    ITALIC = 1 << 2
    UNDERLINE = 1 << 3
    BLINK = 1 << 4
    INVERSE = 1 << 5
    HIDDEN = 1 << 6
    STRIKETHROUGH = 1 << 7


def create_text_attributes(
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    dim: bool = False,
    strikethrough: bool = False,
    reverse: bool = False,
    blink: bool = False,
    **kwargs: Any,
) -> int:
    """Align with OpenTUI createTextAttributes. Returns bitmask."""
    attrs = TextAttributes.NONE
    if bold:
        attrs |= TextAttributes.BOLD
    if italic:
        attrs |= TextAttributes.ITALIC
    if underline:
        attrs |= TextAttributes.UNDERLINE
    if dim:
        attrs |= TextAttributes.DIM
    if strikethrough:
        attrs |= TextAttributes.STRIKETHROUGH
    if reverse:
        attrs |= TextAttributes.INVERSE
    if blink:
        attrs |= TextAttributes.BLINK
    return attrs


def string_to_styled_text(content: str) -> StyledText:
    """Create StyledText from plain string. Aligns OpenTUI stringToStyledText()."""
    chunk = {"__is_chunk": True, "text": content}
    return StyledText([chunk])


def is_styled_text(obj: Any) -> bool:
    """Return True if obj is a StyledText instance. Aligns OpenTUI isStyledText()."""
    return isinstance(obj, StyledText) or getattr(obj, _STYLED_TEXT_MARKER, False) is True


class StyledText:
    """Align with OpenTUI StyledText. chunks: list of TextChunk dicts."""

    def __init__(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks = chunks
        setattr(self, _STYLED_TEXT_MARKER, True)
