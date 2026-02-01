# pytui.core.poga_layout - Adapter for poga (Python YogaLayout binding)
# Aligns with https://github.com/dzhsurf/poga CAPI: YGNodeNew, YGNodeStyleSet*, YGNodeLayoutGet*, etc.

from __future__ import annotations

from typing import Any, Literal

FlexDirection = Literal["row", "column", "row-reverse", "column-reverse"]
AlignItems = Literal["flex-start", "flex-end", "center", "stretch", "baseline"]
JustifyContent = Literal[
    "flex-start", "flex-end", "center",
    "space-between", "space-around", "space-evenly",
]

def _load_poga_capi() -> bool:
    global YGNodeNew, YGNodeFree, YGNodeFreeRecursive, YGNodeSetNodeType, YGNodeType
    global YGNodeInsertChild, YGNodeRemoveChild, YGNodeCalculateLayout
    global YGNodeLayoutGetLeft, YGNodeLayoutGetTop, YGNodeLayoutGetWidth, YGNodeLayoutGetHeight
    global YGNodeStyleSetWidth, YGNodeStyleSetHeight, YGNodeStyleSetWidthPercent, YGNodeStyleSetHeightPercent
    global YGNodeStyleSetPosition, YGNodeStyleSetPositionType
    global YGNodeStyleSetFlexDirection, YGNodeStyleSetJustifyContent, YGNodeStyleSetAlignItems, YGNodeStyleSetBorder
    global YGNodeStyleSetFlexGrow, YGNodeStyleSetFlexShrink
    global YGFlexDirection, YGJustify, YGAlign, YGEdge, YGPositionType, YGDirection, YGUndefined
    try:
        capi = __import__("poga.libpoga_capi", fromlist=[  # type: ignore[import-untyped]
            "YGNodeNew", "YGNodeInsertChild", "YGNodeCalculateLayout",
            "YGNodeLayoutGetLeft", "YGNodeLayoutGetTop", "YGNodeLayoutGetWidth", "YGNodeLayoutGetHeight",
            "YGNodeStyleSetWidth", "YGNodeStyleSetHeight", "YGNodeStyleSetPosition", "YGNodeStyleSetPositionType",
            "YGNodeStyleSetFlexDirection", "YGNodeStyleSetJustifyContent", "YGNodeStyleSetAlignItems", "YGNodeStyleSetBorder",
        ])
    except ImportError:
        return False
    YGNodeNew = getattr(capi, "YGNodeNew", None)
    if YGNodeNew is None:
        return False
    YGNodeFree = getattr(capi, "YGNodeFree", None)
    YGNodeFreeRecursive = getattr(capi, "YGNodeFreeRecursive", None)
    YGNodeSetNodeType = getattr(capi, "YGNodeSetNodeType", None)
    YGNodeType = getattr(capi, "YGNodeType", None)
    YGNodeInsertChild = getattr(capi, "YGNodeInsertChild", None)
    YGNodeRemoveChild = getattr(capi, "YGNodeRemoveChild", None)
    YGNodeCalculateLayout = getattr(capi, "YGNodeCalculateLayout", None)
    YGNodeLayoutGetLeft = getattr(capi, "YGNodeLayoutGetLeft", None)
    YGNodeLayoutGetTop = getattr(capi, "YGNodeLayoutGetTop", None)
    YGNodeLayoutGetWidth = getattr(capi, "YGNodeLayoutGetWidth", None)
    YGNodeLayoutGetHeight = getattr(capi, "YGNodeLayoutGetHeight", None)
    YGNodeStyleSetWidth = getattr(capi, "YGNodeStyleSetWidth", None)
    YGNodeStyleSetHeight = getattr(capi, "YGNodeStyleSetHeight", None)
    YGNodeStyleSetWidthPercent = getattr(capi, "YGNodeStyleSetWidthPercent", None)
    YGNodeStyleSetHeightPercent = getattr(capi, "YGNodeStyleSetHeightPercent", None)
    YGNodeStyleSetPosition = getattr(capi, "YGNodeStyleSetPosition", None)
    YGNodeStyleSetPositionType = getattr(capi, "YGNodeStyleSetPositionType", None)
    YGNodeStyleSetFlexDirection = getattr(capi, "YGNodeStyleSetFlexDirection", None)
    YGNodeStyleSetJustifyContent = getattr(capi, "YGNodeStyleSetJustifyContent", None)
    YGNodeStyleSetAlignItems = getattr(capi, "YGNodeStyleSetAlignItems", None)
    YGNodeStyleSetBorder = getattr(capi, "YGNodeStyleSetBorder", None)
    YGNodeStyleSetFlexGrow = getattr(capi, "YGNodeStyleSetFlexGrow", None)
    YGNodeStyleSetFlexShrink = getattr(capi, "YGNodeStyleSetFlexShrink", None)
    YGFlexDirection = getattr(capi, "YGFlexDirection", None)
    YGJustify = getattr(capi, "YGJustify", None)
    YGAlign = getattr(capi, "YGAlign", None)
    YGEdge = getattr(capi, "YGEdge", None)
    YGPositionType = getattr(capi, "YGPositionType", None)
    YGDirection = getattr(capi, "YGDirection", None)
    YGUndefined = getattr(capi, "YGUndefined", None)
    return (
        YGNodeInsertChild is not None
        and YGNodeCalculateLayout is not None
        and YGNodeLayoutGetLeft is not None
        and YGNodeLayoutGetTop is not None
        and YGNodeLayoutGetWidth is not None
        and YGNodeLayoutGetHeight is not None
        and YGNodeStyleSetWidth is not None
        and YGNodeStyleSetHeight is not None
    )


