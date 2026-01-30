# pytui.components.ascii_font - 艺术字组件（可选多套字体 JSON）


from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable

# RGBA tuple
ColorTuple = tuple[int, int, int, int]

# 内置 tiny 字体（简化版，参考 cfonts）
TINY_FONT = {
    "name": "tiny",
    "lines": 2,
    "letterspace_size": 1,
    "chars": {
        "A": ["▄▀█", "█▀█"],
        "B": ["█▄▄", "█▄█"],
        "C": ["█▀▀", "█▄▄"],
        "D": ["█▀▄", "█▄▀"],
        "E": ["█▀▀", "██▄"],
        "F": ["█▀▀", "█▀ "],
        "G": ["█▀▀", "█▄█"],
        "H": ["█ █", "█▀█"],
        "I": ["█", "█"],
        "J": ["  █", "█▄█"],
        "K": ["█▄▀", "█ █"],
        "L": ["█  ", "█▄▄"],
        "M": ["█▀▄▀█", "█ ▀ █"],
        "N": ["█▄ █", "█ ▀█"],
        "O": ["█▀█", "█▄█"],
        "P": ["█▀█", "█▀▀"],
        "Q": ["█▀█", "▀▀█"],
        "R": ["█▀█", "█▀▄"],
        "S": ["█▀▀", "▄▄█"],
        "T": ["▀█▀", " █ "],
        "U": ["█ █", "█▄█"],
        "V": ["█ █", "▀▄▀"],
        "W": ["█ █ █", "▀▄▀▄▀"],
        "X": ["▀▄▀", "█ █"],
        "Y": ["█▄█", " █ "],
        "Z": ["▀█", "█▄"],
        "0": ["▞█▚", "▚█▞"],
        "1": ["▄█", " █"],
        "2": ["▀█", "█▄"],
        " ": [" ", " "],
        ".": [" ", "▄"],
        "!": ["█", "▄"],
        "?": ["▀█", " ▄"],
        "-": ["▄▄", "  "],
        "_": ["  ", "▄▄"],
    },
}

# 内置 block 风格（方块体，3 行高，与 tiny 区分）
BLOCK_FONT = {
    "name": "block",
    "lines": 3,
    "letterspace_size": 0,
    "chars": {
        "A": [" ▄▄ ", "█  █", "█▄▄█"],
        "B": ["█▄▄ ", "█  █", "█▄▄ "],
        "C": [" ▄▄▄", "█   ", " ▀▀▀"],
        "D": ["█▄▄ ", "█  █", "█▄▄ "],
        "E": ["█▄▄▄", "█   ", "█▄▄▄"],
        "F": ["█▄▄▄", "█   ", "█   "],
        "G": [" ▄▄▄", "█  ▄", " ▀▀█"],
        "H": ["█  █", "█▄▄█", "█  █"],
        "I": ["▄█▄", " █ ", "▀█▀"],
        "J": ["   █", "   █", "▄▄█ "],
        "K": ["█  █", "█▄▄ ", "█  █"],
        "L": ["█   ", "█   ", "█▄▄▄"],
        "M": ["█ █ █", "██ ██", "█   █"],
        "N": ["█   █", "██  █", "█  ██"],
        "O": [" ▄▄ ", "█  █", " ▀▀ "],
        "P": ["█▄▄ ", "█  █", "█   "],
        "Q": [" ▄▄ ", "█  █", " ▀▀█"],
        "R": ["█▄▄ ", "█  █", "█  █"],
        "S": [" ▄▄▄", " ▀▀ ", "▄▄▄ "],
        "T": ["▀█▀", " █ ", " █ "],
        "U": ["█  █", "█  █", " ▀▀ "],
        "V": ["█   █", " █ █ ", "  █  "],
        "W": ["█   █", "█ █ █", " █ █ "],
        "X": ["█   █", " █ █ ", "█   █"],
        "Y": ["█   █", " █ █ ", "  █  "],
        "Z": ["▀▀▀", " ▄█ ", "▀▀▀ "],
        "0": [" ▄▄ ", "█ ██", " ▀▀ "],
        "1": [" █ ", "▄█ ", " █ "],
        "2": [" ▄▄ ", "  █ ", "▄▄▄ "],
        " ": ["   ", "   ", "   "],
        ".": ["   ", "   ", " █ "],
        "!": [" █ ", " █ ", " █ "],
        "?": [" ▄▄ ", "  █ ", " █  "],
        "-": ["    ", " ▄▄ ", "    "],
        "_": ["    ", "    ", "    "],
    },
}

