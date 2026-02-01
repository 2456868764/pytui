# pytui.components.ascii_font - ASCIIFont renderable; aligns with OpenTUI ASCIIFontRenderable (ASCIIFont.ts).

from __future__ import annotations

from typing import Any

from pytui.components.frame_buffer import FrameBuffer
from pytui.lib.ascii_font import (
    get_character_positions,
    get_font,
    measure_text,
    register_font,
    render_font_to_frame_buffer,
)
from pytui.lib.rgba import parse_color_to_tuple
from pytui.lib.selection import (
    ASCIIFontSelectionHelper,
    LocalSelectionBounds,
    convert_global_to_local_selection,
)

# Re-export for lib/selection and consumers
def coordinate_to_character_index(x: int, text: str, font: str | dict[str, Any] = "tiny") -> int:
    """Map local x to character index. Aligns with OpenTUI coordinateToCharacterIndex()."""
    from pytui.lib.ascii_font import coordinate_to_character_index as _impl
    return _impl(x, text, font)


# Align with OpenTUI: TINY_FONT = fonts.tiny (first font name)
TINY_FONT = "tiny"

# Preload grid/huge/pallet for tests that expect ASCIIFont._fonts and GRID_FONT etc.
_fonts: dict[str, Any] = {}
for _name in ("grid", "huge", "pallet"):
    try:
        _font_def = get_font(_name)
        if _font_def.get("name") or _font_def.get("chars"):
            _fonts[_name] = _font_def
    except Exception:
        pass
GRID_FONT = _fonts.get("grid", "grid")
HUGE_FONT = _fonts.get("huge", "huge")
PALLET_FONT = _fonts.get("pallet", "pallet")


