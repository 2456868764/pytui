# pytui.core.buffer - Frame buffer, Cell, OptimizedBuffer. Aligns with OpenTUI packages/core/src/buffer.ts
# API: create/static create, width/height/widthMethod, setRespectAlpha, setCell, drawText, fillRect, drawBox,
# clear, drawFrameBuffer, destroy, resize; getSpanLines/getRealCharBytes (native); pushScissorRect/popScissorRect,
# pushOpacity/popOpacity. PyTUI uses native_buffer (Rust) or numpy fallback; OpenTUI uses zig + bun:ffi.

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
    strikethrough: bool = False
    dim: bool = False
    reverse: bool = False
    blink: bool = False

    def to_native(self) -> Any:
        """转换为原生 Cell（无 native 时返回 None）。strikethrough/dim/reverse/blink 暂不写入 native。"""
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
    """优化的帧缓冲区。对齐 OpenTUI OptimizedBuffer（respectAlpha、widthMethod、create 等）。
    方案 B 阶段二：可传入 native_buffer 包装 CliRenderer 的 getNextBuffer/getCurrentBuffer。
    """

    @classmethod
    def create(
        cls,
        width: int,
        height: int,
        width_method: str,
        options: dict[str, Any] | None = None,
    ) -> "OptimizedBuffer":
        """Create buffer (align OpenTUI OptimizedBuffer.create). options: respect_alpha?, id?"""
        opts = options or {}
        respect_alpha = opts.get("respect_alpha", opts.get("respectAlpha", False))
        return cls(
            width=width,
            height=height,
            respect_alpha=respect_alpha,
            width_method=width_method or "unicode",
        )

    def __init__(
        self,
        width: int,
        height: int,
        use_native: bool = True,
        respect_alpha: bool = False,
        width_method: str = "unicode",
        *,
        native_buffer: Any = None,
    ) -> None:
        self.respect_alpha = respect_alpha
        self.width_method = width_method
        if native_buffer is not None:
            self._native_buffer = native_buffer
            self.use_native = True
            self.width = native_buffer.get_width()
            self.height = native_buffer.get_height()
            self.cells = None
        else:
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
        self._destroyed = False

    def destroy(self) -> None:
        """Release native buffer (align OpenTUI buffer.destroy()). No-op if already destroyed or Python fallback."""
        if getattr(self, "_destroyed", False):
            return
        self._destroyed = True
        if self.use_native and getattr(self, "_native_buffer", None) is not None:
            if hasattr(self._native_buffer, "destroy"):
                self._native_buffer.destroy()
            self._native_buffer = None
        self.cells = None

    def set_respect_alpha(self, value: bool) -> None:
        """对齐 OpenTUI setRespectAlpha()。"""
        self.respect_alpha = value

    def _guard(self) -> None:
        """Raise if buffer is destroyed (align OpenTUI guard())."""
        if getattr(self, "_destroyed", False):
            raise RuntimeError("Buffer is destroyed")

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        """设置单元格。越界时静默忽略。"""
        self._guard()
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
        self._guard()
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
            strikethrough=cell.strikethrough or existing.strikethrough,
            dim=cell.dim or existing.dim,
            reverse=cell.reverse or existing.reverse,
            blink=cell.blink or existing.blink,
        )
        self.set_cell(x, y, blended)

    def get_cell(self, x: int, y: int) -> Cell | None:
        """获取单元格，越界返回 None。"""
        self._guard()
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
                strikethrough=False,
                dim=False,
                reverse=False,
                blink=False,
            )
        return self.cells[y, x]

    def draw_text(self, text: str, x: int, y: int, fg: tuple[int, int, int, int]) -> None:
        """绘制文本，超出宽度截断。"""
        self._guard()
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
        self._guard()
        for dy in range(height):
            for dx in range(width):
                self.set_cell(x + dx, y + dy, cell)

    def draw_box(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        border_style: str = "single",
        custom_border_chars: list[int] | None = None,
        border: bool | list[str] = True,
        border_color: tuple[int, int, int, int],
        backgroundColor: tuple[int, int, int, int],
        should_fill: bool = True,
        title: str | None = None,
        title_alignment: str = "left",
    ) -> None:
        """Draw box with border and optional title. Aligns with OpenTUI buffer.drawBox()."""
        self._guard()
        from pytui.lib.border import BorderCharArrays, BorderChars, get_border_sides

        sides = get_border_sides(border)
        if custom_border_chars is not None and len(custom_border_chars) >= 11:
            # Use code points: tl, tr, bl, br, h, v, topT, bottomT, leftT, rightT, cross
            def ch_at(i: int) -> str:
                return chr(custom_border_chars[i]) if custom_border_chars[i] else " "
            tl, tr, bl, br, h, v, top_t, bottom_t, left_t, right_t, cross = (
                ch_at(0), ch_at(1), ch_at(2), ch_at(3), ch_at(4), ch_at(5),
                ch_at(6), ch_at(7), ch_at(8), ch_at(9), ch_at(10),
            )
        else:
            style = border_style if border_style in BorderChars else "single"
            bc = BorderChars[style]
            tl, tr, bl, br = bc.top_left, bc.top_right, bc.bottom_left, bc.bottom_right
            h, v = bc.horizontal, bc.vertical
            top_t, bottom_t, left_t, right_t, cross = bc.top_t, bc.bottom_t, bc.left_t, bc.right_t, bc.cross
        bg_cell = Cell(bg=backgroundColor, fg=border_color)

        def set_char(px: int, py: int, ch: str) -> None:
            if 0 <= px < self.width and 0 <= py < self.height:
                self.set_cell(px, py, Cell(char=ch, fg=border_color, bg=backgroundColor))

        # Fill interior if should_fill
        if should_fill and width > 0 and height > 0:
            inner_x = 1 if sides.left else 0
            inner_y = 1 if sides.top else 0
            inner_w = max(0, width - (1 if sides.left else 0) - (1 if sides.right else 0))
            inner_h = max(0, height - (1 if sides.top else 0) - (1 if sides.bottom else 0))
            if inner_w > 0 and inner_h > 0:
                self.fill_rect(x + inner_x, y + inner_y, inner_w, inner_h, bg_cell)

        # Corners and edges (top/bottom rows use tl/tr and bl/br at ends; left/right only when sides)
        if sides.top:
            set_char(x, y, tl)
            for dx in range(1, width - 1):
                set_char(x + dx, y, h)
            set_char(x + width - 1, y, tr)
        if sides.bottom:
            set_char(x, y + height - 1, bl)
            for dx in range(1, width - 1):
                set_char(x + dx, y + height - 1, h)
            set_char(x + width - 1, y + height - 1, br)
        if sides.left and height > 2:
            for dy in range(1, height - 1):
                set_char(x, y + dy, v)
        if sides.right and height > 2:
            for dy in range(1, height - 1):
                set_char(x + width - 1, y + dy, v)

        # Title on top row (inside border)
        if title and sides.top and height >= 1 and width > 2:
            title_row = y
            left_off = 1 if sides.left else 0
            right_off = 1 if sides.right else 0
            inner_w = width - left_off - right_off
            max_title_len = max(0, inner_w)
            display_title = (title[:max_title_len]) if len(title) > max_title_len else title
            if title_alignment == "center" and len(display_title) < max_title_len - 2:
                display_title = " " + display_title.strip() + " "
            elif title_alignment == "left" and display_title and display_title[0] != " ":
                display_title = " " + display_title
            if title_alignment == "center":
                start_x = x + left_off + (inner_w - len(display_title)) // 2
            elif title_alignment == "right":
                start_x = x + width - right_off - len(display_title)
            else:
                start_x = x + left_off
            for i, c in enumerate(display_title):
                set_char(start_x + i, title_row, c)

    def clear(self) -> None:
        """清空缓冲区。"""
        self._guard()
        if self.use_native and self._native_buffer is not None:
            self._native_buffer.clear()
        else:
            for y in range(self.height):
                for x in range(self.width):
                    self.cells[y, x] = Cell()

    def to_ansi(self) -> str:
        """转换为 ANSI 转义序列（整屏）。"""
        self._guard()
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
        """单格转 ANSI。SGR: bold=1, dim=2, italic=3, underline=4, blink=5, reverse=7, strikethrough=9。"""

        codes = []
        if cell.bold:
            codes.append("1")
        if cell.dim:
            codes.append("2")
        if cell.italic:
            codes.append("3")
        if cell.underline:
            codes.append("4")
        if cell.blink:
            codes.append("5")
        if cell.reverse:
            codes.append("7")
        if cell.strikethrough:
            codes.append("9")
        r, g, b, a = cell.fg
        if a > 0:
            codes.append(f"38;2;{r};{g};{b}")
        r, g, b, a = cell.bg
        if a > 0:
            codes.append(f"48;2;{r};{g};{b}")
        prefix = f"\x1b[{';'.join(codes)}m" if codes else ""
        return f"{prefix}{cell.char}\x1b[0m"
