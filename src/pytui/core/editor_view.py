# pytui.core.editor_view - 视口与 EditBuffer 绑定、光标、选区


from __future__ import annotations

from pytui.core.edit_buffer import EditBuffer


class EditorView:
    """编辑视口：绑定 EditBuffer，维护光标位置、滚动、选区。不负责渲染，供 Textarea 等组件使用。"""

    def __init__(self, buffer: EditBuffer, view_width: int = 80, view_height: int = 24) -> None:
        self.buffer = buffer
        self.view_width = max(1, view_width)
        self.view_height = max(1, view_height)
        self._cursor_pos = 0
        self._scroll_y = 0
        self._selection_anchor: int | None = None  # 选区起点，None 表示无选区

    @property
    def cursor_pos(self) -> int:
        return max(0, min(self._cursor_pos, len(self.buffer.text)))

    @cursor_pos.setter
    def cursor_pos(self, value: int) -> None:
        self._cursor_pos = max(0, min(value, len(self.buffer.text)))

    @property
    def cursor_line(self) -> int:
        return self.buffer.pos_to_line_col(self.cursor_pos)[0]

    @property
    def cursor_col(self) -> int:
        return self.buffer.pos_to_line_col(self.cursor_pos)[1]

    @property
    def scroll_y(self) -> int:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: int) -> None:
        self._scroll_y = max(0, min(value, max(0, self.buffer.line_count - self.view_height)))

    @property
    def selection_anchor(self) -> int | None:
        return self._selection_anchor

    def set_cursor(self, pos: int) -> None:
        """设置光标位置并清除选区。"""
        self.cursor_pos = pos
        self._selection_anchor = None

    def set_cursor_line_col(self, line: int, col: int) -> None:
        """按行号列号设置光标。"""
        self.cursor_pos = self.buffer.line_col_to_pos(line, col)
        self._selection_anchor = None

    def get_selection_range(self) -> tuple[int, int] | None:
        """返回 (start, end) 选区字符区间，无选区返回 None。"""
        if self._selection_anchor is None:
            return None
        a, b = self._selection_anchor, self.cursor_pos
        if a > b:
            a, b = b, a
        return (a, b)

    def set_selection(self, anchor: int, cursor: int) -> None:
        """设置选区：anchor 为起点，cursor 为终点。"""
        self._selection_anchor = max(0, min(anchor, len(self.buffer.text)))
        self.cursor_pos = cursor

    def clear_selection(self) -> None:
        self._selection_anchor = None

    def get_visible_lines(self) -> list[str]:
        """当前视口可见行（受 scroll_y 与 view_height 限制）。"""
        lines = self.buffer.get_lines()
        start = self.scroll_y
        end = min(start + self.view_height, len(lines))
        return lines[start:end]

    def ensure_cursor_visible(self) -> None:
        """滚动视口使光标所在行可见。"""
        line = self.cursor_line
        if line < self.scroll_y:
            self.scroll_y = line
        elif line >= self.scroll_y + self.view_height:
            self.scroll_y = line - self.view_height + 1

    def insert(self, text: str) -> None:
        """在光标处插入文本；若有选区则先删除选区内容。"""
        sel = self.get_selection_range()
        if sel is not None:
            start, end = sel
            self.buffer.delete(start, end)
            self.cursor_pos = start
            self._selection_anchor = None
        self.buffer.insert(self.cursor_pos, text)
        self.cursor_pos = self.cursor_pos + len(text)

    def delete_backward(self) -> bool:
        """删除光标前一个字符或选区，成功返回 True。"""
        sel = self.get_selection_range()
        if sel is not None:
            start, end = sel
            self.buffer.delete(start, end)
            self.cursor_pos = start
            self._selection_anchor = None
            return True
        if self.cursor_pos <= 0:
            return False
        self.buffer.delete(self.cursor_pos - 1, self.cursor_pos)
        self.cursor_pos = self.cursor_pos - 1
        return True

    def delete_forward(self) -> bool:
        """删除光标处字符或选区，成功返回 True。"""
        sel = self.get_selection_range()
        if sel is not None:
            start, end = sel
            self.buffer.delete(start, end)
            self.cursor_pos = start
            self._selection_anchor = None
            return True
        if self.cursor_pos >= len(self.buffer.text):
            return False
        self.buffer.delete(self.cursor_pos, self.cursor_pos + 1)
        return True

    def undo(self) -> bool:
        return self.buffer.undo()

    def redo(self) -> bool:
        return self.buffer.redo()