# slick / shade 使用 block 风格（与 tiny 明显区分即可）
SLICK_FONT = {**BLOCK_FONT, "name": "slick"}
SHADE_FONT = {**BLOCK_FONT, "name": "shade"}


# 未知字符用空格
def _char_lines(font: dict, ch: str) -> list[str]:
    c = font["chars"].get(ch.upper(), font["chars"].get(" ", [" ", " "]))
    return c if isinstance(c[0], str) else [" ", " "]


def measure_text(text: str, font: dict | None = None) -> tuple[int, int]:
    """返回 (width, height)。"""
    font = font or TINY_FONT
    lines_count = font["lines"]
    letter_space = font.get("letterspace_size", 1)
    w = 0
    for i, ch in enumerate(text):
        char_lines = _char_lines(font, ch)
        cw = max((len(line) for line in char_lines), default=1)
        w += cw
        if i < len(text) - 1:
            w += letter_space
    return (max(0, w), lines_count)


def character_bounds(text: str, index: int, font: dict | None = None) -> tuple[int, int, int, int] | None:
    """返回字符 index 在艺术字布局中的 (x_start, y_start, x_end, y_end)；越界返回 None。"""
    if index < 0 or index >= len(text):
        return None
    font = font or TINY_FONT
    w_before, _ = measure_text(text[:index], font)
    w_after, h = measure_text(text[: index + 1], font)
    return (w_before, 0, w_after, h)


def render_font_to_buffer(
    buffer: OptimizedBuffer,
    text: str,
    x: int,
    y: int,
    font: dict | None = None,
    fg: ColorTuple | None = None,
    bg: ColorTuple | None = None,
) -> tuple[int, int]:
    """将艺术字绘制到 buffer 的 (x,y)，返回 (width, height)。"""
    font = font or TINY_FONT
    fg = fg or (255, 255, 255, 255)
    bg = bg or (0, 0, 0, 0)
    lines_count = font["lines"]
    letter_space = font.get("letterspace_size", 1)
    buf_h, buf_w = buffer.height, buffer.width
    cur_x = x
    for i, ch in enumerate(text):
        char_lines = _char_lines(font, ch)
        cw = max(len(line) for line in char_lines) if char_lines else 1
        for line_idx, line in enumerate(char_lines):
            ry = y + line_idx
            if ry < 0 or ry >= buf_h:
                continue
            for dx, char in enumerate(line):
                rx = cur_x + dx
                if 0 <= rx < buf_w and char != " ":
                    buffer.set_cell(rx, ry, Cell(char=char, fg=fg, bg=bg))
        cur_x += cw + letter_space
    return (max(0, cur_x - x - letter_space), lines_count)


