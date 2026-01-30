# pytui.core.selection - 选区状态：anchor + cursor，供 EditorView/Textarea 等复用


from __future__ import annotations


class SelectionState:
    """独立选区状态：维护 anchor 与 cursor，与 buffer 长度同步，供 EditorView/Textarea 复用。"""

    def __init__(self, length: int = 0) -> None:
        self._anchor: int | None = None
        self._cursor = 0
        self._length = max(0, length)

    def set_length(self, length: int) -> None:
        """同步 buffer 长度，并夹紧 anchor/cursor。"""
        self._length = max(0, length)
        self._cursor = max(0, min(self._cursor, self._length))
        if self._anchor is not None:
            self._anchor = max(0, min(self._anchor, self._length))

    def get_range(self) -> tuple[int, int] | None:
        """返回 (start, end) 选区字符区间，无选区返回 None。"""
        if self._anchor is None:
            return None
        a, b = self._anchor, self._cursor
        if a > b:
            a, b = b, a
        return (a, b)

    @property
    def cursor(self) -> int:
        return self._cursor

    @cursor.setter
    def cursor(self, value: int) -> None:
        self._cursor = max(0, min(value, self._length))

    @property
    def anchor(self) -> int | None:
        return self._anchor

    def set_cursor(self, pos: int) -> None:
        """设置光标并清除选区。"""
        self._cursor = max(0, min(pos, self._length))
        self._anchor = None

    def set_selection(self, anchor: int, cursor: int) -> None:
        """设置选区：anchor 为起点，cursor 为终点。"""
        self._anchor = max(0, min(anchor, self._length))
        self._cursor = max(0, min(cursor, self._length))

    def clear_selection(self) -> None:
        self._anchor = None

    def has_selection(self) -> bool:
        return self._anchor is not None
