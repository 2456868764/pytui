# pytui.lib.yoga_options - Aligns with OpenTUI lib/yoga.options.ts (optional)
# String-to-layout constant parsers. PyTUI may use a different layout backend; values are string tokens.

from __future__ import annotations


def _lower(value: str | None) -> str:
    return (value or "").lower()


def parse_align(value: str | None) -> str:
    """Align with OpenTUI parseAlign. Returns token: auto, flex-start, center, flex-end, stretch, baseline, space-between, space-around, space-evenly."""
    v = _lower(value)
    if v in ("auto", "flex-start", "center", "flex-end", "stretch", "baseline", "space-between", "space-around", "space-evenly"):
        return v
    return "auto"


def parse_align_items(value: str | None) -> str:
    """Align with OpenTUI parseAlignItems. Default stretch."""
    v = _lower(value)
    if v in ("auto", "flex-start", "center", "flex-end", "stretch", "baseline", "space-between", "space-around", "space-evenly"):
        return v
    return "stretch"


def parse_flex_direction(value: str | None) -> str:
    """Align with OpenTUI parseFlexDirection. Returns column, column-reverse, row, row-reverse."""
    v = _lower(value)
    if v in ("column", "column-reverse", "row", "row-reverse"):
        return v
    return "column"


def parse_justify(value: str | None) -> str:
    """Align with OpenTUI parseJustify. Returns flex-start, center, flex-end, space-between, space-around, space-evenly."""
    v = _lower(value)
    if v in ("flex-start", "center", "flex-end", "space-between", "space-around", "space-evenly"):
        return v
    return "flex-start"


def parse_display(value: str | None) -> str:
    """Align with OpenTUI parseDisplay. Returns flex, none, contents."""
    v = _lower(value)
    if v in ("flex", "none", "contents"):
        return v
    return "flex"


def parse_position_type(value: str | None) -> str:
    """Align with OpenTUI parsePositionType. Returns static, relative, absolute."""
    v = _lower(value)
    if v in ("static", "relative", "absolute"):
        return v
    return "relative"


def parse_overflow(value: str | None) -> str:
    """Align with OpenTUI parseOverflow. Returns visible, hidden, scroll."""
    v = _lower(value)
    if v in ("visible", "hidden", "scroll"):
        return v
    return "visible"


def parse_wrap(value: str | None) -> str:
    """Align with OpenTUI parseWrap. Returns no-wrap, wrap, wrap-reverse."""
    v = _lower(value)
    if v in ("no-wrap", "wrap", "wrap-reverse"):
        return v
    return "no-wrap"
