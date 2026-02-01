# pytui.components.text - Text component aligned with OpenTUI TextRenderable / TextBufferRenderable
# content (string | StyledText), fg, bg, selectionBg, selectionFg, attributes, selectable,
# wrap_mode (none|char|word), truncate, tabIndicator, tabIndicatorColor,
# position, left/top/right/bottom. plainText, textLength, lineCount, virtualLineCount.
# See OpenTUI renderables/Text.ts, TextBufferRenderable.ts.

from __future__ import annotations

import re
from typing import Any, Literal

from pytui.components.text_node import Span
from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import ADDED, REMOVED, Renderable
from pytui.core.types import TextAttributes
from pytui.lib import parse_color_to_tuple

# OpenTUI: content is string | StyledText. In pytui, StyledText = list of Span or str (inline rich text).
StyledText = list[Span | str]

# OpenTUI TextBufferOptions: wrapMode "none" | "char" | "word" (default "word")
WrapMode = Literal["none", "char", "word"]


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


def _wrap_line(line: str, width: int, mode: WrapMode) -> list[str]:
    """Break a single logical line into visual lines. Align OpenTUI wrap: word/char/none."""
    if width <= 0:
        return [line] if line else []
    if mode == "none":
        return [line] if line else []
    if mode == "char":
        return [line[i : i + width] for i in range(0, len(line), width)] if line else []
    # word: break at word boundaries; long words break by char
    out: list[str] = []
    rest = line
    while rest:
        if len(rest) <= width:
            out.append(rest)
            break
        segment = rest[: width + 1]
        last_space = segment.rfind(" ")
        if last_space >= 0:
            out.append(rest[:last_space].rstrip())
            rest = rest[last_space + 1 :].lstrip()
        else:
            # no space in segment, break by char (long word)
            out.append(rest[:width])
            rest = rest[width:]
    return out


def _has_get_span(obj: Any) -> bool:
    """True if obj is an inline text child (span/br/b etc.) with get_span()."""
    return callable(getattr(obj, "get_span", None))


def _content_to_plain_text(content: str | StyledText) -> str:
    """Get plain string from content. Align OpenTUI getPlainText."""
    if isinstance(content, str):
        return content
    return "".join(s.text if hasattr(s, "text") else str(s) for s in content)


def _compute_line_counts(content: str | StyledText, width: int, wrap_mode: WrapMode) -> tuple[int, int]:
    """Return (line_count, virtual_line_count). Align OpenTUI lineCount / getVirtualLineCount."""
    plain = _content_to_plain_text(content)
    if not plain:
        return 0, 0
    logical_lines = plain.split("\n")
    line_count = len(logical_lines)
    if width <= 0 or wrap_mode == "none":
        return line_count, line_count
    virtual = 0
    for line in logical_lines:
        virtual += len(_wrap_line(line, width, wrap_mode))
    return line_count, virtual


def _expand_tab(text: str, tab_indicator: str | int | None) -> str:
    """Replace \\t with tab_indicator (string or number of spaces). Align OpenTUI tabIndicator."""
    if tab_indicator is None:
        return text
    if isinstance(tab_indicator, int):
        return text.replace("\t", " " * max(1, tab_indicator))
    return text.replace("\t", tab_indicator)


