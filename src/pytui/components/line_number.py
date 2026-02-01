# pytui.components.line_number - aligns with OpenTUI LineNumberRenderable (LineNumberRenderable.ts):
# min_width, padding_right, line_number_offset (scroll_offset), line_colors, line_signs,
# hide_line_numbers, line_numbers, show_line_numbers, set_line_color, clear_line_color, etc.

from __future__ import annotations

from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple

# Align with OpenTUI LineSign
LineSign = dict[str, Any]  # before?, beforeColor?, after?, afterColor?

# Align with OpenTUI LineColorConfig
LineColorConfig = dict[str, Any]  # gutter?, content?


def _darken_color(color: tuple[int, int, int, int], factor: float = 0.8) -> tuple[int, int, int, int]:
    r, g, b, a = color
    return (int(r * factor), int(g * factor), int(b * factor), a)


class LineNumber(Renderable):
    """行号区。Aligns with OpenTUI LineNumberRenderable: min_width, padding_right,
    line_number_offset, line_colors, line_signs, hide_line_numbers, line_numbers, show_line_numbers.
    """

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self.line_count = max(0, int(options.get("line_count", options.get("lineCount", 1))))
        self._scroll_offset = max(0, int(options.get("scroll_offset", options.get("scrollOffset", 0))))
        self.scroll_offset = self._scroll_offset  # backward compat
        self._line_number_offset = int(options.get("line_number_offset", options.get("lineNumberOffset", 0)))
        self._min_width = max(1, int(options.get("min_width", options.get("minWidth", 3))))
        self._padding_right = max(0, int(options.get("padding_right", options.get("paddingRight", 1))))
        self.line_number_width = max(self._min_width, int(options.get("line_number_width", options.get("lineNumberWidth", 4))))
        self.fg = parse_color_to_tuple(options.get("fg", "#888888"))
        self.bg = parse_color_to_tuple(options.get("bg", "transparent"))
        self._line_colors_gutter: dict[int, tuple[int, int, int, int]] = {}
        self._line_colors_content: dict[int, tuple[int, int, int, int]] = {}
        self._line_signs: dict[int, LineSign] = {}
        self._hide_line_numbers: set[int] = set(options.get("hide_line_numbers", options.get("hideLineNumbers", [])))
        self._line_numbers: dict[int, int] = dict(options.get("line_numbers", options.get("lineNumbers", {})))
        self._show_line_numbers = options.get("show_line_numbers", options.get("showLineNumbers", True))

        line_colors = options.get("line_colors", options.get("lineColors"))
        if line_colors:
            for line, color in (line_colors.items() if isinstance(line_colors, dict) else line_colors):
                self._parse_line_color(line, color)
        line_signs = options.get("line_signs", options.get("lineSigns"))
        if line_signs:
            for line, sign in (line_signs.items() if isinstance(line_signs, dict) else line_signs):
                self._line_signs[line] = dict(sign) if isinstance(sign, dict) else {}

    def _parse_line_color(self, line: int, color: str | tuple | LineColorConfig) -> None:
        if isinstance(color, dict) and ("gutter" in color or "content" in color):
            cfg = color
            if cfg.get("gutter"):
                self._line_colors_gutter[line] = parse_color_to_tuple(cfg["gutter"]) if isinstance(cfg["gutter"], str) else tuple(cfg["gutter"])
            if cfg.get("content"):
                self._line_colors_content[line] = parse_color_to_tuple(cfg["content"]) if isinstance(cfg["content"], str) else tuple(cfg["content"])
            elif cfg.get("gutter"):
                g = self._line_colors_gutter[line]
                self._line_colors_content[line] = _darken_color(g)
        else:
            c = parse_color_to_tuple(color) if isinstance(color, str) else tuple(color)[:4]
            if len(c) == 3:
                c = (*c, 255)
            self._line_colors_gutter[line] = c
            self._line_colors_content[line] = _darken_color(c)

    @property
    def line_number_offset(self) -> int:
        return self._line_number_offset

    @line_number_offset.setter
    def line_number_offset(self, value: int) -> None:
        value = int(value)
        if value != self._line_number_offset:
            self._line_number_offset = value
            self.request_render()

    @property
    def min_width(self) -> int:
        return self._min_width

    @min_width.setter
    def min_width(self, value: int) -> None:
        self._min_width = max(1, int(value))
        self.request_render()

    @property
    def padding_right(self) -> int:
        return self._padding_right

    @padding_right.setter
    def padding_right(self, value: int) -> None:
        self._padding_right = max(0, int(value))
        self.request_render()

    @property
    def show_line_numbers(self) -> bool:
        return self._show_line_numbers

    @show_line_numbers.setter
    def show_line_numbers(self, value: bool) -> None:
        self._show_line_numbers = value
        self.request_render()

    def set_scroll_offset(self, offset: int) -> None:
        offset = max(0, int(offset))
        if offset != self._scroll_offset:
            self._scroll_offset = offset
            self.scroll_offset = offset
            self.request_render()

    def set_line_number_offset(self, offset: int) -> None:
        self.line_number_offset = offset

    def set_hide_line_numbers(self, hide: set[int] | list[int]) -> None:
        self._hide_line_numbers = set(hide)
        self.request_render()

    def get_hide_line_numbers(self) -> set[int]:
        return set(self._hide_line_numbers)

    def set_line_numbers(self, line_numbers: dict[int, int]) -> None:
        self._line_numbers = dict(line_numbers)
        self.request_render()

    def get_line_numbers(self) -> dict[int, int]:
        return dict(self._line_numbers)

    def set_line_color(self, line: int, color: str | tuple | LineColorConfig) -> None:
        self._parse_line_color(line, color)
        self.request_render()

    def clear_line_color(self, line: int) -> None:
        self._line_colors_gutter.pop(line, None)
        self._line_colors_content.pop(line, None)
        self.request_render()

    def clear_all_line_colors(self) -> None:
        self._line_colors_gutter.clear()
        self._line_colors_content.clear()
        self.request_render()

    def set_line_colors(self, line_colors: dict[int, str | tuple | LineColorConfig]) -> None:
        self._line_colors_gutter.clear()
        self._line_colors_content.clear()
        for line, color in line_colors.items():
            self._parse_line_color(line, color)
        self.request_render()

    def get_line_colors(self) -> dict[str, dict[int, tuple[int, int, int, int]]]:
        return {"gutter": dict(self._line_colors_gutter), "content": dict(self._line_colors_content)}

    def set_line_sign(self, line: int, sign: LineSign) -> None:
        self._line_signs[line] = dict(sign)
        self.request_render()

    def clear_line_sign(self, line: int) -> None:
        self._line_signs.pop(line, None)
        self.request_render()

    def clear_all_line_signs(self) -> None:
        self._line_signs.clear()
        self.request_render()

    def set_line_signs(self, line_signs: dict[int, LineSign]) -> None:
        self._line_signs = {k: dict(v) for k, v in line_signs.items()}
        self.request_render()

    def get_line_signs(self) -> dict[int, LineSign]:
        return dict(self._line_signs)

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if not self._show_line_numbers:
            return
        w = min(max(self.line_number_width, self._min_width), self.width)
        for dy in range(self.height):
            line_num_0 = self._scroll_offset + dy
            line_bg = self._line_colors_gutter.get(line_num_0, self.bg)
            if line_num_0 + 1 > self.line_count:
                num_str = "".ljust(w)
            elif line_num_0 in self._hide_line_numbers:
                num_str = "".ljust(w)
            else:
                display_num = self._line_numbers.get(line_num_0, line_num_0 + 1 + self._line_number_offset)
                num_str = str(display_num).rjust(w)
            fg = self.fg
            for dx, ch in enumerate(num_str):
                if dx < self.width:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=ch, fg=fg, bg=line_bg),
                    )
            for dx in range(len(num_str), w):
                if dx < self.width:
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(char=" ", fg=fg, bg=line_bg),
                    )
