# pytui.core.renderable - render tree base

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pyee import EventEmitter

from pytui.core.buffer import OptimizedBuffer
from pytui.core.layout import LayoutNode

if TYPE_CHECKING:
    from pytui.core.renderer import RenderContext


class Renderable(ABC, EventEmitter):
    """可渲染对象基类。"""

    _id_counter = 0

    def __init__(self, ctx: RenderContext, options: dict[str, Any] | None = None) -> None:
        super().__init__()
        options = options or {}
        self.ctx = ctx
        if options.get("id"):
            self.id = options["id"]
        else:
            Renderable._id_counter += 1
            self.id = f"renderable-{Renderable._id_counter}"
        self.parent: Renderable | None = None
        self.children: list[Renderable] = []
        self.layout_node = LayoutNode()
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.visible = options.get("visible", True)
        self.z_index = options.get("z_index", 0)
        self.focused = options.get("focused", False)
        self._dirty = True
        self._apply_layout_options(options)

    def _apply_layout_options(self, options: dict[str, Any]) -> None:
        if "flex_direction" in options:
            self.layout_node.set_flex_direction(options["flex_direction"])
        if "align_items" in options:
            self.layout_node.set_align_items(options["align_items"])
        if "justify_content" in options:
            self.layout_node.set_justify_content(options["justify_content"])
        if "flex_grow" in options:
            self.layout_node.set_flex_grow(options["flex_grow"])
        if "flex_shrink" in options:
            self.layout_node.set_flex_shrink(options["flex_shrink"])
        if "flex_basis" in options:
            self.layout_node.set_flex_basis(options["flex_basis"])
        if "width" in options:
            self.layout_node.set_width(options["width"])
        if "height" in options:
            self.layout_node.set_height(options["height"])
        if "min_width" in options:
            self.layout_node.set_min_width(options["min_width"])
        if "min_height" in options:
            self.layout_node.set_min_height(options["min_height"])
        if "max_width" in options:
            self.layout_node.set_max_width(options["max_width"])
        if "max_height" in options:
            self.layout_node.set_max_height(options["max_height"])
        if "margin" in options:
            self.layout_node.set_margin("all", options["margin"])
        for edge in ["margin_left", "margin_top", "margin_right", "margin_bottom"]:
            if edge in options:
                self.layout_node.set_margin(edge.split("_")[1], options[edge])
        if "padding" in options:
            self.layout_node.set_padding("all", options["padding"])
        for edge in ["padding_left", "padding_top", "padding_right", "padding_bottom"]:
            if edge in options:
                self.layout_node.set_padding(edge.split("_")[1], options[edge])
        if "position" in options:
            self.layout_node.set_position_type(options["position"])
        for edge in ["left", "top", "right", "bottom"]:
            if edge in options:
                self.layout_node.set_position(edge, options[edge])

    def add(self, child: Renderable, index: int | None = None) -> None:
        if child.parent:
            child.parent.remove(child)
        child.parent = self
        if index is None:
            self.children.append(child)
            self.layout_node.add_child(child.layout_node)
        else:
            self.children.insert(index, child)
            self.layout_node.add_child(child.layout_node, index)
        self.emit("child_added", child)
        child.emit("added", self)
        self.request_render()

    def remove(self, child: Renderable) -> None:
        if child in self.children:
            self.children.remove(child)
            self.layout_node.remove_child(child.layout_node)
            child.parent = None
            self.emit("child_removed", child)
            child.emit("removed", self)
            self.request_render()

    def remove_all(self) -> None:
        for c in list(self.children):
            self.remove(c)

    def request_render(self) -> None:
        self._dirty = True
        if self.parent:
            self.parent.request_render()
        elif hasattr(self.ctx, "renderer"):
            self.ctx.renderer.schedule_render()

    def calculate_layout(self) -> None:
        if self.parent is None:
            self.layout_node.calculate_layout(
                float(self.ctx.renderer.width),
                float(self.ctx.renderer.height),
            )
        layout = self.layout_node.get_computed_layout()
        if self.parent:
            self.x = self.parent.x + int(layout["x"])
            self.y = self.parent.y + int(layout["y"])
        else:
            self.x = int(layout["x"])
            self.y = int(layout["y"])
        self.width = int(layout["width"])
        self.height = int(layout["height"])
        for child in self.children:
            child.calculate_layout()

    def render(self, buffer: OptimizedBuffer) -> None:
        if not self.visible:
            return
        self.render_self(buffer)
        for child in sorted(self.children, key=lambda c: c.z_index):
            child.render(buffer)
        self._dirty = False

    @abstractmethod
    def render_self(self, buffer: OptimizedBuffer) -> None:
        pass

    def focus(self) -> None:
        if not self.focused:
            self.focused = True
            self.emit("focused")
            self.request_render()

    def blur(self) -> None:
        if self.focused:
            self.focused = False
            self.emit("blurred")
            self.request_render()

    def is_root(self) -> bool:
        return self.parent is None

    def get_root(self) -> Renderable:
        node: Renderable = self
        while node.parent:
            node = node.parent
        return node

    def find_by_id(self, id: str) -> Renderable | None:
        if self.id == id:
            return self
        for child in self.children:
            r = child.find_by_id(id)
            if r:
                return r
        return None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id="{self.id}" x={self.x} y={self.y} w={self.width} h={self.height}>'
