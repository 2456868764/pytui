# pytui.core.layout - Yoga layout or stub

from typing import Literal

FlexDirection = Literal["row", "column", "row-reverse", "column-reverse"]
AlignItems = Literal["flex-start", "flex-end", "center", "stretch", "baseline"]
JustifyContent = Literal[
    "flex-start", "flex-end", "center",
    "space-between", "space-around", "space-evenly",
]

try:
    import yoga  # type: ignore[import-untyped]

    HAS_YOGA = True
except ImportError:
    HAS_YOGA = False
    yoga = None  # type: ignore[assignment]


class _StubLayoutNode:
    """Stub layout (no Yoga): flexbox-like column/row, justify/align, flex_grow, gap, padding, % sizing."""

    def __init__(self) -> None:
        self.children: list[_StubLayoutNode] = []
        self._width: float = 0.0
        self._height: float = 0.0
        self._x = 0.0
        self._y = 0.0
        self._width_is_pct = False
        self._height_is_pct = False
        self._padding_left = 0.0
        self._padding_top = 0.0
        self._padding_right = 0.0
        self._padding_bottom = 0.0
        self._flex_direction: FlexDirection = "column"
        self._justify_content: JustifyContent = "flex-start"
        self._align_items: AlignItems = "stretch"
        self._gap: float = 0.0
        self._flex_grow: float = 0.0
        self._position_type: Literal["relative", "absolute"] = "relative"
        self._pos_left: int | str | None = None
        self._pos_top: int | str | None = None
        self._pos_right: int | str | None = None
        self._pos_bottom: int | str | None = None
        self._border_left = 0.0
        self._border_right = 0.0
        self._border_top = 0.0
        self._border_bottom = 0.0
        self._row_gap = 0.0
        self._column_gap = 0.0

    def set_border(self, edge: str, value: float) -> None:
        """Set border width for edge (left, top, right, bottom). Aligns OpenTUI Edge + setBorder."""
        if edge == "left":
            self._border_left = value
        elif edge == "top":
            self._border_top = value
        elif edge == "right":
            self._border_right = value
        elif edge == "bottom":
            self._border_bottom = value

    def set_gap(self, gap_or_gutter: float | str, value: float | None = None) -> None:
        """Set gap. One arg: set_gap(gap). Two args: set_gap(gutter, value) with gutter 'all'|'row'|'column' (OpenTUI Gutter)."""
        if value is None:
            self._gap = float(gap_or_gutter)
            self._row_gap = float(gap_or_gutter)
            self._column_gap = float(gap_or_gutter)
        else:
            gutter = gap_or_gutter
            v = float(value)
            if gutter == "row":
                self._row_gap = v
            elif gutter == "column":
                self._column_gap = v
            else:
                self._gap = v
                self._row_gap = v
                self._column_gap = v

    def set_position_type(self, position: Literal["relative", "absolute"]) -> None:
        self._position_type = position

    def set_position(self, edge: str, value: int | str) -> None:
        """value: number, 'auto', or '{number}%' (e.g. '50%')."""
        if edge == "left":
            self._pos_left = value
        elif edge == "top":
            self._pos_top = value
        elif edge == "right":
            self._pos_right = value
        elif edge == "bottom":
            self._pos_bottom = value

    def set_flex_direction(self, direction: FlexDirection) -> None:
        self._flex_direction = direction

    def set_flex_wrap(self, wrap: Literal["wrap", "nowrap"]) -> None:
        pass

    def set_align_items(self, align: AlignItems) -> None:
        self._align_items = align

    def set_justify_content(self, justify: JustifyContent) -> None:
        self._justify_content = justify

    def set_flex_grow(self, grow: float) -> None:
        self._flex_grow = grow

    def set_flex_shrink(self, shrink: float) -> None:
        pass

    def set_flex_basis(self, basis: int | Literal["auto"]) -> None:
        pass

    def set_gap(self, gap_or_gutter: float | str, value: float | None = None) -> None:
        if value is None:
            self._gap = float(gap_or_gutter)
            self._row_gap = float(gap_or_gutter)
            self._column_gap = float(gap_or_gutter)
        else:
            gutter = gap_or_gutter
            v = float(value)
            if gutter == "row":
                self._row_gap = v
            elif gutter == "column":
                self._column_gap = v
            else:
                self._gap = v
                self._row_gap = v
                self._column_gap = v

    def set_width(self, width: int | str) -> None:
        if isinstance(width, int):
            self._width = float(width)
            self._width_is_pct = False
        elif width == "auto":
            self._width = 0.0
            self._width_is_pct = False
        elif isinstance(width, str) and width.endswith("%"):
            self._width = float(width[:-1])
            self._width_is_pct = True

    def set_height(self, height: int | str) -> None:
        if isinstance(height, int):
            self._height = float(height)
            self._height_is_pct = False
        elif height == "auto":
            self._height = 0.0
            self._height_is_pct = False
        elif isinstance(height, str) and height.endswith("%"):
            self._height = float(height[:-1])
            self._height_is_pct = True

    def set_min_width(self, width: int) -> None:
        pass

    def set_min_height(self, height: int) -> None:
        pass

    def set_max_width(self, width: int) -> None:
        pass

    def set_max_height(self, height: int) -> None:
        pass

    def set_margin(self, edge: str, value: int | str) -> None:
        pass

    def set_padding(self, edge: str, value: int | str) -> None:
        v = float(value) if isinstance(value, (int, float)) else 0.0
        if edge == "all":
            self._padding_left = self._padding_top = self._padding_right = self._padding_bottom = v
        elif edge == "left":
            self._padding_left = v
        elif edge == "top":
            self._padding_top = v
        elif edge == "right":
            self._padding_right = v
        elif edge == "bottom":
            self._padding_bottom = v

    def insert_child(self, child: "_StubLayoutNode", index: int) -> None:
        self.children.insert(index, child)

    def remove_child(self, child: "_StubLayoutNode") -> None:
        if child in self.children:
            self.children.remove(child)

    def _resolve_pct(self, avail_w: float, avail_h: float) -> None:
        if self._width_is_pct and avail_w > 0:
            self._width = avail_w * self._width / 100.0
            self._width_is_pct = False
        if self._height_is_pct and avail_h > 0:
            self._height = avail_h * self._height / 100.0
            self._height_is_pct = False

    def calculate_layout(
        self,
        width: float = float("nan"),
        height: float = float("nan"),
        direction: Literal["ltr", "rtl"] = "ltr",
    ) -> None:
        nan = float("nan")
        has_w = not (width != width)  # not nan
        has_h = not (height != height)
        if has_w and self._width_is_pct:
            self._width = width * self._width / 100.0
            self._width_is_pct = False
        if has_h and self._height_is_pct:
            self._height = height * self._height / 100.0
            self._height_is_pct = False
        if has_w and self._width == 0:
            self._width = width
        if has_h and self._height == 0:
            self._height = height
        inner_w = max(0.0, self.get_computed_width() - self._padding_left - self._padding_right)
        inner_h = max(0.0, self.get_computed_height() - self._padding_top - self._padding_bottom)
        if inner_w <= 0:
            inner_w = 80.0
        if inner_h <= 0:
            inner_h = 24.0
        for c in self.children:
            c._resolve_pct(inner_w, inner_h)
            if hasattr(c, "calculate_layout"):
                c.calculate_layout(inner_w, inner_h, direction)
        n = len(self.children)
        gap = self._gap
        is_row = self._flex_direction in ("row", "row-reverse")
        main_size = inner_w if is_row else inner_h
        cross_size = inner_h if is_row else inner_w
        main_sizes: list[float] = []
        cross_sizes: list[float] = []
        for c in self.children:
            cw = c.get_computed_width() if c.get_computed_width() > 0 else (inner_w if is_row else 0)
            ch = c.get_computed_height() if c.get_computed_height() > 0 else (inner_h if not is_row else 0)
            if is_row:
                main_sizes.append(cw if cw > 0 else 0)
                cross_sizes.append(ch if ch > 0 else cross_size)
            else:
                main_sizes.append(ch if ch > 0 else 0)
                cross_sizes.append(cw if cw > 0 else cross_size)
        total_main = sum(main_sizes) + gap * max(0, n - 1)
        grow_total = sum(getattr(c, "_flex_grow", 0.0) for c in self.children)
        if grow_total > 0 and total_main < main_size:
            extra = main_size - total_main
            for i, c in enumerate(self.children):
                g = getattr(c, "_flex_grow", 0.0)
                if g > 0:
                    add = extra * g / grow_total
                    if is_row:
                        c._width = main_sizes[i] + add
                        main_sizes[i] = c._width
                    else:
                        c._height = main_sizes[i] + add
                        main_sizes[i] = c._height
            total_main = main_size
        if self._align_items == "stretch":
            for i, c in enumerate(self.children):
                if is_row:
                    if getattr(c, "_height", 0) <= 0:
                        c._height = cross_size
                else:
                    if getattr(c, "_width", 0) <= 0:
                        c._width = cross_size
                cross_sizes[i] = cross_size
        justify_off = 0.0
        if self._justify_content == "flex-end":
            justify_off = main_size - total_main
        elif self._justify_content == "center":
            justify_off = (main_size - total_main) * 0.5
        elif self._justify_content == "space-between" and n > 1:
            gap = (main_size - sum(main_sizes)) / (n - 1)
        elif self._justify_content == "space-around" and n > 0:
            gap = (main_size - sum(main_sizes)) / n
            justify_off = gap * 0.5
        elif self._justify_content == "space-evenly" and n > 0:
            gap = (main_size - sum(main_sizes)) / (n + 1)
            justify_off = gap
        main_off = self._padding_left if is_row else self._padding_top
        main_off += justify_off
        for i, c in enumerate(self.children):
            cross_off = self._padding_top if is_row else self._padding_left
            if self._align_items == "flex-end":
                cross_off += cross_size - cross_sizes[i]
            elif self._align_items == "center":
                cross_off += (cross_size - cross_sizes[i]) * 0.5
            if is_row:
                c._x = self._padding_left + main_off
                c._y = self._padding_top + cross_off
                main_off += main_sizes[i] + gap
            else:
                c._x = self._padding_left + cross_off
                c._y = self._padding_top + main_off
                main_off += main_sizes[i] + gap
        if self._flex_direction == "row-reverse":
            for c in self.children:
                c._x = self.get_computed_width() - c._x - c.get_computed_width()
        elif self._flex_direction == "column-reverse":
            for c in self.children:
                c._y = self.get_computed_height() - c._y - c.get_computed_height()

    def get_computed_left(self) -> float:
        return self._x

    def get_computed_top(self) -> float:
        return self._y

    def get_computed_width(self) -> float:
        return self._width if self._width > 0 else 80.0

    def get_computed_height(self) -> float:
        return self._height if self._height > 0 else 24.0


