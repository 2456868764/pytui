# pytui.components.slider - Aligns OpenTUI packages/core/src/renderables/Slider.ts
# SliderOptions: orientation, value, min, max, viewPortSize, backgroundColor, foregroundColor, onChange.
# Virtual thumb (getVirtualThumbSize/getVirtualThumbStart), getThumbRect; render with half-blocks (█▌▐ horizontal, █▀▄ vertical).
# Mouse: onMouseDown/onMouseDrag/onMouseUp via on_mouse(event) with type down/drag/up.

from __future__ import annotations

import math
from typing import Any, Literal

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple

# Align OpenTUI defaultThumbBackgroundColor / defaultTrackBackgroundColor
_DEFAULT_TRACK_BG = parse_color_to_tuple("#252527")
_DEFAULT_THUMB_FG = parse_color_to_tuple("#9a9ea3")


class Slider(Renderable):
    """Slider: value, min, max, viewPortSize, orientation, backgroundColor, foregroundColor, onChange.
    Virtual thumb size/start; render with half-blocks; mouse down/drag/up. Aligns OpenTUI SliderRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        opts = dict(options) if options else {}
        opts.setdefault("flex_shrink", 0)
        super().__init__(ctx, opts)
        self.orientation: Literal["vertical", "horizontal"] = opts.get(
            "orientation", opts.get("orientation", "horizontal")
        )
        self._min = float(opts.get("min", 0))
        self._max = float(opts.get("max", 100))
        self._view_port_size = float(
            opts.get("view_port_size", opts.get("viewPortSize", max(1, (self._max - self._min) * 0.1)))
        )
        self._value = max(
            self._min,
            min(self._max, float(opts.get("value", self._min))),
        )
        self._backgroundColor = parse_color_to_tuple(
            opts.get("backgroundColor", "#252527")
        )
        self._foregroundColor = parse_color_to_tuple(
            opts.get("foregroundColor", "#9a9ea3")
        )
        self._on_change = opts.get("on_change", opts.get("onChange"))
        self._is_dragging = False
        self._drag_offset_virtual = 0.0

    def remove_mouse_listener(self) -> None:
        """No-op; mouse is dispatched by renderer hit_test. Kept for demo destroy compatibility."""
        pass

    # --- Options alignment: backgroundColor, foregroundColor (OpenTUI names) ---
    @property
    def backgroundColor(self) -> tuple[int, int, int, int]:
        return self._backgroundColor

    @backgroundColor.setter
    def backgroundColor(self, value: Any) -> None:
        self._backgroundColor = parse_color_to_tuple(value)
        self.request_render()

    @property
    def foregroundColor(self) -> tuple[int, int, int, int]:
        return self._foregroundColor

    @foregroundColor.setter
    def foregroundColor(self, value: Any) -> None:
        self._foregroundColor = parse_color_to_tuple(value)
        self.request_render()

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        v = max(self._min, min(self._max, v))
        if v != self._value:
            self._value = v
            if self._on_change:
                self._on_change(v)
            self.emit("change", {"value": v})
            self.request_render()

    @property
    def min(self) -> float:
        return self._min

    @min.setter
    def min(self, v: float) -> None:
        if v != self._min:
            self._min = v
            if self._value < v:
                self.value = v
            self.request_render()

    @property
    def max(self) -> float:
        return self._max

    @max.setter
    def max(self, v: float) -> None:
        if v != self._max:
            self._max = v
            if self._value > v:
                self.value = v
            self.request_render()

    @property
    def view_port_size(self) -> float:
        return self._view_port_size

    @view_port_size.setter
    def view_port_size(self, v: float) -> None:
        v = max(0.01, min(v, self._max - self._min))
        if v != self._view_port_size:
            self._view_port_size = v
            self.request_render()

    @property
    def viewPortSize(self) -> float:
        return self._view_port_size

    @viewPortSize.setter
    def viewPortSize(self, v: float) -> None:
        self.view_port_size = v

    # --- Virtual thumb (align OpenTUI getVirtualThumbSize / getVirtualThumbStart) ---
    def get_virtual_thumb_size(self) -> int:
        """Align OpenTUI getVirtualThumbSize()."""
        virtual_track = (self.height if self.orientation == "vertical" else self.width) * 2
        range_val = self._max - self._min
        if range_val <= 0:
            return virtual_track
        viewport = max(1, self._view_port_size)
        content = range_val + viewport
        if content <= viewport:
            return virtual_track
        ratio = viewport / content
        size = math.floor(virtual_track * ratio)
        return max(1, min(size, virtual_track))

    def get_virtual_thumb_start(self) -> int:
        """Align OpenTUI getVirtualThumbStart()."""
        virtual_track = (self.height if self.orientation == "vertical" else self.width) * 2
        range_val = self._max - self._min
        if range_val <= 0:
            return 0
        value_ratio = (self._value - self._min) / range_val
        thumb_size = self.get_virtual_thumb_size()
        return round(value_ratio * (virtual_track - thumb_size))

    def get_thumb_rect(self) -> dict[str, int]:
        """Real rect of thumb (x, y, width, height) for hit test. Align OpenTUI getThumbRect()."""
        virtual_size = self.get_virtual_thumb_size()
        virtual_start = self.get_virtual_thumb_start()
        real_start = virtual_start // 2
        real_size = max(1, math.ceil((virtual_start + virtual_size) / 2.0) - real_start)
        if self.orientation == "vertical":
            return {"x": self.x, "y": self.y + real_start, "width": self.width, "height": real_size}
        return {"x": self.x + real_start, "y": self.y, "width": real_size, "height": self.height}

    def _calculate_drag_offset_virtual(self, event: dict) -> float:
        track_start = self.y if self.orientation == "vertical" else self.x
        mouse_pos = (event.get("y", 0) if self.orientation == "vertical" else event.get("x", 0)) - track_start
        track_size = self.height if self.orientation == "vertical" else self.width
        virtual_mouse = max(0, min(track_size * 2, mouse_pos * 2))
        thumb_start = self.get_virtual_thumb_start()
        thumb_size = self.get_virtual_thumb_size()
        return max(0, min(thumb_size, virtual_mouse - thumb_start))

    def _update_value_from_mouse_direct(self, event: dict) -> None:
        track_start = self.y if self.orientation == "vertical" else self.x
        track_size = self.height if self.orientation == "vertical" else self.width
        mouse_pos = (event.get("y", 0) if self.orientation == "vertical" else event.get("x", 0)) - track_start
        clamped = max(0, min(track_size, mouse_pos))
        ratio = clamped / track_size if track_size else 0
        self.value = self._min + ratio * (self._max - self._min)

    def _update_value_from_mouse_with_offset(self, event: dict, offset_virtual: float) -> None:
        track_start = self.y if self.orientation == "vertical" else self.x
        track_size = self.height if self.orientation == "vertical" else self.width
        mouse_pos = (event.get("y", 0) if self.orientation == "vertical" else event.get("x", 0)) - track_start
        clamped = max(0, min(track_size, mouse_pos))
        virtual_mouse = clamped * 2
        thumb_size = self.get_virtual_thumb_size()
        virtual_track = track_size * 2
        max_thumb_start = max(0, virtual_track - thumb_size)
        desired = virtual_mouse - offset_virtual
        desired = max(0, min(max_thumb_start, desired))
        ratio = desired / max_thumb_start if max_thumb_start else 0
        self.value = self._min + ratio * (self._max - self._min)

    def on_mouse(self, event: dict) -> None:
        """Handle mouse down/drag/up; only called when this slider is hit or captured. Aligns OpenTUI onMouseDown/onMouseDrag/onMouseUp."""
        ev_type = event.get("type") or ""
        ex = event.get("x", 0)
        ey = event.get("y", 0)
        if ev_type == "down":
            thumb = self.get_thumb_rect()
            in_thumb = (
                thumb["x"] <= ex < thumb["x"] + thumb["width"]
                and thumb["y"] <= ey < thumb["y"] + thumb["height"]
            )
            self._drag_offset_virtual = self._calculate_drag_offset_virtual(event)
            if in_thumb:
                self._is_dragging = True
            else:
                self._update_value_from_mouse_direct(event)
                self._is_dragging = True
        elif ev_type in ("drag", "move") and self._is_dragging:
            self._update_value_from_mouse_with_offset(event, self._drag_offset_virtual)
        elif ev_type == "up":
            if self._is_dragging:
                self._update_value_from_mouse_with_offset(event, self._drag_offset_virtual)
            self._is_dragging = False

    def blur(self) -> None:
        self._is_dragging = False
        super().blur()

    # --- Render (align OpenTUI renderHorizontal / renderVertical: virtual thumb, half-blocks) ---
    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.orientation == "horizontal":
            self._render_horizontal(buffer)
        else:
            self._render_vertical(buffer)

    def _render_horizontal(self, buffer: OptimizedBuffer) -> None:
        """Align OpenTUI renderHorizontal(): fillRect track, then thumb half-blocks █▌▐."""
        buffer.fill_rect(
            self.x, self.y, self.width, self.height,
            Cell(char=" ", fg=self._backgroundColor, bg=self._backgroundColor),
        )
        virtual_start = self.get_virtual_thumb_start()
        virtual_end = virtual_start + self.get_virtual_thumb_size()
        real_start_cell = virtual_start // 2
        real_end_cell = math.ceil(virtual_end / 2.0) - 1
        start_x = max(0, real_start_cell)
        end_x = min(self.width - 1, real_end_cell)
        thumb_fg, thumb_bg = self._foregroundColor, self._backgroundColor
        for real_x in range(start_x, end_x + 1):
            cell_start = real_x * 2
            cell_end = cell_start + 2
            thumb_start_in_cell = max(virtual_start, cell_start)
            thumb_end_in_cell = min(virtual_end, cell_end)
            coverage = thumb_end_in_cell - thumb_start_in_cell
            if coverage >= 2:
                ch = "█"
            else:
                ch = "▌" if thumb_start_in_cell == cell_start else "▐"
            cell = Cell(char=ch, fg=thumb_fg, bg=thumb_bg)
            for dy in range(self.height):
                buffer.set_cell_with_alpha(self.x + real_x, self.y + dy, cell, 1.0)

    def _render_vertical(self, buffer: OptimizedBuffer) -> None:
        """Align OpenTUI renderVertical(): fillRect track, then thumb half-blocks █▀▄."""
        buffer.fill_rect(
            self.x, self.y, self.width, self.height,
            Cell(char=" ", fg=self._backgroundColor, bg=self._backgroundColor),
        )
        virtual_start = self.get_virtual_thumb_start()
        virtual_end = virtual_start + self.get_virtual_thumb_size()
        real_start_cell = virtual_start // 2
        real_end_cell = math.ceil(virtual_end / 2.0) - 1
        start_y = max(0, real_start_cell)
        end_y = min(self.height - 1, real_end_cell)
        thumb_fg, thumb_bg = self._foregroundColor, self._backgroundColor
        for real_y in range(start_y, end_y + 1):
            cell_start = real_y * 2
            cell_end = cell_start + 2
            thumb_start_in_cell = max(virtual_start, cell_start)
            thumb_end_in_cell = min(virtual_end, cell_end)
            coverage = thumb_end_in_cell - thumb_start_in_cell
            if coverage >= 2:
                ch = "█"
            elif coverage > 0:
                ch = "▀" if (thumb_start_in_cell - cell_start) == 0 else "▄"
            else:
                ch = " "
            cell = Cell(char=ch, fg=thumb_fg, bg=thumb_bg)
            for dx in range(self.width):
                buffer.set_cell_with_alpha(self.x + dx, self.y + real_y, cell, 1.0)


# API parity with OpenTUI SliderRenderable
SliderRenderable = Slider