YGNodeNew = None
YGNodeFree = YGNodeFreeRecursive = YGNodeSetNodeType = YGNodeType = None
YGNodeInsertChild = YGNodeRemoveChild = YGNodeCalculateLayout = None
YGNodeLayoutGetLeft = YGNodeLayoutGetTop = YGNodeLayoutGetWidth = YGNodeLayoutGetHeight = None
YGNodeStyleSetWidth = YGNodeStyleSetHeight = YGNodeStyleSetWidthPercent = YGNodeStyleSetHeightPercent = None
YGNodeStyleSetPosition = YGNodeStyleSetPositionType = None
YGNodeStyleSetFlexDirection = YGNodeStyleSetJustifyContent = YGNodeStyleSetAlignItems = YGNodeStyleSetBorder = None
YGNodeStyleSetFlexGrow = YGNodeStyleSetFlexShrink = None
YGFlexDirection = YGJustify = YGAlign = YGEdge = YGPositionType = YGDirection = YGUndefined = None

_POGA_CAPI = _load_poga_capi()


def is_available() -> bool:
    return _POGA_CAPI


# Map our names to poga/Yoga C API enums (poga may use YGFlexDirection.Column etc.)
def _flex_dir(d: str) -> int:
    if not _POGA_CAPI or YGFlexDirection is None:
        return 0
    return getattr(
        YGFlexDirection,
        {"row": "Row", "column": "Column", "row-reverse": "RowReverse", "column-reverse": "ColumnReverse"}.get(d, "Column"),
        0,
    )


def _justify(j: str) -> int:
    if not _POGA_CAPI or YGJustify is None:
        return 0
    return getattr(
        YGJustify,
        {
            "flex-start": "FlexStart",
            "flex-end": "FlexEnd",
            "center": "Center",
            "space-between": "SpaceBetween",
            "space-around": "SpaceAround",
            "space-evenly": "SpaceEvenly",
        }.get(j, "FlexStart"),
        0,
    )


def _align(a: str) -> int:
    if not _POGA_CAPI or YGAlign is None:
        return 0
    return getattr(
        YGAlign,
        {"flex-start": "FlexStart", "flex-end": "FlexEnd", "center": "Center", "stretch": "Stretch", "baseline": "Baseline"}.get(a, "Stretch"),
        0,
    )


def _edge(e: str) -> int:
    if not _POGA_CAPI or YGEdge is None:
        return 0
    return getattr(YGEdge, {"left": "Left", "top": "Top", "right": "Right", "bottom": "Bottom"}.get(e.lower(), "Left"), 0)