class LayoutNode:
    """Yoga 布局节点封装；无 yoga 时使用简单 stub。"""

    def __init__(self) -> None:
        self.children: list[LayoutNode] = []
        if HAS_YOGA and yoga is not None:
            self.node = yoga.Node.create()
            self._stub: _StubLayoutNode | None = None
        else:
            self._stub = _StubLayoutNode()
            self.node = None  # type: ignore[assignment]

    def _node(self) -> "_StubLayoutNode":
        if self._stub is not None:
            return self._stub
        return self.node  # type: ignore[return-value]

    def set_flex_direction(self, direction: FlexDirection) -> None:
        if self.node is not None and yoga is not None:
            mapping = {
                "row": yoga.FLEX_DIRECTION_ROW,
                "column": yoga.FLEX_DIRECTION_COLUMN,
                "row-reverse": yoga.FLEX_DIRECTION_ROW_REVERSE,
                "column-reverse": yoga.FLEX_DIRECTION_COLUMN_REVERSE,
            }
            self.node.set_flex_direction(mapping[direction])
        else:
            self._stub.set_flex_direction(direction)

    def set_flex_wrap(self, wrap: Literal["wrap", "nowrap"]) -> None:
        if self.node is not None and yoga is not None:
            self.node.set_flex_wrap(yoga.WRAP_WRAP if wrap == "wrap" else yoga.WRAP_NO_WRAP)
        else:
            self._stub.set_flex_wrap(wrap)

    def set_align_items(self, align: AlignItems) -> None:
        if self.node is not None and yoga is not None:
            mapping = {
                "flex-start": yoga.ALIGN_FLEX_START,
                "flex-end": yoga.ALIGN_FLEX_END,
                "center": yoga.ALIGN_CENTER,
                "stretch": yoga.ALIGN_STRETCH,
                "baseline": yoga.ALIGN_BASELINE,
            }
            self.node.set_align_items(mapping[align])
        else:
            self._stub.set_align_items(align)

    def set_justify_content(self, justify: JustifyContent) -> None:
        if self.node is not None and yoga is not None:
            mapping = {
                "flex-start": yoga.JUSTIFY_FLEX_START,
                "flex-end": yoga.JUSTIFY_FLEX_END,
                "center": yoga.JUSTIFY_CENTER,
                "space-between": yoga.JUSTIFY_SPACE_BETWEEN,
                "space-around": yoga.JUSTIFY_SPACE_AROUND,
            }
            if justify == "space-evenly" and hasattr(yoga, "JUSTIFY_SPACE_EVENLY"):
                mapping["space-evenly"] = yoga.JUSTIFY_SPACE_EVENLY
            self.node.set_justify_content(mapping.get(justify, yoga.JUSTIFY_FLEX_START))
        else:
            self._stub.set_justify_content(justify)

    def set_gap(self, gap_or_gutter: float | str, value: float | None = None) -> None:
        """Set gap. One arg: set_gap(gap). Two args: set_gap(gutter, value), gutter 'all'|'row'|'column'."""
        n = self._node()
        if value is None:
            if hasattr(n, "set_gap"):
                n.set_gap(gap_or_gutter)
            if self.node is not None and yoga is not None and hasattr(yoga, "Gutter"):
                self.node.set_gap(yoga.Gutter.All, float(gap_or_gutter))
        else:
            if hasattr(n, "set_gap"):
                n.set_gap(gap_or_gutter, value)
            if self.node is not None and yoga is not None and hasattr(yoga, "Gutter"):
                g = getattr(yoga.Gutter, str(gap_or_gutter).upper(), yoga.Gutter.All)
                self.node.set_gap(g, float(value))

    def set_border(self, edge: str, value: float) -> None:
        """Set border width for edge (left, top, right, bottom). Aligns OpenTUI Edge + setBorder."""
        n = self._node()
        if hasattr(n, "set_border"):
            n.set_border(edge, value)
        if self.node is not None and yoga is not None and hasattr(yoga, "Edge"):
            edge_enum = getattr(yoga.Edge, edge.upper(), None)
            if edge_enum is not None:
                self.node.set_border(edge_enum, value)

    def set_flex_grow(self, grow: float) -> None:
        n = self._node()
        if hasattr(n, "set_flex_grow"):
            n.set_flex_grow(grow)

    def set_flex_shrink(self, shrink: float) -> None:
        n = self._node()
        if hasattr(n, "set_flex_shrink"):
            n.set_flex_shrink(shrink)

    def set_flex_basis(self, basis: int | Literal["auto"]) -> None:
        if self.node is not None and yoga is not None:
            if basis == "auto":
                self.node.set_flex_basis_auto()
            else:
                self.node.set_flex_basis(basis)
        else:
            self._stub.set_flex_basis(basis)

    def set_width(self, width: int | str) -> None:
        if self.node is not None and yoga is not None:
            if isinstance(width, int):
                self.node.set_width(width)
            elif width == "auto":
                self.node.set_width_auto()
            elif isinstance(width, str) and width.endswith("%"):
                self.node.set_width_percent(float(width[:-1]))
        else:
            self._stub.set_width(width)

    def set_height(self, height: int | str) -> None:
        if self.node is not None and yoga is not None:
            if isinstance(height, int):
                self.node.set_height(height)
            elif height == "auto":
                self.node.set_height_auto()
            elif isinstance(height, str) and height.endswith("%"):
                self.node.set_height_percent(float(height[:-1]))
        else:
            self._stub.set_height(height)

    def set_min_width(self, width: int) -> None:
        n = self._node()
        if hasattr(n, "set_min_width"):
            n.set_min_width(width)

    def set_min_height(self, height: int) -> None:
        n = self._node()
        if hasattr(n, "set_min_height"):
            n.set_min_height(height)

    def set_max_width(self, width: int) -> None:
        n = self._node()
        if hasattr(n, "set_max_width"):
            n.set_max_width(width)

    def set_max_height(self, height: int) -> None:
        n = self._node()
        if hasattr(n, "set_max_height"):
            n.set_max_height(height)

    def set_margin(self, edge: str, value: int | str) -> None:
        n = self._node()
        if hasattr(n, "set_margin"):
            n.set_margin(edge, value)

    def set_padding(self, edge: str, value: int | str) -> None:
        n = self._node()
        if hasattr(n, "set_padding"):
            n.set_padding(edge, value)

    def set_position_type(self, position: Literal["relative", "absolute"]) -> None:
        n = self._node()
        if hasattr(n, "set_position_type"):
            n.set_position_type(position)

    def set_position(self, edge: str, value: int | str) -> None:
        n = self._node()
        if hasattr(n, "set_position"):
            n.set_position(edge, value)

    def add_child(self, child: "LayoutNode", index: int | None = None) -> None:
        if index is None:
            index = len(self.children)
        self.children.insert(index, child)
        if self.node is not None and yoga is not None and getattr(child, "node", None) is not None:
            self.node.insert_child(child.node, index)
        elif self._stub is not None and child._stub is not None:
            self._stub.insert_child(child._stub, index)

    def remove_child(self, child: "LayoutNode") -> None:
        if child in self.children:
            self.children.remove(child)
            if self.node is not None and yoga is not None and getattr(child, "node", None) is not None:
                self.node.remove_child(child.node)
            elif self._stub is not None and child._stub is not None:
                self._stub.remove_child(child._stub)

    def calculate_layout(
        self,
        width: float = float("nan"),
        height: float = float("nan"),
        direction: Literal["ltr", "rtl"] = "ltr",
    ) -> None:
        node = self._node()
        if self.node is not None and yoga is not None:
            d = yoga.DIRECTION_RTL if direction == "rtl" else yoga.DIRECTION_LTR
            self.node.calculate_layout(width, height, d)
        else:
            node.calculate_layout(width, height, direction)

    def get_computed_layout(self) -> dict:
        node = self._node()
        return {
            "x": node.get_computed_left(),
            "y": node.get_computed_top(),
            "width": node.get_computed_width(),
            "height": node.get_computed_height(),
        }
