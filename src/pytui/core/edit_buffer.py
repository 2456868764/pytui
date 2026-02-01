# pytui.core.edit_buffer - Aligns with OpenTUI packages/core/src/edit-buffer.ts
# EditBuffer.create(widthMethod), setText, getText, replaceText, getCursorPosition, setCursor, setCursorToLineCol,
# gotoLine, moveCursorLeft/Right/Up/Down, insertChar, insertText, deleteChar, deleteCharBackward, undo, redo, destroy.

from __future__ import annotations

from typing import Any, TypedDict

HighlightDict = dict[str, Any]


class LogicalCursor(TypedDict):
    row: int
    col: int
    offset: int


class EditBuffer:
    """可编辑文本缓冲：光标、insert/delete/undo/redo，highlights。API 对齐 OpenTUI EditBuffer。"""

    def __init__(self, text: str = "") -> None:
        self._text = text
        self._cursor_row = 0
        self._cursor_col = 0
        self._undo_stack: list[tuple[str, Any, ...]] = []
        self._redo_stack: list[tuple[str, Any, ...]] = []
        self._line_highlights: dict[int, list[HighlightDict]] = {}
        self._hl_ref_counter = 0
        self._destroyed = False

    @classmethod
    def create(cls, width_method: str = "unicode") -> "EditBuffer":
        """Create edit buffer (align OpenTUI EditBuffer.create)."""
        return cls()

    def _guard(self) -> None:
        if self._destroyed:
            raise RuntimeError("EditBuffer is destroyed")

    @property
    def text(self) -> str:
        return self._text

    def get_text(self) -> str:
        """Align OpenTUI getText()."""
        self._guard()
        return self._text

    def set_text(self, text: str) -> None:
        """Set text and completely reset buffer state (clears history). Aligns OpenTUI setText()."""
        self._guard()
        self._text = text
        self._cursor_row = 0
        self._cursor_col = 0
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._line_highlights.clear()

    def replace_text(self, text: str) -> None:
        """Replace text while preserving undo history (one undo point). Aligns OpenTUI replaceText()."""
        self._guard()
        old = self._text
        self._text = text
        self._cursor_row = 0
        self._cursor_col = 0
        self._undo_stack.append(("replace", old, text))
        self._redo_stack.clear()
        self._line_highlights.clear()

    def get_lines(self) -> list[str]:
        self._guard()
        if not self._text:
            return [""]
        return self._text.split("\n")

    def get_line_count(self) -> int:
        """Align OpenTUI getLineCount()."""
        self._guard()
        return len(self.get_lines())

    @property
    def line_count(self) -> int:
        return len(self.get_lines())

    def get_cursor_position(self) -> LogicalCursor:
        """Align OpenTUI getCursorPosition() -> { row, col, offset }."""
        self._guard()
        offset = self.line_col_to_pos(self._cursor_row, self._cursor_col)
        return {"row": self._cursor_row, "col": self._cursor_col, "offset": offset}

    def set_cursor(self, row: int, col: int) -> None:
        """Align OpenTUI setCursor(line, col)."""
        self._guard()
        lines = self.get_lines()
        row = max(0, min(row, len(lines) - 1))
        col = max(0, min(col, len(lines[row])))
        self._cursor_row = row
        self._cursor_col = col

    def set_cursor_to_line_col(self, line: int, col: int) -> None:
        """Align OpenTUI setCursorToLineCol(line, col)."""
        self.set_cursor(line, col)

    def goto_line(self, line: int) -> None:
        """Align OpenTUI gotoLine(line)."""
        self._guard()
        lines = self.get_lines()
        line = max(0, min(line, len(lines) - 1))
        self._cursor_row = line
        self._cursor_col = 0

    def move_cursor_left(self) -> None:
        self._guard()
        if self._cursor_col > 0:
            self._cursor_col -= 1
        elif self._cursor_row > 0:
            self._cursor_row -= 1
            self._cursor_col = len(self.get_lines()[self._cursor_row])

    def move_cursor_right(self) -> None:
        self._guard()
        lines = self.get_lines()
        if self._cursor_col < len(lines[self._cursor_row]):
            self._cursor_col += 1
        elif self._cursor_row < len(lines) - 1:
            self._cursor_row += 1
            self._cursor_col = 0

    def move_cursor_up(self) -> None:
        self._guard()
        if self._cursor_row > 0:
            self._cursor_row -= 1
            self._cursor_col = min(self._cursor_col, len(self.get_lines()[self._cursor_row]))

    def move_cursor_down(self) -> None:
        self._guard()
        lines = self.get_lines()
        if self._cursor_row < len(lines) - 1:
            self._cursor_row += 1
            self._cursor_col = min(self._cursor_col, len(lines[self._cursor_row]))

    def insert_char(self, char: str) -> None:
        """Align OpenTUI insertChar(char)."""
        self.insert_text(char)

    def insert_text(self, text: str) -> None:
        """Align OpenTUI insertText(text)."""
        self._guard()
        if not text:
            return
        pos = self.line_col_to_pos(self._cursor_row, self._cursor_col)
        self.insert(pos, text)
        new_row, new_col = self.pos_to_line_col(pos + len(text))
        self._cursor_row, self._cursor_col = new_row, new_col

    def insert(self, pos: int, text: str) -> None:
        if not text:
            return
        pos = max(0, min(pos, len(self._text)))
        self._undo_stack.append(("insert", pos, text))
        self._redo_stack.clear()
        self._text = self._text[:pos] + text + self._text[pos:]

    def delete_char(self) -> None:
        """Delete char at cursor (align OpenTUI deleteChar)."""
        self._guard()
        pos = self.line_col_to_pos(self._cursor_row, self._cursor_col)
        if pos < len(self._text):
            self.delete(pos, pos + 1)

    def delete_char_backward(self) -> None:
        """Backspace (align OpenTUI deleteCharBackward)."""
        self._guard()
        pos = self.line_col_to_pos(self._cursor_row, self._cursor_col)
        if pos > 0:
            self.delete(pos - 1, pos)
            self._cursor_col = max(0, self._cursor_col - 1)
            if self._cursor_col == 0 and self._cursor_row > 0:
                self._cursor_row -= 1
                self._cursor_col = len(self.get_lines()[self._cursor_row])

    def new_line(self) -> None:
        """Align OpenTUI newLine()."""
        self.insert_text("\n")

    def delete_line(self) -> None:
        """Align OpenTUI deleteLine() - delete current line."""
        self._guard()
        lines = self.get_lines()
        if self._cursor_row >= len(lines):
            return
        start = self.line_col_to_pos(self._cursor_row, 0)
        end = start + len(lines[self._cursor_row]) + (1 if self._cursor_row < len(lines) - 1 else 0)
        self.delete(start, end)
        self._cursor_col = 0

    def delete(self, start: int, end: int) -> str:
        self._guard()
        start = max(0, min(start, len(self._text)))
        end = max(start, min(end, len(self._text)))
        if start >= end:
            return ""
        deleted = self._text[start:end]
        self._undo_stack.append(("delete", start, deleted))
        self._redo_stack.clear()
        self._text = self._text[:start] + self._text[end:]
        # Keep cursor in bounds
        new_row, new_col = self.pos_to_line_col(min(start, len(self._text)))
        self._cursor_row, self._cursor_col = new_row, new_col
        return deleted

    def undo(self) -> bool:
        self._guard()
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
        elif op[0] == "replace":
            _, old_text, new_text = op
            self._text = old_text
            self._redo_stack.append(("replace", new_text, old_text))
        return True

    def redo(self) -> bool:
        self._guard()
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
        elif op[0] == "replace":
            _, new_text, old_text = op
            self._text = new_text
            self._undo_stack.append(("replace", old_text, new_text))
        return True

    def pos_to_line_col(self, pos: int) -> tuple[int, int]:
        self._guard()
        pos = max(0, min(pos, len(self._text)))
        lines = self.get_lines()
        offset = 0
        for line_idx, line in enumerate(lines):
            line_len = len(line) + 1
            if offset + line_len > pos or line_idx == len(lines) - 1:
                col = pos - offset
                return line_idx, min(col, len(line))
            offset += line_len
        return len(lines) - 1, len(lines[-1])

    def line_col_to_pos(self, line: int, col: int) -> int:
        self._guard()
        lines = self.get_lines()
        line = max(0, min(line, len(lines) - 1))
        col = max(0, min(col, len(lines[line])))
        pos = 0
        for i in range(line):
            pos += len(lines[i]) + 1
        return pos + col

    def clear(self) -> None:
        self.set_text("")

    def get_text_range(self, start_offset: int, end_offset: int) -> str:
        self._guard()
        return self._text[start_offset:end_offset]

    def get_text_range_by_coords(
        self, start_row: int, start_col: int, end_row: int, end_col: int
    ) -> str:
        start = self.line_col_to_pos(start_row, start_col)
        end = self.line_col_to_pos(end_row, end_col)
        return self._text[start:end]

    def delete_range(
        self, start_line: int, start_col: int, end_line: int, end_col: int
    ) -> None:
        start = self.line_col_to_pos(start_line, start_col)
        end = self.line_col_to_pos(end_line, end_col)
        self.delete(start, end)

    def add_highlight(self, line_idx: int, highlight: HighlightDict) -> None:
        if line_idx not in self._line_highlights:
            self._line_highlights[line_idx] = []
        hl = dict(highlight)
        if hl.get("hl_ref") is None:
            self._hl_ref_counter += 1
            hl["hl_ref"] = self._hl_ref_counter
        self._line_highlights[line_idx].append(hl)

    def add_highlight_by_char_range(self, highlight: HighlightDict) -> None:
        start = highlight.get("start", 0)
        line_idx, _ = self.pos_to_line_col(start)
        self.add_highlight(line_idx, highlight)

    def get_line_highlights(self, line_idx: int) -> list[HighlightDict]:
        return list(self._line_highlights.get(line_idx, []))

    def remove_highlights_by_ref(self, hl_ref: int) -> None:
        for line_idx in list(self._line_highlights):
            self._line_highlights[line_idx] = [
                h for h in self._line_highlights[line_idx] if h.get("hl_ref") != hl_ref
            ]
            if not self._line_highlights[line_idx]:
                del self._line_highlights[line_idx]

    def clear_line_highlights(self, line_idx: int) -> None:
        self._line_highlights.pop(line_idx, None)

    def clear_all_highlights(self) -> None:
        self._line_highlights.clear()

    def destroy(self) -> None:
        """Align OpenTUI destroy()."""
        if self._destroyed:
            return
        self._destroyed = True
        self._text = ""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._line_highlights.clear()
