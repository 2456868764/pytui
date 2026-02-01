# pytui.core.editor_view - Aligns with OpenTUI packages/core/src/editor-view.ts
# EditorView.create(editBuffer, viewportWidth, viewportHeight), setViewportSize, getViewport, setSelection,
# getSelection, hasSelection, getVirtualLineCount, destroy.

from __future__ import annotations

from typing import Any, TypedDict

from pytui.core.edit_buffer import EditBuffer


class Viewport(TypedDict):
    offset_y: int
    offset_x: int
    height: int
    width: int


class EditorView:
    """编辑视口：绑定 EditBuffer，维护光标位置、滚动、选区。API 对齐 OpenTUI EditorView。"""

    def __init__(self, buffer: EditBuffer, view_width: int = 80, view_height: int = 24) -> None:
        self.buffer = buffer
        self.view_width = max(1, view_width)
        self.view_height = max(1, view_height)
        self._cursor_pos = 0
        self._scroll_y = 0
        self._selection_anchor: int | None = None
        self._selection_end: int | None = None
        self._wrap_mode: str = "word"
        self._scroll_margin: float = 0.2
        self._tab_indicator: str | int | None = None
        self._tab_indicator_color: tuple[int, int, int, int] | None = None
        self._destroyed = False

    @classmethod
    def create(cls, edit_buffer: EditBuffer, viewport_width: int, viewport_height: int) -> "EditorView":
        """Create editor view (align OpenTUI EditorView.create)."""
        return cls(edit_buffer, viewport_width, viewport_height)

    def _guard(self) -> None:
        if self._destroyed:
            raise RuntimeError("EditorView is destroyed")

    def destroy(self) -> None:
        """Align OpenTUI destroy()."""
        if self._destroyed:
            return
        self._destroyed = True

    def set_wrap_mode(self, mode: str) -> None:
        """Aligns OpenTUI setWrapMode()."""
        self._guard()
        self._wrap_mode = mode

    def set_scroll_margin(self, margin: float) -> None:
        """Aligns OpenTUI setScrollMargin()."""
        self._guard()
        self._scroll_margin = max(0.0, min(1.0, margin))

    def set_viewport_size(self, width: int, height: int) -> None:
        """Aligns OpenTUI setViewportSize()."""
        self._guard()
        self.view_width = max(1, width)
        self.view_height = max(1, height)

    def set_viewport(self, x: int, y: int, width: int, height: int, move_cursor: bool = True) -> None:
        """Align OpenTUI setViewport(x, y, width, height, moveCursor)."""
        self._guard()
        self._scroll_y = y
        self.view_width = max(1, width)
        self.view_height = max(1, height)

    def get_viewport(self) -> Viewport:
        """Align OpenTUI getViewport() -> { offsetY, offsetX, height, width }."""
        self._guard()
        return {
            "offset_y": self._scroll_y,
            "offset_x": 0,
            "height": self.view_height,
            "width": self.view_width,
        }

    def get_virtual_line_count(self) -> int:
        """Align OpenTUI getVirtualLineCount()."""
        self._guard()
        return self.buffer.get_line_count()

    def get_total_virtual_line_count(self) -> int:
        """Align OpenTUI getTotalVirtualLineCount()."""
        return self.get_virtual_line_count()

    def set_selection(self, start: int, end: int, bg_color: Any = None, fg_color: Any = None) -> None:
        """Align OpenTUI setSelection(start, end, bgColor?, fgColor?)."""
        self._guard()
        self._selection_anchor = start
        self._selection_end = end
        self._cursor_pos = end  # get_selection_range uses cursor_pos as end

    def update_selection(self, end: int, bg_color: Any = None, fg_color: Any = None) -> None:
        self._guard()
        self._selection_end = end

    def reset_selection(self) -> None:
        self._guard()
        self._selection_anchor = None
        self._selection_end = None

    def get_selection(self) -> tuple[int, int] | None:
        """Align OpenTUI getSelection() -> { start, end } | null."""
        self._guard()
        if self._selection_anchor is None:
            return None
        end = self._selection_end if self._selection_end is not None else self._selection_anchor
        return (self._selection_anchor, end)

    def has_selection(self) -> bool:
        self._guard()
        return self.get_selection() is not None

    def set_tab_indicator(self, value: str | int) -> None:
        """Aligns OpenTUI setTabIndicator()."""
        self._tab_indicator = value

    def set_tab_indicator_color(self, color: tuple[int, int, int, int]) -> None:
        """Aligns OpenTUI setTabIndicatorColor()."""
        self._tab_indicator_color = color

    @property
    def cursor_pos(self) -> int:
        self._guard()
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
    def cursor_offset(self) -> int:
        """Character offset (same as cursor_pos). Aligns OpenTUI cursorOffset."""
        return self.cursor_pos

    @cursor_offset.setter
    def cursor_offset(self, value: int) -> None:
        self.set_cursor(max(0, min(value, len(self.buffer.text))))

    def set_cursor_by_offset(self, offset: int) -> None:
        """Set cursor by character offset. Aligns OpenTUI setCursorByOffset."""
        self.cursor_offset = offset

    def get_visual_cursor(self) -> tuple[int, int]:
        """Return (visual_row, visual_col) in viewport coords. Aligns OpenTUI getVisualCursor()."""
        row = self.cursor_line - self.scroll_y
        col = self.cursor_col
        return (max(0, row), col)

    @property
    def scroll_y(self) -> int:
        self._guard()
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
        self._guard()
        if self._selection_anchor is None:
            return None
        a, b = self._selection_anchor, self.cursor_pos
        if a > b:
            a, b = b, a
        return (a, b)

    def get_selected_text(self) -> str:
        """Return selected text. Aligns OpenTUI getSelectedText()."""
        sel = self.get_selection_range()
        if sel is None:
            return ""
        return self.buffer.text[sel[0] : sel[1]]

    def clear_selection(self) -> None:
        self._selection_anchor = None

    @property
    def virtual_line_count(self) -> int:
        """Virtual line count (with wrapping). We don't wrap, so same as line count. Aligns OpenTUI getVirtualLineCount()."""
        return self.buffer.line_count

    def get_visible_lines(self) -> list[str]:
        """当前视口可见行（受 scroll_y 与 view_height 限制）。"""
        lines = self.buffer.get_lines()
        start = self.scroll_y
        end = min(start + self.view_height, len(lines))
        return lines[start:end]

    def get_logical_line_info(self) -> dict[str, Any]:
        """Line info for layout. Aligns OpenTUI getLogicalLineInfo(). Returns line_starts, line_widths, max_line_width."""
        lines = self.buffer.get_lines()
        line_starts = [0]
        line_widths: list[int] = []
        for line in lines:
            line_widths.append(len(line))
            line_starts.append(line_starts[-1] + len(line) + 1)
        line_starts = line_starts[:-1]
        max_line_width = max(line_widths) if line_widths else 0
        return {
            "line_starts": line_starts,
            "line_widths": line_widths,
            "max_line_width": max_line_width,
        }

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
