# pytui.core.terminal_palette - 终端调色板检测与映射


from __future__ import annotations

import os

# 能力：truecolor | 256 | 16 | mono
ColorCapability = str

# 256 色标准 xterm 调色板前 16 与 216 立方 + 24 灰度
def _xterm_256_palette() -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    # 0: 默认, 1-15: 16 色
    sixteen = [
        (0, 0, 0, 255),
        (205, 0, 0, 255),
        (0, 205, 0, 255),
        (205, 205, 0, 255),
        (0, 0, 238, 255),
        (205, 0, 205, 255),
        (0, 205, 205, 255),
        (229, 229, 229, 255),
        (76, 76, 76, 255),
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (255, 255, 0, 255),
        (92, 92, 255, 255),
        (255, 0, 255, 255),
        (0, 255, 255, 255),
        (255, 255, 255, 255),
    ]
    out.extend(sixteen)
    # 16-231: 6x6x6 立方
    for r in range(6):
        for g in range(6):
            for b in range(6):
                out.append((
                    55 + r * 40 if r else 0,
                    55 + g * 40 if g else 0,
                    55 + b * 40 if b else 0,
                    255,
                ))
    # 232-255: 灰度
    for i in range(24):
        v = 8 + i * 10
        if v > 238:
            v = 238
        out.append((v, v, v, 255))
    return out


_XTERM_256: list[tuple[int, int, int, int]] | None = None


def get_palette_color(index: int) -> tuple[int, int, int, int]:
    """返回 256 调色板中索引 index 的 (r,g,b,a)。越界返回黑色。"""
    global _XTERM_256
    if _XTERM_256 is None:
        _XTERM_256 = _xterm_256_palette()
    if 0 <= index < len(_XTERM_256):
        return _XTERM_256[index]
    return (0, 0, 0, 255)


def detect_capability() -> ColorCapability:
    """检测终端颜色能力：truecolor | 256 | 16 | mono。"""
    color_term = os.environ.get("COLORTERM", "")
    if "truecolor" in color_term or "24bit" in color_term:
        return "truecolor"
    term = os.environ.get("TERM", "")
    if "256" in term or "xterm-256" in term.lower():
        return "256"
    if term and term != "dumb":
        return "16"
    return "mono"
