# pytui.post.filters - Aligns with OpenTUI packages/core/src/post/filters.ts
# applyDim, applyBlur, applyGrayscale, applySepia, applyInvert, applyScanlines, applyNoise, applyAsciiArt.


from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytui.core.buffer import Cell, OptimizedBuffer


def _cell_with_fg_bg(
    cell: Cell,
    fg: tuple[int, int, int, int],
    bg: tuple[int, int, int, int],
) -> Cell:
    """返回与 cell 相同属性但 fg/bg 替换的新 Cell。"""
    from pytui.core.buffer import Cell

    return Cell(
        char=cell.char,
        fg=fg,
        bg=bg,
        bold=cell.bold,
        italic=cell.italic,
        underline=cell.underline,
        strikethrough=cell.strikethrough,
        dim=cell.dim,
        reverse=cell.reverse,
        blink=cell.blink,
    )


def apply_dim(buffer: OptimizedBuffer, alpha: float = 0.5) -> None:
    """对 buffer 整体做 dim（按 alpha 与黑色混合）。alpha=1 不变，alpha=0 全黑。"""
    if alpha >= 1.0:
        return
    from pytui.core.buffer import OptimizedBuffer

    black = (0, 0, 0, 255)
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            fg = OptimizedBuffer.blend_color(cell.fg, black, alpha)
            bg = OptimizedBuffer.blend_color(cell.bg, black, alpha)
            buffer.set_cell(x, y, _cell_with_fg_bg(cell, fg, bg))


def apply_grayscale(buffer: OptimizedBuffer) -> None:
    """将 buffer 前景/背景转为灰度（亮度 0.299*R + 0.587*G + 0.114*B）。"""
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            r, g, b, a = cell.fg
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            lum = max(0, min(255, lum))
            fg = (lum, lum, lum, a)
            r, g, b, a = cell.bg
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            lum = max(0, min(255, lum))
            bg = (lum, lum, lum, a)
            buffer.set_cell(x, y, _cell_with_fg_bg(cell, fg, bg))


def apply_sepia(buffer: OptimizedBuffer) -> None:
    """对 buffer 应用棕褐色调（sepia）。"""
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            r, g, b, a = cell.fg
            nr = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
            ng = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
            nb = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
            fg = (nr, ng, nb, a)
            r, g, b, a = cell.bg
            nr = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
            ng = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
            nb = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
            bg = (nr, ng, nb, a)
            buffer.set_cell(x, y, _cell_with_fg_bg(cell, fg, bg))


def apply_invert(buffer: OptimizedBuffer) -> None:
    """反转 buffer 前景/背景 RGB（255 - 分量），Alpha 不变。"""
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            r, g, b, a = cell.fg
            fg = (255 - r, 255 - g, 255 - b, a)
            r, g, b, a = cell.bg
            bg = (255 - r, 255 - g, 255 - b, a)
            buffer.set_cell(x, y, _cell_with_fg_bg(cell, fg, bg))


def apply_scanlines(
    buffer: OptimizedBuffer,
    strength: float = 0.8,
    step: int = 2,
) -> None:
    """每隔 step 行按 strength 变暗（扫描线效果）。strength=1 不变，strength=0 全黑。"""
    for y in range(0, buffer.height, step):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            r, g, b, a = cell.fg
            fg = (
                max(0, min(255, int(r * strength))),
                max(0, min(255, int(g * strength))),
                max(0, min(255, int(b * strength))),
                a,
            )
            r, g, b, a = cell.bg
            bg = (
                max(0, min(255, int(r * strength))),
                max(0, min(255, int(g * strength))),
                max(0, min(255, int(b * strength))),
                a,
            )
            buffer.set_cell(x, y, _cell_with_fg_bg(cell, fg, bg))


def apply_noise(buffer: OptimizedBuffer, strength: float = 0.1) -> None:
    """对前景/背景 RGB 加随机扰动并钳位。strength 对应约 ±strength*255 的扰动。"""
    scale = max(0.0, min(1.0, strength)) * 255
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            r, g, b, a = cell.fg
            noise_r = int((random.random() - 0.5) * 2 * scale)
            noise_g = int((random.random() - 0.5) * 2 * scale)
            noise_b = int((random.random() - 0.5) * 2 * scale)
            fg = (
                max(0, min(255, r + noise_r)),
                max(0, min(255, g + noise_g)),
                max(0, min(255, b + noise_b)),
                a,
            )
            r, g, b, a = cell.bg
            noise_r = int((random.random() - 0.5) * 2 * scale)
            noise_g = int((random.random() - 0.5) * 2 * scale)
            noise_b = int((random.random() - 0.5) * 2 * scale)
            bg = (
                max(0, min(255, r + noise_r)),
                max(0, min(255, g + noise_g)),
                max(0, min(255, b + noise_b)),
                a,
            )
            buffer.set_cell(x, y, _cell_with_fg_bg(cell, fg, bg))


def apply_ascii_art(
    buffer: OptimizedBuffer,
    ramp: str = " .:-=+*#%@",
) -> None:
    """按背景亮度将字符替换为 ramp 中字符（亮度越高字符越“亮”）。"""
    from pytui.core.buffer import Cell

    ramp_len = len(ramp)
    if ramp_len == 0:
        return
    for y in range(buffer.height):
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            if cell is None:
                continue
            r, g, b, _ = cell.bg
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            idx = min(ramp_len - 1, int(lum / 255.0 * ramp_len))
            ch = ramp[idx]
            new_cell = Cell(
                char=ch,
                fg=cell.fg,
                bg=cell.bg,
                bold=cell.bold,
                italic=cell.italic,
                underline=cell.underline,
                strikethrough=cell.strikethrough,
                dim=cell.dim,
                reverse=cell.reverse,
                blink=cell.blink,
            )
            buffer.set_cell(x, y, new_cell)


def apply_blur_placeholder(buffer: OptimizedBuffer, _radius: int = 1) -> None:
    """占位：blur 效果暂未实现，不修改 buffer。"""
    pass
