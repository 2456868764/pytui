# pytui.components.scrollbox - aligns with OpenTUI ScrollBoxRenderable (ScrollBox.ts):
# scroll_top, scroll_left, scroll_height, scroll_width, sticky_scroll, sticky_start,
# scroll_by(delta, unit), scroll_to(position), viewport_culling, scroll_acceleration.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable

if TYPE_CHECKING:
    from pytui.lib.scroll_acceleration import ScrollAcceleration

ScrollUnit = Literal["absolute", "viewport", "content", "step"]
StickyStart = Literal["top", "bottom", "left", "right"]


class Scrollbox(Renderable):
    """Scroll container. Aligns with OpenTUI ScrollBoxRenderable: scroll_top, scroll_left,
    scroll_height, scroll_width, sticky_scroll, sticky_start, scroll_by(delta, unit),
    scroll_to(position), viewport_culling, scroll_acceleration.
    """

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._scroll_x = 0
        self._scroll_y = 0
        accel = options.get("scroll_acceleration", options.get("scrollAcceleration"))
        self._scroll_accel: ScrollAcceleration | None = (
            accel if accel is not None and hasattr(accel, "tick") and hasattr(accel, "reset") else None
        )
        self._sticky_scroll = options.get("sticky_scroll", options.get("stickyScroll", False))
        self._sticky_start: StickyStart | None = options.get("sticky_start", options.get("stickyStart"))
        self._viewport_culling = options.get("viewport_culling", options.get("viewportCulling", True))
        self._has_manual_scroll = False
        self._is_applying_sticky = False

    def _content_height(self) -> int:
        if not self.children:
            return 0
        return max((c.y - self.y) + c.height for c in self.children)

    def _content_width(self) -> int:
        if not self.children:
            return 0
        return max((c.x - self.x) + c.width for c in self.children)

    @property
    def scroll_top(self) -> int:
        return self._scroll_y

    @scroll_top.setter
    def scroll_top(self, value: int) -> None:
        max_top = max(0, self._content_height() - self.height)
        value = max(0, min(max_top, int(value)))
        if value != self._scroll_y:
            self._scroll_y = value
            if not self._is_applying_sticky and max_top > 1:
                self._has_manual_scroll = True
            self.request_render()

    @property
    def scroll_left(self) -> int:
        return self._scroll_x

    @scroll_left.setter
    def scroll_left(self, value: int) -> None:
        max_left = max(0, self._content_width() - self.width)
        value = max(0, min(max_left, int(value)))
        if value != self._scroll_x:
            self._scroll_x = value
            if not self._is_applying_sticky and max_left > 1:
                self._has_manual_scroll = True
            self.request_render()

    @property
    def scroll_height(self) -> int:
        return self._content_height()

    @property
    def scroll_width(self) -> int:
        return self._content_width()

    @property
    def sticky_scroll(self) -> bool:
        return self._sticky_scroll

    @sticky_scroll.setter
    def sticky_scroll(self, value: bool) -> None:
        self._sticky_scroll = value

    @property
    def sticky_start(self) -> StickyStart | None:
        return self._sticky_start

    @sticky_start.setter
    def sticky_start(self, value: StickyStart | None) -> None:
        self._sticky_start = value

    @property
    def viewport_culling(self) -> bool:
        return self._viewport_culling

    @viewport_culling.setter
    def viewport_culling(self, value: bool) -> None:
        self._viewport_culling = value
        self.request_render()

    @property
    def scroll_acceleration(self) -> ScrollAcceleration | None:
        return self._scroll_accel

    @scroll_acceleration.setter
    def scroll_acceleration(self, value: ScrollAcceleration | None) -> None:
        self._scroll_accel = value

    @property
    def scroll_x(self) -> int:
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: int) -> None:
        self.scroll_left = value

    @property
    def scroll_y(self) -> int:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: int) -> None:
        self.scroll_top = value

    def scroll_by(
        self,
        delta: int | dict[str, int],
        unit: ScrollUnit = "absolute",
    ) -> None:
        """Align with OpenTUI scrollBy(delta, unit). delta: number for vertical only, or {x, y}."""
        if isinstance(delta, dict):
            dx = delta.get("x", 0)
            dy = delta.get("y", 0)
        else:
            dx = 0
            dy = int(delta)
        if unit == "viewport":
            dy = dy * self.height if dy else 0
            dx = dx * self.width if dx else 0
        elif unit == "content":
            dy = dy * self._content_height() if dy else 0
            dx = dx * self._content_width() if dx else 0
        elif unit == "step":
            dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
            dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
        if dy:
            self.scroll_top = self.scroll_top + dy
        if dx:
            self.scroll_left = self.scroll_left + dx

    def scroll_to(self, position: int | dict[str, int]) -> None:
        """Align with OpenTUI scrollTo(position). position: number for vertical only, or {x, y}."""
        if isinstance(position, dict):
            if "x" in position:
                self.scroll_left = position["x"]
            if "y" in position:
                self.scroll_top = position["y"]
        else:
            self.scroll_top = int(position)

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
        if name == "up" or name == "k":
            self.scroll_up()
        elif name == "down" or name == "j":
            self.scroll_down()

    def set_scroll(self, x: int = 0, y: int = 0) -> None:
        self.scroll_left = x
        self.scroll_top = y

    def scroll_down(self) -> None:
        if self._scroll_accel is not None:
            mult = self._scroll_accel.tick()
            self.scroll_top = self.scroll_top + max(1, int(mult))
        else:
            self.scroll_top = self.scroll_top + 1

    def scroll_up(self) -> None:
        if self._scroll_accel is not None:
            mult = self._scroll_accel.tick()
            self.scroll_top = max(0, self.scroll_top - max(1, int(mult)))
        else:
            self.scroll_top = max(0, self.scroll_top - 1)

    def render(self, buffer: OptimizedBuffer) -> None:
        if not self.visible:
            return
        self.render_self(buffer)
        content_top = self.y
        content_left = self.x
        view_start_y = self._scroll_y
        view_start_x = self._scroll_x
        view_end_y = view_start_y + self.height
        view_end_x = view_start_x + self.width
        children_list = sorted(self.children, key=lambda c: c.z_index) if self._viewport_culling else sorted(
            self.children, key=lambda c: c.z_index
        )
        for child in children_list:
            off_y = child.y - content_top
            off_x = child.x - content_left
            if self._viewport_culling:
                if off_y + child.height <= view_start_y or off_y >= view_end_y:
                    continue
                if off_x + child.width <= view_start_x or off_x >= view_end_x:
                    continue
            saved_y, saved_x = child.y, child.x
            child.y = content_top + off_y - view_start_y
            child.x = content_left + off_x - view_start_x
            child.render(buffer)
            child.y, child.x = saved_y, saved_x
        self._dirty = False

    def render_self(self, buffer: OptimizedBuffer) -> None:
        pass
