# pytui.core.layout - Yoga layout or stub

from typing import Literal

FlexDirection = Literal["row", "column", "row-reverse", "column-reverse"]
AlignItems = Literal["flex-start", "flex-end", "center", "stretch", "baseline"]
JustifyContent = Literal["flex-start", "flex-end", "center", "space-between", "space-around"]

try:
    import yoga  # type: ignore[import-untyped]

    HAS_YOGA = True
except ImportError:
    HAS_YOGA = False
    yoga = None  # type: ignore[assignment]


class _StubLayoutNode:
    """无 yoga 时的简单布局：仅存储宽高，子节点按顺序平分，支持 padding。"""

    def __init__(self) -> None:
        self.children: list[LayoutNode] = []
        self._width: float = 0.0
        self._height: float = 0.0
        self._x = 0.0
        self._y = 0.0
        self._padding_left = 0.0
        self._padding_top = 0.0
        self._padding_right = 0.0
        self._padding_bottom = 0.0

    def set_flex_direction(self, direction: FlexDirection) -> None:
        pass

    def set_flex_wrap(self, wrap: Literal["wrap", "nowrap"]) -> None:
        pass

    def set_align_items(self, align: AlignItems) -> None:
        pass

    def set_justify_content(self, justify: JustifyContent) -> None:
        pass

    def set_flex_grow(self, grow: float) -> None:
        pass

    def set_flex_shrink(self, shrink: float) -> None:
        pass

    def set_flex_basis(self, basis: int | Literal["auto"]) -> None:
        pass

    def set_width(self, width: int | str) -> None:
        if isinstance(width, int):
            self._width = float(width)
        elif width == "auto":
            self._width = 0.0
        elif isinstance(width, str) and width.endswith("%"):
            self._width = float(width[:-1])

    def set_height(self, height: int | str) -> None:
        if isinstance(height, int):
            self._height = float(height)
        elif height == "auto":
            self._height = 0.0
        elif isinstance(height, str) and height.endswith("%"):
            self._height = float(height[:-1])

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

    def set_position_type(self, position: Literal["relative", "absolute"]) -> None:
        pass

    def set_position(self, edge: str, value: int | str) -> None:
        pass

    def insert_child(self, child: "_StubLayoutNode", index: int) -> None:
        self.children.insert(index, child)

    def remove_child(self, child: "_StubLayoutNode") -> None:
        if child in self.children:
            self.children.remove(child)

    def calculate_layout(
        self,
        width: float = float("nan"),
        height: float = float("nan"),
        direction: Literal["ltr", "rtl"] = "ltr",
    ) -> None:
        if not (width != width):  # not nan
            self._width = width if self._width == 0 else self._width
        if not (height != height):
            self._height = height if self._height == 0 else self._height
        inner_w = max(0.0, self._width - self._padding_left - self._padding_right)
        inner_h = max(0.0, self._height - self._padding_top - self._padding_bottom)
        for c in self.children:
            if hasattr(c, "calculate_layout"):
                c.calculate_layout(inner_w, inner_h, direction)
        # 简单垂直堆叠：子节点按顺序从上到下排列，在 padding 区域内
        y_off = 0.0
        for c in self.children:
            c._x = self._padding_left
            c._y = self._padding_top + y_off
            y_off += c.get_computed_height()

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
            self.node.set_justify_content(mapping[justify])
        else:
            self._stub.set_justify_content(justify)

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