def load_font_from_json(path: str | Path) -> dict:
    """从 JSON 文件加载字体（与 OpenTUI tiny/block 等格式兼容）。"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {
        "name": data.get("name", "custom"),
        "lines": data["lines"],
        "letterspace_size": data.get("letterspace_size", 1),
        "chars": data["chars"],
    }


class ASCIIFont(Renderable):
    """艺术字组件：用内置或可选 JSON 字体渲染文本。可选 selectable、选区高亮（selectionBg/selectionFg）。"""

    _fonts: dict[str, dict] = {
        "tiny": TINY_FONT,
        "block": BLOCK_FONT,
        "slick": SLICK_FONT,
        "shade": SHADE_FONT,
    }

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._text = options.get("text", "")
        self._font_name = options.get("font", "tiny")
        self._font_dict = options.get("font_dict")  # 可选：直接传字体 dict
        self._fg = parse_color(options.get("fg", "#ffffff"))
        self._bg = parse_color(options.get("bg", "transparent"))
        self._buffer: OptimizedBuffer | None = None
        self._buf_w = 0
        self._buf_h = 0
        self._selectable = options.get("selectable", False)
        self._selection_bg = parse_color(options.get("selection_bg", options.get("selectionBg", "#4444aa")))
        self._selection_fg = parse_color(options.get("selection_fg", options.get("selectionFg", "#ffffff")))
        self._cursor_pos = 0
        self._selection_anchor: int | None = None
        self._update_size()

    def _get_font(self) -> dict:
        if self._font_dict is not None:
            return self._font_dict
        return self._fonts.get(self._font_name, TINY_FONT)

    def _update_size(self) -> None:
        w, h = measure_text(self._text, self._get_font())
        self.layout_node.set_width(max(1, w))
        self.layout_node.set_height(max(1, h))

    def set_text(self, text: str) -> None:
        self._text = text
        self._update_size()
        self._buffer = None
        self.request_render()

    def set_font(self, font_name: str) -> None:
        self._font_name = font_name
        self._font_dict = None
        self._update_size()
        self._buffer = None
        self.request_render()

    def _get_selection_range(self) -> tuple[int, int] | None:
        if self._selection_anchor is None:
            return None
        a, b = self._selection_anchor, self._cursor_pos
        if a > b:
            a, b = b, a
        return (a, b)

    def focus(self) -> None:
        super().focus()
        if self._selectable and hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.events.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.events.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if not self.focused or not self._selectable:
            return
        name = key.get("name") or key.get("char")
        shift = key.get("shift", False)
        n = len(self._text)
        if name == "left":
            if self._cursor_pos > 0:
                if shift and self._selection_anchor is None:
                    self._selection_anchor = self._cursor_pos
                elif not shift:
                    self._selection_anchor = None
                self._cursor_pos -= 1
                self.request_render()
            return
        if name == "right":
            if self._cursor_pos < n:
                if shift and self._selection_anchor is None:
                    self._selection_anchor = self._cursor_pos
                elif not shift:
                    self._selection_anchor = None
                self._cursor_pos += 1
                self.request_render()
            return
        if name == "home":
            self._cursor_pos = 0
            if not shift:
                self._selection_anchor = None
            self.request_render()
            return
        if name == "end":
            self._cursor_pos = n
            if not shift:
                self._selection_anchor = None
            self.request_render()
            return

    def _ensure_buffer(self) -> None:
        font = self._get_font()
        w, h = measure_text(self._text, font)
        w, h = max(1, w), max(1, h)
        if self._buffer is None or self._buf_w != w or self._buf_h != h:
            self._buffer = OptimizedBuffer(w, h, use_native=False)
            self._buf_w, self._buf_h = w, h
        self._buffer.clear()
        render_font_to_buffer(self._buffer, self._text, 0, 0, font, self._fg, self._bg)

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if not self._text:
            return
        self._ensure_buffer()
        if self._buffer is None:
            return
        for dy in range(self._buffer.height):
            for dx in range(self._buffer.width):
                cell = self._buffer.get_cell(dx, dy)
                if cell is not None:
                    buffer.set_cell(self.x + dx, self.y + dy, cell)
        if self._selectable and self.focused:
            sel = self._get_selection_range()
            if sel is not None:
                font = self._get_font()
                for idx in range(sel[0], sel[1]):
                    bounds = character_bounds(self._text, idx, font)
                    if bounds is None:
                        continue
                    x0, y0, x1, y1 = bounds
                    for by in range(y0, y1):
                        for bx in range(x0, x1):
                            if 0 <= bx < self._buffer.width and 0 <= by < self._buffer.height:
                                cell = self._buffer.get_cell(bx, by)
                                if cell is not None:
                                    buffer.set_cell(
                                        self.x + bx,
                                        self.y + by,
                                        Cell(char=cell.char, fg=self._selection_fg, bg=self._selection_bg),
                                    )

    @classmethod
    def register_font(cls, name: str, font_dict: dict) -> None:
        """注册命名字体，供 font= 使用。"""
        cls._fonts[name] = font_dict
