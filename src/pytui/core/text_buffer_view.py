# pytui.core.text_buffer_view - Aligns with OpenTUI packages/core/src/text-buffer-view.ts
# TextBufferView.create(textBuffer), setSelection, updateSelection, resetSelection, getSelection,
# hasSelection, setWrapWidth, setViewportSize, lineInfo, getPlainText, getSelectedText, destroy.
# PyTUI: pure Python stub (no native); OpenTUI uses zig + lib.

from __future__ import annotations

from typing import Any

from pytui.core.types import LineInfo
from pytui.core.text_buffer import TextBuffer


class TextBufferView:
    """View over TextBuffer for selection, viewport, line info. Aligns OpenTUI TextBufferView (API stub)."""

    def __init__(self, text_buffer: TextBuffer) -> None:
        self._text_buffer = text_buffer
        self._destroyed = False
        self._selection_start: int | None = None
        self._selection_end: int | None = None
        self._wrap_width: int = 0
        self._wrap_mode: str = "none"  # "none" | "char" | "word"
        self._viewport_width = 0
        self._viewport_height = 0

    @classmethod
    def create(cls, text_buffer: TextBuffer) -> "TextBufferView":
        """Create view (align OpenTUI TextBufferView.create)."""
        return cls(text_buffer)

    def _guard(self) -> None:
        if self._destroyed:
            raise RuntimeError("TextBufferView is destroyed")

    def set_selection(self, start: int, end: int, bg_color: Any = None, fg_color: Any = None) -> None:
        self._guard()
        self._selection_start = start
        self._selection_end = end

    def update_selection(self, end: int, bg_color: Any = None, fg_color: Any = None) -> None:
        self._guard()
        if self._selection_start is not None:
            self._selection_end = end

    def reset_selection(self) -> None:
        self._guard()
        self._selection_start = None
        self._selection_end = None

    def get_selection(self) -> tuple[int, int] | None:
        self._guard()
        if self._selection_start is None or self._selection_end is None:
            return None
        return (self._selection_start, self._selection_end)

    def has_selection(self) -> bool:
        self._guard()
        return self.get_selection() is not None

    def set_wrap_width(self, width: int | None) -> None:
        self._guard()
        self._wrap_width = width or 0

    def set_wrap_mode(self, mode: str) -> None:
        """mode: 'none' | 'char' | 'word'. Aligns OpenTUI setWrapMode."""
        self._guard()
        self._wrap_mode = mode

    def set_viewport_size(self, width: int, height: int) -> None:
        self._guard()
        self._viewport_width = width
        self._viewport_height = height

    def set_viewport(self, x: int, y: int, width: int, height: int) -> None:
        self._guard()
        self._viewport_width = width
        self._viewport_height = height

    @property
    def line_info(self) -> LineInfo:
        self._guard()
        text = self._text_buffer.get_plain_text()
        lines = text.split("\n") if text else [""]
        line_starts: list[int] = []
        line_widths: list[int] = []
        pos = 0
        for line in lines:
            line_starts.append(pos)
            line_widths.append(len(line))
            pos += len(line) + 1
        max_w = max(line_widths) if line_widths else 0
        return {
            "line_starts": line_starts,
            "line_widths": line_widths,
            "max_line_width": max_w,
            "line_sources": list(range(len(lines))),
            "line_wraps": [0] * len(lines),
        }

    def get_plain_text(self) -> str:
        self._guard()
        return self._text_buffer.get_plain_text()

    def get_selected_text(self) -> str:
        self._guard()
        sel = self.get_selection()
        if sel is None:
            return ""
        start, end = sel
        return self._text_buffer.get_text_range(start, end)

    def get_virtual_line_count(self) -> int:
        self._guard()
        info = self.line_info
        return len(info["line_starts"])

    def destroy(self) -> None:
        if self._destroyed:
            return
        self._destroyed = True
