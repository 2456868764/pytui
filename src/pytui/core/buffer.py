# pytui.core.buffer - frame buffer and Cell

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

try:
    from pytui_native import Buffer as NativeBuffer
    from pytui_native import Cell as NativeCell

    HAS_NATIVE = True
except ImportError:
    HAS_NATIVE = False
    NativeBuffer = None  # type: ignore[misc, assignment]
    NativeCell = None  # type: ignore[misc, assignment]


@dataclass
class Cell:
    """终端单元格"""

    char: str = " "
    fg: tuple[int, int, int, int] = (255, 255, 255, 255)
    bg: tuple[int, int, int, int] = (0, 0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = False

    def to_native(self) -> Any:
        """转换为原生 Cell（无 native 时返回 None）。"""
        if HAS_NATIVE and NativeCell is not None:
            cell = NativeCell()
            cell.char = self.char
            cell.fg = self.fg
            cell.bg = self.bg
            cell.bold = self.bold
            cell.italic = self.italic
            cell.underline = self.underline
            return cell
        return None


class OptimizedBuffer:
    """优化的帧缓冲区（支持 native 或纯 Python 后备）。"""

    def __init__(self, width: int, height: int, use_native: bool = True) -> None:
        self.width = width
        self.height = height
        self.use_native = use_native and HAS_NATIVE and NativeBuffer is not None

        if self.use_native:
            self._native_buffer = NativeBuffer(width, height)
            self.cells = None
        else:
            self._native_buffer = None
            self.cells = np.empty((height, width), dtype=object)
            self.clear()

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        """设置单元格。越界时静默忽略。"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.use_native and self._native_buffer is not None:
            self._native_buffer.set_cell(x, y, cell.to_native())
        else:
            self.cells[y, x] = cell

    @staticmethod
    def blend_color(
        fg: tuple[int, int, int, int],
        bg: tuple[int, int, int, int],
        alpha: float,
    ) -> tuple[int, int, int, int]:
        """按 alpha (0~1) 混合前景与背景色，返回 (r,g,b,a)。"""
        a = max(0.0, min(1.0, alpha))
        r = int(fg[0] * a + bg[0] * (1 - a))
        g = int(fg[1] * a + bg[1] * (1 - a))
        b = int(fg[2] * a + bg[2] * (1 - a))
        out_a = int(fg[3] * a + bg[3] * (1 - a))
        return (r, g, b, out_a)

    def set_cell_with_alpha(
        self,
        x: int,
        y: int,
        cell: Cell,
        alpha: float = 1.0,
    ) -> None:
        """设置单元格；alpha < 1 时与当前格混合（blend）。越界静默忽略。"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if alpha >= 1.0:
            self.set_cell(x, y, cell)
            return
        existing = self.get_cell(x, y)
        if existing is None:
            self.set_cell(x, y, cell)
            return
        blended_fg = self.blend_color(cell.fg, existing.fg, alpha)
        blended_bg = self.blend_color(cell.bg, existing.bg, alpha)
        blended = Cell(
            char=cell.char,
            fg=blended_fg,
            bg=blended_bg,
            bold=cell.bold or existing.bold,
            italic=cell.italic or existing.italic,
            underline=cell.underline or existing.underline,
        )
        self.set_cell(x, y, blended)

    def get_cell(self, x: int, y: int) -> Cell | None:
        """获取单元格，越界返回 None。"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        if self.use_native and self._native_buffer is not None:
            nc = self._native_buffer.get_cell(x, y)
            return Cell(
                char=nc.char,
                fg=nc.fg,
                bg=nc.bg,
                bold=nc.bold,
                italic=nc.italic,
                underline=nc.underline,
            )
        return self.cells[y, x]

    def draw_text(
        self, text: str, x: int, y: int, fg: tuple[int, int, int, int]
    ) -> None:
        """绘制文本，超出宽度截断。"""
        if self.use_native and self._native_buffer is not None:
            self._native_buffer.draw_text(text, x, y, fg)
        else:
            for i, char in enumerate(text):
                if x + i >= self.width:
                    break
                self.set_cell(x + i, y, Cell(char=char, fg=fg))

    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        cell: Cell,
    ) -> None:
        """填充矩形区域。"""
        for dy in range(height):
            for dx in range(width):
                self.set_cell(x + dx, y + dy, cell)

    def clear(self) -> None:
        """清空缓冲区。"""
        if self.use_native and self._native_buffer is not None:
            self._native_buffer.clear()
        else:
            for y in range(self.height):
                for x in range(self.width):
                    self.cells[y, x] = Cell()

    def to_ansi(self) -> str:
        """转换为 ANSI 转义序列（整屏）。"""
        lines = []
        for y in range(self.height):
            line_chars = []
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    line_chars.append(self._cell_to_ansi(cell))
            lines.append("".join(line_chars))
        return "\n".join(lines)

    def _cell_to_ansi(self, cell: Cell) -> str:
        """单格转 ANSI。"""

        codes = []
        if cell.bold:
            codes.append("1")
        if cell.italic:
            codes.append("3")
        if cell.underline:
            codes.append("4")
        r, g, b, a = cell.fg
        if a > 0:
            codes.append(f"38;2;{r};{g};{b}")
        r, g, b, a = cell.bg
        if a > 0:
            codes.append(f"48;2;{r};{g};{b}")
        prefix = f'\x1b[{";".join(codes)}m' if codes else ""
        return f"{prefix}{cell.char}\x1b[0m"
