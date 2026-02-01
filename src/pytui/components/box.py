# pytui.components.box - Box renderable; aligns with OpenTUI BoxRenderable (Box.ts).

from __future__ import annotations

from typing import Any, Literal

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib.border import (
    BorderCharacters,
    border_chars_to_array,
    get_border_sides,
)
from pytui.lib.rgba import parse_color_to_tuple
from pytui.lib.renderable_validations import is_valid_percentage

BorderStyle = Literal["single", "double", "rounded", "heavy"]
BorderSides = Literal["top", "right", "bottom", "left"]
TitleAlignment = Literal["left", "center", "right"]


def _is_gap_type(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (int, float)) and not (isinstance(value, float) and value != value):
        return True
    return is_valid_percentage(value)


class Box(Renderable):
    """Box renderable with border, title, fill. Aligns with OpenTUI BoxRenderable."""

    _default_options = {
        "backgroundColor": "transparent",
        "borderStyle": "single",
        "border": False,
        "borderColor": "#FFFFFF",
        "shouldFill": True,
        "titleAlignment": "left",
        "focusedBorderColor": "#00AAFF",
    }

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        defs = self._default_options
        self._backgroundColor = parse_color_to_tuple(
            options.get("backgroundColor", options.get("background_color", defs["backgroundColor"])))
        border_opt = options.get("border", defs["border"])
        if border_opt is None and (
            options.get("borderStyle") or options.get("border_style")
            or options.get("borderColor") or options.get("border_color")
            or options.get("focusedBorderColor") or options.get("focused_border_color")
            or options.get("customBorderChars") or options.get("custom_border_chars")
        ):
            border_opt = True
        self._border: bool | list[str] = border_opt if border_opt is not None else defs["border"]
        self._border_style: BorderStyle = (
            options.get("borderStyle", options.get("border_style", defs["borderStyle"])) or defs["borderStyle"]
        )
        self._border_color = parse_color_to_tuple(
            options.get("borderColor", options.get("border_color", defs["borderColor"])))
        self._focused_border_color = parse_color_to_tuple(
            options.get("focusedBorderColor", options.get("focused_border_color", defs["focusedBorderColor"])))
        custom_chars = options.get("customBorderChars", options.get("custom_border_chars"))
        self._custom_border_chars_obj: BorderCharacters | None = custom_chars
        self._custom_border_chars: list[int] | None = (
            border_chars_to_array(custom_chars) if custom_chars else None
        )
        self.border_sides = get_border_sides(self._border)
        self.should_fill = options.get("shouldFill", options.get("should_fill", defs["shouldFill"]))
        self._title = options.get("title")
        self._title_alignment: TitleAlignment = (
            options.get("titleAlignment", options.get("title_alignment", defs["titleAlignment"])) or defs["titleAlignment"]
        )
        self._apply_yoga_borders()
        if options.get("gap") is not None or options.get("rowGap") is not None or options.get("columnGap") is not None:
            self._apply_yoga_gap(options)

    def _initialize_border(self) -> None:
        if self._border is False:
            self._border = True
            self.border_sides = get_border_sides(self._border)
            self._apply_yoga_borders()

    @property
    def custom_border_chars(self) -> BorderCharacters | None:
        return self._custom_border_chars_obj

    @custom_border_chars.setter
    def custom_border_chars(self, value: BorderCharacters | None) -> None:
        self._custom_border_chars_obj = value
        self._custom_border_chars = border_chars_to_array(value) if value else None
        self.request_render()

    @property
    def backgroundColor(self) -> tuple[int, int, int, int]:
        return self._backgroundColor

    @property
    def background_color(self) -> tuple[int, int, int, int]:
        """Snake_case alias for backgroundColor."""
        return self._backgroundColor

    @background_color.setter
    def background_color(self, value: Any) -> None:
        self.backgroundColor = value

    @backgroundColor.setter
    def backgroundColor(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value or self._default_options["backgroundColor"])
        if self._backgroundColor != new_color:
            self._backgroundColor = new_color
            self.request_render()

    @property
    def border(self) -> bool | list[str]:
        return self._border

    @border.setter
    def border(self, value: bool | list[str]) -> None:
        if self._border != value:
            self._border = value
            self.border_sides = get_border_sides(value)
            self._apply_yoga_borders()
            self.request_render()

    @property
    def border_style(self) -> BorderStyle:
        return self._border_style

    @border_style.setter
    def border_style(self, value: BorderStyle | None) -> None:
        val = value or self._default_options["borderStyle"]
        if self._border_style != val or not self._border:
            self._border_style = val
            self._custom_border_chars = None
            self._initialize_border()
            self.request_render()

    @property
    def border_color(self) -> tuple[int, int, int, int]:
        return self._border_color

    @border_color.setter
    def border_color(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value or self._default_options["borderColor"])
        if self._border_color != new_color:
            self._border_color = new_color
            self._initialize_border()
            self.request_render()

    @property
    def focused_border_color(self) -> tuple[int, int, int, int]:
        return self._focused_border_color

    @focused_border_color.setter
    def focused_border_color(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value or self._default_options["focusedBorderColor"])
        if self._focused_border_color != new_color:
            self._focused_border_color = new_color
            self._initialize_border()
            if self.focused:
                self.request_render()

    @property
    def title(self) -> str | None:
        return self._title

    @title.setter
    def title(self, value: str | None) -> None:
        if self._title != value:
            self._title = value
            self.request_render()

    @property
    def title_alignment(self) -> TitleAlignment:
        return self._title_alignment

    @title_alignment.setter
    def title_alignment(self, value: TitleAlignment) -> None:
        if self._title_alignment != value:
            self._title_alignment = value
            self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        current_border_color = (
            self._focused_border_color if self.focused else self._border_color
        )
        buffer.draw_box(
            self.x,
            self.y,
            self.width,
            self.height,
            border_style=self._border_style,
            custom_border_chars=self._custom_border_chars,
            border=self._border,
            border_color=current_border_color,
            backgroundColor=self._backgroundColor,
            should_fill=self.should_fill,
            title=self._title,
            title_alignment=self._title_alignment,
        )

    def get_scissor_rect(self) -> dict[str, int]:
        """Return rect inset by border. Aligns with OpenTUI getScissorRect()."""
        base_x, base_y = self.x, self.y
        base_w, base_h = self.width, self.height
        if not (
            self.border_sides.top or self.border_sides.right
            or self.border_sides.bottom or self.border_sides.left
        ):
            return {"x": base_x, "y": base_y, "width": base_w, "height": base_h}
        left_inset = 1 if self.border_sides.left else 0
        right_inset = 1 if self.border_sides.right else 0
        top_inset = 1 if self.border_sides.top else 0
        bottom_inset = 1 if self.border_sides.bottom else 0
        return {
            "x": base_x + left_inset,
            "y": base_y + top_inset,
            "width": max(0, base_w - left_inset - right_inset),
            "height": max(0, base_h - top_inset - bottom_inset),
        }

    def _apply_yoga_borders(self) -> None:
        node = self.layout_node
        node.set_border("left", 1 if self.border_sides.left else 0)
        node.set_border("right", 1 if self.border_sides.right else 0)
        node.set_border("top", 1 if self.border_sides.top else 0)
        node.set_border("bottom", 1 if self.border_sides.bottom else 0)
        self.request_render()

    def _apply_yoga_gap(self, options: dict[str, Any]) -> None:
        node = self.layout_node
        gap = options.get("gap")
        if _is_gap_type(gap) and gap is not None:
            node.set_gap("all", gap)
        row_gap = options.get("rowGap", options.get("row_gap"))
        if _is_gap_type(row_gap) and row_gap is not None:
            node.set_gap("row", row_gap)
        col_gap = options.get("columnGap", options.get("column_gap"))
        if _is_gap_type(col_gap) and col_gap is not None:
            node.set_gap("column", col_gap)

    def set_gap(self, gap: float | str | None) -> None:
        if _is_gap_type(gap):
            self.layout_node.set_gap("all", gap)
            self.request_render()

    def set_row_gap(self, row_gap: float | str | None) -> None:
        if _is_gap_type(row_gap):
            self.layout_node.set_gap("row", row_gap)
            self.request_render()

    def set_column_gap(self, column_gap: float | str | None) -> None:
        if _is_gap_type(column_gap):
            self.layout_node.set_gap("column", column_gap)
            self.request_render()

    @property
    def gap(self) -> float:
        """Current gap (from layout stub; aligns with OpenTUI gap getter)."""
        n = self.layout_node._node()
        return getattr(n, "_gap", 0.0)

    @gap.setter
    def gap(self, value: float | str | None) -> None:
        if _is_gap_type(value):
            self.layout_node.set_gap("all", value)
            self.request_render()

    @property
    def row_gap(self) -> float:
        n = self.layout_node._node()
        return getattr(n, "_row_gap", 0.0)

    @row_gap.setter
    def row_gap(self, value: float | str | None) -> None:
        if _is_gap_type(value):
            self.layout_node.set_gap("row", value)
            self.request_render()

    @property
    def column_gap(self) -> float:
        n = self.layout_node._node()
        return getattr(n, "_column_gap", 0.0)

    @column_gap.setter
    def column_gap(self, value: float | str | None) -> None:
        if _is_gap_type(value):
            self.layout_node.set_gap("column", value)
            self.request_render()
