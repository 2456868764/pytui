# pytui.post.filters - 后处理滤镜占位（dim、blur 等）


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytui.core.buffer import OptimizedBuffer


def apply_dim(buffer: OptimizedBuffer, alpha: float = 0.5) -> None:
    """占位：对 buffer 整体做 dim（按 alpha 与黑色混合）。alpha=1 不变，alpha=0 全黑。"""
    if alpha >= 1.0:
        return
    from pytui.core.buffer import Cell, OptimizedBuffer

    black = (0, 0, 0, 255)
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            fg = OptimizedBuffer.blend_color(cell.fg, black, alpha)
            bg = OptimizedBuffer.blend_color(cell.bg, black, alpha)
            buffer.set_cell(x, y, Cell(char=cell.char, fg=fg, bg=bg))


def apply_blur_placeholder(buffer: OptimizedBuffer, _radius: int = 1) -> None:
    """占位：blur 效果暂未实现，不修改 buffer。"""
    pass