class PogaNode:
    """Wrapper around poga YGNode; API aligned with Yoga so LayoutNode can delegate."""

    def __init__(self) -> None:
        if not _POGA_CAPI or YGNodeNew is None:
            raise RuntimeError("poga CAPI not available")
        self._node = YGNodeNew()
        if YGNodeSetNodeType and YGNodeType is not None:
            YGNodeSetNodeType(self._node, getattr(YGNodeType, "Default", 0))

    def __del__(self) -> None:
        if _POGA_CAPI and getattr(self, "_node", None) is not None and YGNodeFree is not None:
            try:
                YGNodeFree(self._node)
            except Exception:
                pass
            self._node = None

    def set_flex_direction(self, direction: FlexDirection) -> None:
        if YGNodeStyleSetFlexDirection is not None:
            YGNodeStyleSetFlexDirection(self._node, _flex_dir(direction))

    def set_flex_wrap(self, wrap: Literal["wrap", "nowrap"]) -> None:
        pass  # poga CAPI may have YGNodeStyleSetFlexWrap; optional

    def set_align_items(self, align: AlignItems) -> None:
        if YGNodeStyleSetAlignItems is not None:
            YGNodeStyleSetAlignItems(self._node, _align(align))

    def set_justify_content(self, justify: JustifyContent) -> None:
        if YGNodeStyleSetJustifyContent is not None:
            YGNodeStyleSetJustifyContent(self._node, _justify(justify))

    def set_gap(self, gap_or_gutter: float | str, value: float | None = None) -> None:
        # Yoga 2.0+ gap; poga may expose YGNodeStyleSetGap(edge, value)
        pass

    def set_border(self, edge: str, value: float) -> None:
        if YGNodeStyleSetBorder is not None:
            YGNodeStyleSetBorder(self._node, _edge(edge), float(value))

    def set_flex_grow(self, grow: float) -> None:
        if YGNodeStyleSetFlexGrow is not None:
            YGNodeStyleSetFlexGrow(self._node, float(grow))

    def set_flex_shrink(self, shrink: float) -> None:
        if YGNodeStyleSetFlexShrink is not None:
            YGNodeStyleSetFlexShrink(self._node, float(shrink))

    def set_flex_basis(self, basis: int | Literal["auto"]) -> None:
        pass

    def set_width(self, width: int | str) -> None:
        if YGNodeStyleSetWidth is None:
            return
        if isinstance(width, (int, float)):
            YGNodeStyleSetWidth(self._node, float(width))
        elif width == "auto":
            if YGUndefined is not None:
                YGNodeStyleSetWidth(self._node, YGUndefined)
        elif isinstance(width, str) and width.endswith("%") and YGNodeStyleSetWidthPercent is not None:
            YGNodeStyleSetWidthPercent(self._node, float(width[:-1]))

    def set_height(self, height: int | str) -> None:
        if YGNodeStyleSetHeight is None:
            return
        if isinstance(height, (int, float)):
            YGNodeStyleSetHeight(self._node, float(height))
        elif height == "auto":
            if YGUndefined is not None:
                YGNodeStyleSetHeight(self._node, YGUndefined)
        elif isinstance(height, str) and height.endswith("%") and YGNodeStyleSetHeightPercent is not None:
            YGNodeStyleSetHeightPercent(self._node, float(height[:-1]))

    def set_position_type(self, position: Literal["relative", "absolute"]) -> None:
        if YGNodeStyleSetPositionType is not None and YGPositionType is not None:
            v = getattr(YGPositionType, "Absolute", 1) if position == "absolute" else getattr(YGPositionType, "Relative", 0)
            YGNodeStyleSetPositionType(self._node, v)

    def set_position(self, edge: str, value: int | str) -> None:
        if YGNodeStyleSetPosition is None:
            return
        try:
            v = float(value) if isinstance(value, (int, float)) else 0.0
        except (TypeError, ValueError):
            v = 0.0
        YGNodeStyleSetPosition(self._node, _edge(edge), v)

    def insert_child(self, child: "PogaNode", index: int) -> None:
        if YGNodeInsertChild is not None and isinstance(child, PogaNode):
            YGNodeInsertChild(self._node, child._node, index)

    def remove_child(self, child: "PogaNode") -> None:
        if YGNodeRemoveChild is not None and isinstance(child, PogaNode):
            YGNodeRemoveChild(self._node, child._node)

    def calculate_layout(
        self,
        width: float = float("nan"),
        height: float = float("nan"),
        direction: Literal["ltr", "rtl"] = "ltr",
    ) -> None:
        if YGNodeCalculateLayout is None:
            return
        w = width if width == width else (YGUndefined if YGUndefined is not None else 0.0)  # noqa: PLR1714
        h = height if height == height else (YGUndefined if YGUndefined is not None else 0.0)  # noqa: PLR1714
        d = getattr(YGDirection, "RTL", 1) if direction == "rtl" else getattr(YGDirection, "LTR", 0)
        YGNodeCalculateLayout(self._node, w, h, d)

    def get_computed_left(self) -> float:
        if YGNodeLayoutGetLeft is not None:
            return float(YGNodeLayoutGetLeft(self._node))
        return 0.0

    def get_computed_top(self) -> float:
        if YGNodeLayoutGetTop is not None:
            return float(YGNodeLayoutGetTop(self._node))
        return 0.0

    def get_computed_width(self) -> float:
        if YGNodeLayoutGetWidth is not None:
            return float(YGNodeLayoutGetWidth(self._node))
        return 80.0

    def get_computed_height(self) -> float:
        if YGNodeLayoutGetHeight is not None:
            return float(YGNodeLayoutGetHeight(self._node))
        return 24.0
