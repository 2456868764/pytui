# pytui.components.scrollbox

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable

if TYPE_CHECKING:
    from pytui.utils.scroll_acceleration import ScrollAcceleration


class Scrollbox(Renderable):
    """视口滚动容器：只渲染子节点在视口内的部分。支持可选滚动加速度。获得焦点时 ↑/↓ 或 j/k 滚动。"""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.scroll_x = 0
        self.scroll_y = 0
        accel = options.get("scroll_acceleration")
        self._scroll_accel: ScrollAcceleration | None = (
            accel if hasattr(accel, "tick") and hasattr(accel, "reset") else None
        )

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if not self.focused:
            return
        name = (key.get("name") or key.get("char") or "").lower()
        if name == "up":
            self.scroll_up()
        elif name == "down":
            self.scroll_down()
        elif name == "j":
            self.scroll_down()
        elif name == "k":
            self.scroll_up()

    def set_scroll(self, x: int = 0, y: int = 0) -> None:
        self.scroll_x = max(0, x)
        self.scroll_y = max(0, y)
        self.request_render()

    def scroll_down(self) -> None:
        if self._scroll_accel is not None:
            mult = self._scroll_accel.tick()
            self.scroll_y += max(1, int(mult))
        else:
            self.scroll_y += 1
        self.request_render()

    def scroll_up(self) -> None:
        if self._scroll_accel is not None:
            mult = self._scroll_accel.tick()
            self.scroll_y = max(0, self.scroll_y - max(1, int(mult)))
        else:
            self.scroll_y = max(0, self.scroll_y - 1)
        self.request_render()

    def render(self, buffer: OptimizedBuffer) -> None:
        if not self.visible:
            return
        self.render_self(buffer)
        content_top = self.y
        view_start = self.scroll_y
        view_end = view_start + self.height
        for child in sorted(self.children, key=lambda c: c.z_index):
            off = child.y - content_top
            if off + child.height <= view_start or off >= view_end:
                continue
            saved_y = child.y
            child.y = content_top + off - view_start
            child.render(buffer)
            child.y = saved_y
        self._dirty = False

    def render_self(self, buffer: OptimizedBuffer) -> None:
        pass
