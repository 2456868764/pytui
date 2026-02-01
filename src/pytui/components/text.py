# pytui.components.text - Text component (OpenTUI-aligned: content string | StyledText, fg, bg, attributes, selectable)


from __future__ import annotations

from pytui.components.text_node import Span
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import ADDED, REMOVED, Renderable
from pytui.core.types import TextAttributes
from pytui.lib import parse_color_to_tuple

# OpenTUI: content is string | StyledText. In pytui, StyledText = list of Span or str (inline rich text).
StyledText = list[Span | str]


def _content_to_spans(content: str | StyledText) -> list[Span]:
    """Normalize content to list[Span]. string -> [Span(text=content)]; list of Span|str -> list[Span]."""
    if isinstance(content, str):
        return [Span(text=content)] if content else []
    out: list[Span] = []
    for s in content:
        if isinstance(s, str):
            out.append(Span(text=s))
        else:
            out.append(s)
    return out


def _has_get_span(obj: Any) -> bool:
    """True if obj is an inline text child (span/br/b etc.) with get_span()."""
    return callable(getattr(obj, "get_span", None))


class Text(Renderable):
    """Text component: content (string | StyledText), fg, bg, attributes, selectable, position, left/top/right/bottom. Aligns with OpenTUI Text."""

    def add(self, child: Renderable, index: int | None = None) -> None:
        """Override: inline children (get_span) are not added to layout_node."""
        if child.parent:
            child.parent.remove(child)
        child.parent = self
        if index is None:
            self.children.append(child)
            if not _has_get_span(child):
                self.layout_node.add_child(child.layout_node)
        else:
            self.children.insert(index, child)
            if not _has_get_span(child):
                self.layout_node.add_child(child.layout_node, index)
        self.emit("child_added", child)
        child.emit(ADDED, self)
        self.request_render()

    def remove(self, child: Renderable | str) -> None:
        """Override: inline children were not added to layout_node."""
        if isinstance(child, str):
            super().remove(child)
            return
        if child in self.children:
            self.children.remove(child)
            if not _has_get_span(child):
                self.layout_node.remove_child(child.layout_node)
            child.parent = None
            self.emit("child_removed", child)
            child.emit(REMOVED, self)
            self.request_render()

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        raw = options.get("content", "")
        self._content: str | StyledText = raw  # string or list[Span] / list[Span|str]
        self.fg = parse_color_to_tuple(options.get("fg", "#ffffff"))
        self.bg = parse_color_to_tuple(options.get("bg", "transparent"))
        attrs = options.get("attributes", options.get("attributes"))
        if attrs is not None and isinstance(attrs, int):
            self.bold = bool(attrs & TextAttributes.BOLD)
            self.dim = bool(attrs & TextAttributes.DIM)
            self.italic = bool(attrs & TextAttributes.ITALIC)
            self.underline = bool(attrs & TextAttributes.UNDERLINE)
            self.blink = bool(attrs & TextAttributes.BLINK)
            self.reverse = bool(attrs & TextAttributes.INVERSE)
            self.strikethrough = bool(attrs & TextAttributes.STRIKETHROUGH)
        else:
            self.bold = options.get("bold", False)
            self.dim = options.get("dim", False)
            self.italic = options.get("italic", False)
            self.underline = options.get("underline", False)
            self.blink = options.get("blink", False)
            self.reverse = options.get("reverse", False)
            self.strikethrough = options.get("strikethrough", False)
        # OpenTUI Text: selectable, position, left/top/right/bottom (number | "auto" | "{number}%")
        self.selectable = options.get("selectable", True)
        self.position: str = options.get("position", "relative")  # "relative" | "absolute"
        self.left = options.get("left")   # int | "auto" | "50%" | None
        self.top = options.get("top")
        self.right = options.get("right")
        self.bottom = options.get("bottom")

    def set_content(self, content: str | StyledText) -> None:
        if self.content != content:
            self._content = content
            self.request_render()

    @property
    def content(self) -> str | StyledText:
        """Align with OpenTUI content getter."""
        return getattr(self, "_content", "")

    @content.setter
    def content(self, value: str | StyledText) -> None:
        """Align with OpenTUI content setter."""
        self.set_content(value)

    def clear(self) -> None:
        """Align with OpenTUI clear(). Sets content to empty and request_render."""
        self._content = ""
        self.request_render()

    def _render_plain(self, buffer: OptimizedBuffer) -> None:
        content = self.content
        assert isinstance(content, str)
        lines = content.split("\n")
        for dy, line in enumerate(lines):
            if dy >= self.height:
                break
            for dx, char in enumerate(line):
                if dx >= self.width:
                    break
                buffer.set_cell(
                    self.x + dx,
                    self.y + dy,
                    Cell(
                        char=char,
                        fg=self.fg,
                        bg=self.bg,
                        bold=self.bold,
                        italic=self.italic,
                        underline=self.underline,
                        dim=self.dim,
                        blink=self.blink,
                        reverse=self.reverse,
                        strikethrough=self.strikethrough,
                    ),
                )

    def _render_styled(self, buffer: OptimizedBuffer, spans: list[Span] | None = None) -> None:
        if spans is None:
            spans = _content_to_spans(self.content)
        x, y = 0, 0
        for span in spans:
            fg = span.fg if span.fg is not None else self.fg
            bg = span.bg if span.bg is not None else self.bg
            for c in span.text:
                if c == "\n":
                    x = 0
                    y += 1
                    if y >= self.height:
                        return
                    continue
                while x >= self.width:
                    x = 0
                    y += 1
                    if y >= self.height:
                        return
                buffer.set_cell(
                    self.x + x,
                    self.y + y,
                    Cell(
                        char=c,
                        fg=fg,
                        bg=bg,
                        bold=span.bold,
                        italic=span.italic,
                        underline=span.underline,
                        dim=span.dim,
                        blink=span.blink,
                        reverse=span.reverse,
                        strikethrough=span.strikethrough,
                    ),
                )
                x += 1

    def render_self(self, buffer: OptimizedBuffer) -> None:
        # If all children are inline (get_span), render from them; else use content
        if self.children and all(_has_get_span(c) for c in self.children):
            spans = [c.get_span() for c in self.children]
            self._render_styled(buffer, spans=spans)
            return
        content = self.content
        if isinstance(content, str):
            self._render_plain(buffer)
        else:
            self._render_styled(buffer)
