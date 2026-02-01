# pytui.core.text_buffer - Aligns with OpenTUI packages/core/src/text-buffer.ts
# TextBuffer, TextChunk, createTextBuffer (TextBuffer.create), setText, append, getPlainText, setStyledText,
# setDefaultFg/Bg/Attributes, resetDefaults, getLineCount, length, byteSize, getTextRange, clear, reset, destroy.
# PyTUI: pure Python implementation (no native); OpenTUI uses zig + lib.

from __future__ import annotations

from typing import Any

from pytui.core.types import WidthMethod


def _chunk_to_plain(chunk: dict[str, Any]) -> str:
    return chunk.get("text", "")


class TextBuffer:
    """Text buffer for styled/plain text. Aligns OpenTUI TextBuffer (API only; pure Python)."""

    def __init__(self, width_method: WidthMethod = "unicode") -> None:
        self._width_method = width_method
        self._length = 0
        self._byte_size = 0
        self._text = ""
        self._destroyed = False

    @classmethod
    def create(cls, width_method: WidthMethod) -> "TextBuffer":
        """Create text buffer (align OpenTUI TextBuffer.create)."""
        return cls(width_method=width_method or "unicode")

    def _guard(self) -> None:
        if self._destroyed:
            raise RuntimeError("TextBuffer is destroyed")

    def set_text(self, text: str) -> None:
        self._guard()
        self._text = text
        self._length = len(text)
        self._byte_size = len(text.encode("utf-8"))

    def append(self, text: str) -> None:
        self._guard()
        if not text:
            return
        # Normalize CRLF to LF
        text = text.replace("\r\n", "\n")
        self._text += text
        self._length = len(self._text)
        self._byte_size = len(self._text.encode("utf-8"))

    def set_styled_text(self, styled_text: Any) -> None:
        """Set content from StyledText (chunks with text). Aligns OpenTUI setStyledText."""
        self._guard()
        chunks = getattr(styled_text, "chunks", styled_text) if not isinstance(styled_text, list) else styled_text
        self._text = "".join(_chunk_to_plain(c) for c in chunks)
        self._length = len(self._text)
        self._byte_size = len(self._text.encode("utf-8"))

    def set_default_fg(self, fg: Any | None) -> None:
        self._guard()
        pass  # stub: no native

    def set_default_bg(self, bg: Any | None) -> None:
        self._guard()
        pass

    def set_default_attributes(self, attributes: int | None) -> None:
        self._guard()
        pass

    def reset_defaults(self) -> None:
        self._guard()
        pass

    def get_line_count(self) -> int:
        self._guard()
        if not self._text:
            return 1
        return self._text.count("\n") + 1

    @property
    def length(self) -> int:
        self._guard()
        return self._length

    @property
    def byte_size(self) -> int:
        self._guard()
        return self._byte_size

    def get_plain_text(self) -> str:
        self._guard()
        return self._text

    def get_text_range(self, start_offset: int, end_offset: int) -> str:
        self._guard()
        if start_offset >= end_offset:
            return ""
        if self._byte_size == 0:
            return ""
        return self._text[start_offset:end_offset]

    def clear(self) -> None:
        self._guard()
        self._text = ""
        self._length = 0
        self._byte_size = 0

    def reset(self) -> None:
        self._guard()
        self._text = ""
        self._length = 0
        self._byte_size = 0

    def destroy(self) -> None:
        if self._destroyed:
            return
        self._destroyed = True
        self._text = ""