class Text(Renderable):
    """Text component. Aligns OpenTUI TextRenderable/TextBufferRenderable: content, fg, bg, attributes,
    selectable, wrap_mode (none|char|word), truncate, position, left/top/right/bottom."""

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

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        raw = options.get("content", "")
        self._content: str | StyledText = raw
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
        self.selectable = options.get("selectable", True)
        self.position = options.get("position", "relative")
        self.left = options.get("left")
        self.top = options.get("top")
        self.right = options.get("right")
        self.bottom = options.get("bottom")
        # OpenTUI TextBufferOptions: wrapMode, truncate, selectionBg/Fg, tabIndicator
        self._wrap_mode: WrapMode = options.get("wrapMode", options.get("wrap_mode", "word"))
        self._truncate: bool = options.get("truncate", False)
        self._selection_bg = parse_color_to_tuple(options.get("selectionBg", options.get("selection_bg"))) if options.get("selectionBg") or options.get("selection_bg") else None
        self._selection_fg = parse_color_to_tuple(options.get("selectionFg", options.get("selection_fg"))) if options.get("selectionFg") or options.get("selection_fg") else None
        self._tab_indicator = options.get("tabIndicator", options.get("tab_indicator"))
        self._tab_indicator_color = parse_color_to_tuple(options.get("tabIndicatorColor", options.get("tab_indicator_color"))) if options.get("tabIndicatorColor") or options.get("tab_indicator_color") else None

    @property
    def wrap_mode(self) -> WrapMode:
        """Align OpenTUI wrapMode getter."""
        return self._wrap_mode

    @wrap_mode.setter
    def wrap_mode(self, value: WrapMode) -> None:
        if self._wrap_mode != value:
            self._wrap_mode = value
            self.request_render()

    @property
    def truncate(self) -> bool:
        """Align OpenTUI truncate getter."""
        return self._truncate

    @truncate.setter
    def truncate(self, value: bool) -> None:
        if self._truncate != value:
            self._truncate = value
            self.request_render()

    @property
    def selection_bg(self) -> tuple[int, int, int, int] | None:
        """Align OpenTUI selectionBg."""
        return getattr(self, "_selection_bg", None)

    @selection_bg.setter
    def selection_bg(self, value: tuple[int, int, int, int] | str | None) -> None:
        parsed = parse_color_to_tuple(value) if value is not None else None
        if getattr(self, "_selection_bg", None) != parsed:
            self._selection_bg = parsed
            self.request_render()

    @property
    def selection_fg(self) -> tuple[int, int, int, int] | None:
        """Align OpenTUI selectionFg."""
        return getattr(self, "_selection_fg", None)

    @selection_fg.setter
    def selection_fg(self, value: tuple[int, int, int, int] | str | None) -> None:
        parsed = parse_color_to_tuple(value) if value is not None else None
        if getattr(self, "_selection_fg", None) != parsed:
            self._selection_fg = parsed
            self.request_render()

    @property
    def tab_indicator(self) -> str | int | None:
        """Align OpenTUI tabIndicator."""
        return getattr(self, "_tab_indicator", None)

    @tab_indicator.setter
    def tab_indicator(self, value: str | int | None) -> None:
        if getattr(self, "_tab_indicator", None) != value:
            self._tab_indicator = value
            self.request_render()

    @property
    def tab_indicator_color(self) -> tuple[int, int, int, int] | None:
        """Align OpenTUI tabIndicatorColor."""
        return getattr(self, "_tab_indicator_color", None)

    @tab_indicator_color.setter
    def tab_indicator_color(self, value: tuple[int, int, int, int] | str | None) -> None:
        parsed = parse_color_to_tuple(value) if value is not None else None
        if getattr(self, "_tab_indicator_color", None) != parsed:
            self._tab_indicator_color = parsed
            self.request_render()

    @property
    def plain_text(self) -> str:
        """Plain string from content. Align OpenTUI getPlainText / plainText."""
        return _content_to_plain_text(self.content)

    @property
    def text_length(self) -> int:
        """Length of plain text. Align OpenTUI textLength."""
        return len(self.plain_text)

    @property
    def line_count(self) -> int:
        """Number of logical lines. Align OpenTUI lineCount."""
        return _compute_line_counts(self.content, max(1, self.width), self._wrap_mode)[0]

    @property
    def virtual_line_count(self) -> int:
        """Number of visual lines after wrapping. Align OpenTUI getVirtualLineCount / virtualLineCount."""
        return _compute_line_counts(self.content, max(1, self.width), self._wrap_mode)[1]

    def set_content(self, content: str | StyledText) -> None:
        if self.content != content:
            self._content = content
            self.request_render()

    @property
    def content(self) -> str | StyledText:
        return getattr(self, "_content", "")

    @content.setter
    def content(self, value: str | StyledText) -> None:
        self.set_content(value)

    def clear(self) -> None:
        """Align OpenTUI clear()."""
        self._content = ""
        self.request_render()

    def _render_plain(self, buffer: OptimizedBuffer) -> None:
        """Render plain string. Respect wrap_mode (none/char/word) and truncate. Align OpenTUI."""
        content = self.content
        assert isinstance(content, str)
        max_w = max(1, self.width)
        max_h = max(1, self.height)
        dy = 0
        for logical_line in content.split("\n"):
            if dy >= max_h:
                return
            logical_line = _expand_tab(logical_line, self._tab_indicator)
            if self._wrap_mode == "none":
                visual_lines = [logical_line]
            else:
                visual_lines = _wrap_line(logical_line, max_w, self._wrap_mode)
            for vis in visual_lines:
                if dy >= max_h:
                    return
                if self._truncate and len(vis) > max_w:
                    vis = vis[: max_w - 1] + "…" if max_w > 0 else ""
                for dx, char in enumerate(vis):
                    if dx >= max_w:
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
                dy += 1

    def _render_styled(self, buffer: OptimizedBuffer, spans: list[Span] | None = None) -> None:
        """Render styled content. Respect wrap_mode (none/char/word). Align OpenTUI."""
        if spans is None:
            spans = _content_to_spans(self.content)
        max_w = max(1, self.width)
        max_h = max(1, self.height)
        # Flatten to (char, style) per position for wrap then draw
        flat: list[tuple[str, tuple, tuple, bool, bool, bool, bool, bool, bool, bool]] = []
        tab_ind = getattr(self, "_tab_indicator", None)
        for span in spans:
            fg = span.fg if span.fg is not None else self.fg
            bg = span.bg if span.bg is not None else self.bg
            for c in span.text:
                if c == "\t" and tab_ind is not None:
                    repl = " " * max(1, tab_ind) if isinstance(tab_ind, int) else tab_ind
                    for rc in repl:
                        flat.append(
                            (
                                rc,
                                fg,
                                bg,
                                span.bold or False,
                                span.italic or False,
                                span.underline or False,
                                span.dim or False,
                                span.blink or False,
                                span.reverse or False,
                                span.strikethrough or False,
                            )
                        )
                else:
                    flat.append(
                        (
                            c,
                            fg,
                            bg,
                            span.bold or False,
                            span.italic or False,
                            span.underline or False,
                            span.dim or False,
                            span.blink or False,
                            span.reverse or False,
                            span.strikethrough or False,
                        )
                    )
        # Build full text and wrap into visual lines (by char indices)
        full_text = "".join(c for c, *_ in flat)
        logical_lines = full_text.split("\n")
        # Map \n to positions so we know where each logical line starts/ends
        pos = 0
        line_ranges: list[tuple[int, int]] = []
        for ll in logical_lines:
            start = pos
            pos += len(ll) + 1  # +1 for \n
            line_ranges.append((start, start + len(ll)))
        dy = 0
        for (start, end) in line_ranges:
            if dy >= max_h:
                return
            segment = flat[start:end]
            seg_text = "".join(c for c, *_ in segment)
            if self._wrap_mode == "none":
                vis_lines_indices: list[tuple[int, int]] = [(0, len(segment))]
            else:
                vis_lines = _wrap_line(seg_text, max_w, self._wrap_mode)
                vis_lines_indices = []
                idx = 0
                for vis in vis_lines:
                    n = len(vis)
                    vis_lines_indices.append((idx, idx + n))
                    idx += n
            for (i0, i1) in vis_lines_indices:
                if dy >= max_h:
                    return
                row = segment[i0:i1]
                if self._truncate and len(row) > max_w:
                    row = row[:max_w]
                for dx, (c, fg, bg, bold, italic, underline, dim, blink, reverse, strike) in enumerate(row):
                    if dx >= max_w:
                        break
                    buffer.set_cell(
                        self.x + dx,
                        self.y + dy,
                        Cell(
                            char=c,
                            fg=fg,
                            bg=bg,
                            bold=bold,
                            italic=italic,
                            underline=underline,
                            dim=dim,
                            blink=blink,
                            reverse=reverse,
                            strikethrough=strike,
                        ),
                    )
                dy += 1

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.children and all(_has_get_span(c) for c in self.children):
            spans = [c.get_span() for c in self.children]
            self._render_styled(buffer, spans=spans)
            return
        content = self.content
        if isinstance(content, str):
            self._render_plain(buffer)
        else:
            self._render_styled(buffer)
