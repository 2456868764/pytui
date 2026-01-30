# pytui.core.edit_buffer - 编辑缓冲：insert/delete/undo/redo，与 native TextBuffer/Rope 解耦（纯 Python 实现）


from __future__ import annotations

from typing import Any


class EditBuffer:
    """可编辑文本缓冲：insert/delete/undo/redo。纯 Python 实现，不依赖 Rope。"""

    def __init__(self, text: str = "") -> None:
        self._text = text
        self._undo_stack: list[tuple[str, Any, ...]] = []
        self._redo_stack: list[tuple[str, Any, ...]] = []

    @property
    def text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        self._text = text
        self._undo_stack.clear()
        self._redo_stack.clear()

    def get_lines(self) -> list[str]:
        """按行返回，末尾无 \\n。"""
        if not self._text:
            return [""]
        return self._text.split("\n")

    @property
    def line_count(self) -> int:
        return len(self.get_lines())

    def insert(self, pos: int, text: str) -> None:
        """在字符位置 pos 处插入 text。"""
        if not text:
            return
        pos = max(0, min(pos, len(self._text)))
        self._undo_stack.append(("insert", pos, text))
        self._redo_stack.clear()
        self._text = self._text[:pos] + text + self._text[pos:]

    def delete(self, start: int, end: int) -> str:
        """删除 [start, end) 区间字符，返回被删内容。"""
        start = max(0, min(start, len(self._text)))
        end = max(start, min(end, len(self._text)))
        if start >= end:
            return ""
        deleted = self._text[start:end]
        self._undo_stack.append(("delete", start, deleted))
        self._redo_stack.clear()
        self._text = self._text[:start] + self._text[end:]
        return deleted

    def undo(self) -> bool:
        """撤销上一次编辑，成功返回 True。"""
        if not self._undo_stack:
            return False
        op = self._undo_stack.pop()
        if op[0] == "insert":
            _, pos, text = op
            self._text = self._text[:pos] + self._text[pos + len(text) :]
            self._redo_stack.append(("insert", pos, text))
        elif op[0] == "delete":
            _, start, deleted = op
            self._text = self._text[:start] + deleted + self._text[start:]
            self._redo_stack.append(("delete", start, deleted))
        return True

    def redo(self) -> bool:
        """重做上一次撤销，成功返回 True。"""
        if not self._redo_stack:
            return False
        op = self._redo_stack.pop()
        if op[0] == "insert":
            _, pos, text = op
            self._text = self._text[:pos] + text + self._text[pos:]
            self._undo_stack.append(("insert", pos, text))
        elif op[0] == "delete":
            _, start, deleted = op
            self._text = self._text[:start] + self._text[start + len(deleted) :]
            self._undo_stack.append(("delete", start, deleted))
        return True

    def pos_to_line_col(self, pos: int) -> tuple[int, int]:
        """将字符位置转为 (行, 列)，0-based。"""
        pos = max(0, min(pos, len(self._text)))
        lines = self.get_lines()
        offset = 0
        for line_idx, line in enumerate(lines):
            line_len = len(line) + 1  # +1 for \n
            if offset + line_len > pos or line_idx == len(lines) - 1:
                col = pos - offset
                return line_idx, min(col, len(line))
            offset += line_len
        return len(lines) - 1, len(lines[-1])

    def line_col_to_pos(self, line: int, col: int) -> int:
        """将 (行, 列) 转为字符位置，0-based。"""
        lines = self.get_lines()
        line = max(0, min(line, len(lines) - 1))
        col = max(0, min(col, len(lines[line])))
        pos = 0
        for i in range(line):
            pos += len(lines[i]) + 1
        return pos + col