class ASCIIFont(FrameBuffer):
    """ASCII font renderable with selection. Aligns with OpenTUI ASCIIFontRenderable."""

    _default_options = {
        "text": "",
        "font": "tiny",
        "color": "#FFFFFF",
        "backgroundColor": "transparent",
        "selectionBg": None,
        "selectionFg": None,
        "selectable": True,
    }

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        defs = self._default_options
        font = options.get("font", defs["font"])
        text = options.get("text", defs["text"])
        measurements = measure_text(text=text, font=font)
        w = getattr(measurements, "width", measurements[0] if hasattr(measurements, "__getitem__") else 1) or 1
        h = getattr(measurements, "height", measurements[1] if hasattr(measurements, "__getitem__") else 1) or 1
        opts = {
            **options,
            "width": w,
            "height": h,
            "flex_shrink": 0,
            "respect_alpha": True,
        }
        super().__init__(ctx, opts)
        self.width = w
        self.height = h
        self._text = text
        self._font = font
        self._color = options.get("color", defs["color"])
        self._backgroundColor = options.get("backgroundColor", options.get("background_color", defs["backgroundColor"]))
        self._selection_bg = (
            parse_color_to_tuple(options["selectionBg"]) if options.get("selectionBg") else None
        )
        self._selection_fg = (
            parse_color_to_tuple(options["selectionFg"]) if options.get("selectionFg") else None
        )
        self.selectable = options.get("selectable", defs["selectable"])
        self._last_local_selection: LocalSelectionBounds | None = None
        self.selection_helper = ASCIIFontSelectionHelper(
            lambda: self._text,
            lambda: self._font,
        )
        self._render_font_to_buffer()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._update_dimensions()
        if self._last_local_selection:
            self.selection_helper.on_local_selection_changed(
                self._last_local_selection, self.width, self.height
            )
        self._render_font_to_buffer()
        self.request_render()

    @property
    def font(self) -> str:
        return self._font

    @font.setter
    def font(self, value: str) -> None:
        self._font = value
        self._update_dimensions()
        if self._last_local_selection:
            self.selection_helper.on_local_selection_changed(
                self._last_local_selection, self.width, self.height
            )
        self._render_font_to_buffer()
        self.request_render()

    @property
    def color(self) -> Any:
        return self._color

    @color.setter
    def color(self, value: Any) -> None:
        self._color = value
        self._render_font_to_buffer()
        self.request_render()

    @property
    def backgroundColor(self) -> Any:
        return self._backgroundColor

    @backgroundColor.setter
    def backgroundColor(self, value: Any) -> None:
        self._backgroundColor = value
        self._render_font_to_buffer()
        self.request_render()

    @property
    def background_color(self) -> Any:
        """Snake_case alias for backgroundColor."""
        return self._backgroundColor

    @background_color.setter
    def background_color(self, value: Any) -> None:
        self._backgroundColor = value
        self._render_font_to_buffer()
        self.request_render()

    @property
    def selection_bg(self) -> Any:
        return self._selection_bg

    @selection_bg.setter
    def selection_bg(self, value: Any) -> None:
        self._selection_bg = parse_color_to_tuple(value) if value is not None else None
        self._render_font_to_buffer()
        self.request_render()

    def _get_font(self) -> str:
        """Return current font (for tests / OpenTUI alignment)."""
        return self._font

    @classmethod
    def register_font(cls, name: str, font_def: dict[str, Any]) -> None:
        """Register a custom font (delegates to lib.ascii_font.register_font)."""
        register_font(name, font_def)

    def _update_dimensions(self) -> None:
        m = measure_text(text=self._text, font=self._font)
        self.width = getattr(m, "width", m[0] if hasattr(m, "__getitem__") else 1)
        self.height = getattr(m, "height", m[1] if hasattr(m, "__getitem__") else 1)
        self.layout_node.set_width(self.width)
        self.layout_node.set_height(self.height)
        self.on_resize(self.width, self.height)

    def should_start_selection(self, x: int, y: int) -> bool:
        local_x = x - self.x
        local_y = y - self.y
        return self.selection_helper.should_start_selection(
            local_x, local_y, self.width, self.height
        )

    def on_selection_changed(self, selection: Any | None) -> bool:
        if isinstance(selection, dict):
            local_selection = LocalSelectionBounds(
                anchor_x=selection.get("anchorX", selection.get("anchor_x", 0)),
                anchor_y=selection.get("anchorY", selection.get("anchor_y", 0)),
                focus_x=selection.get("focusX", selection.get("focus_x", 0)),
                focus_y=selection.get("focusY", selection.get("focus_y", 0)),
                is_active=selection.get("isActive", selection.get("is_active", True)),
            )
        else:
            local_selection = convert_global_to_local_selection(selection, self.x, self.y)
        self._last_local_selection = local_selection
        changed = self.selection_helper.on_local_selection_changed(
            local_selection, self.width, self.height
        )
        if changed:
            self._render_font_to_buffer()
            self.request_render()
        return changed

    def get_selected_text(self) -> str:
        sel = self.selection_helper.get_selection()
        if not sel:
            return ""
        return self._text[sel[0] : sel[1]]

    def has_selection(self) -> bool:
        return self.selection_helper.has_selection()

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self._render_font_to_buffer()

    def _render_font_to_buffer(self) -> None:
        if getattr(self, "is_destroyed", False):
            return
        self._ensure_buffer()
        buf = self.get_buffer()
        if buf is None:
            return
        from pytui.core.buffer import Cell
        bg_tuple = parse_color_to_tuple(self._backgroundColor)
        buf.clear()
        for y in range(buf.height):
            for x in range(buf.width):
                buf.set_cell(x, y, Cell(bg=bg_tuple))
        render_font_to_frame_buffer(
            buf,
            self._text,
            x=0,
            y=0,
            color=self._color,
            backgroundColor=self._backgroundColor,
            font=self._font,
        )
        sel = self.selection_helper.get_selection()
        if sel and (self._selection_bg or self._selection_fg):
            self._render_selection_highlight(sel)

    def _render_selection_highlight(self, selection: tuple[int, int]) -> None:
        if not self._selection_bg and not self._selection_fg:
            return
        start, end = selection
        selected_text = self._text[start:end]
        if not selected_text:
            return
        positions = get_character_positions(self._text, self._font)
        start_x = positions[start] if start < len(positions) else 0
        end_x = (
            positions[end]
            if end < len(positions)
            else measure_text(text=self._text, font=self._font).get("width", 0)
        )
        buf = self.get_buffer()
        if buf is None:
            return
        from pytui.core.buffer import Cell
        if self._selection_bg:
            buf.fill_rect(
                start_x, 0, end_x - start_x, self.height,
                Cell(bg=self._selection_bg),
            )
        if self._selection_fg or self._selection_bg:
            fg = self._selection_fg if self._selection_fg else parse_color_to_tuple(self._color)
            bg = self._selection_bg if self._selection_bg else parse_color_to_tuple(self._backgroundColor)
            render_font_to_frame_buffer(
                buf,
                selected_text,
                x=start_x,
                y=0,
                color=fg,
                backgroundColor=bg,
                font=self._font,
            )


# Class-level font registry for tests (grid/huge/pallet)
ASCIIFont._fonts = _fonts  # type: ignore[attr-defined]
