# pytui.testing.snapshot - buffer 快照（自写，不依赖 pytest 快照插件）


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytui.core.buffer import OptimizedBuffer


def buffer_snapshot_lines(buffer: "OptimizedBuffer") -> list[str]:
    """将 buffer 按行转为字符串列表，每行仅字符（用于快照比对）。"""
    lines = []
    for y in range(buffer.height):
        row = []
        for x in range(buffer.width):
            cell = buffer.get_cell(x, y)
            row.append(cell.char if cell else " ")
        lines.append("".join(row))
    return lines


def assert_buffer_snapshot(buffer: "OptimizedBuffer", expected_lines: list[str]) -> None:
    """断言 buffer 内容与 expected_lines 一致；行数/每行长度需与 buffer 尺寸一致。"""
    got = buffer_snapshot_lines(buffer)
    if len(expected_lines) != buffer.height:
        raise AssertionError(
            f"Line count: expected {buffer.height}, got {len(expected_lines)}\n"
            f"Got:\n" + "\n".join(repr(line) for line in got)
        )
    for y, (exp, g) in enumerate(zip(expected_lines, got)):
        if len(exp) != buffer.width:
            raise AssertionError(
                f"Row {y} length: expected {buffer.width}, got {len(exp)}; line={exp!r}"
            )
        if exp != g:
            raise AssertionError(
                f"Row {y} mismatch:\n  expected: {exp!r}\n  got:      {g!r}"
            )
