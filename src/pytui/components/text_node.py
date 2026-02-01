# pytui.components.text_node - Aligns with OpenTUI packages/core/src/renderables/TextNode.ts (inline rich text: Span, Bold/Italic/Underline/LineBreak, Link)
#
# Link 支持：使用 link(text, url, fg?, bg?) 创建带 href 的 Span，在 TextNode 中按行渲染；
# Span.href 为 URL，样式与普通 Span 相同，可设 fg/bg/underline 等。点击或键盘激活链接
# 由上层（焦点管理、keypress 处理）根据 href 处理；本组件仅负责渲染。
#

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.core.types import TextAttributes as TextNodeAttributes
from pytui.lib import parse_color_to_tuple

# RGBA tuple
ColorTuple = tuple[int, int, int, int]


@dataclass
class Span:
    """内联富文本片段：文本 + 可选样式与链接。"""

    text: str
    fg: ColorTuple | None = None
    bg: ColorTuple | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    dim: bool = False
    reverse: bool = False
    blink: bool = False
    href: str | None = None  # 可选 Link

    def __post_init__(self) -> None:
        if self.fg is not None and isinstance(self.fg, str):
            self.fg = parse_color_to_tuple(self.fg)
        elif self.fg is not None and hasattr(self.fg, "to_tuple"):
            self.fg = self.fg.to_tuple()
        if self.bg is not None and isinstance(self.bg, str):
            self.bg = parse_color_to_tuple(self.bg)
        elif self.bg is not None and hasattr(self.bg, "to_tuple"):
            self.bg = self.bg.to_tuple()


def bold(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """粗体片段。"""
    return Span(text=text, fg=fg, bg=bg, bold=True)


def italic(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """斜体片段。"""
    return Span(text=text, fg=fg, bg=bg, italic=True)


def underline(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """下划线片段。"""
    return Span(text=text, fg=fg, bg=bg, underline=True)


def line_break() -> Span:
    """换行。"""
    return Span(text="\n")


def link(text: str, url: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """链接片段（样式同 Span，href=url）。"""
    return Span(text=text, fg=fg, bg=bg, href=url)


def strikethrough(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """删除线片段。SGR 9。"""
    return Span(text=text, fg=fg, bg=bg, strikethrough=True)


def dim(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """暗淡片段。SGR 2。"""
    return Span(text=text, fg=fg, bg=bg, dim=True)


def reverse(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """反色片段（前景背景互换）。SGR 7。"""
    return Span(text=text, fg=fg, bg=bg, reverse=True)


def blink(text: str, fg: ColorTuple | str | None = None, bg: ColorTuple | str | None = None) -> Span:
    """闪烁片段。SGR 5。"""
    return Span(text=text, fg=fg, bg=bg, blink=True)


def _to_color_tuple(color: str | ColorTuple | Any) -> ColorTuple:
    """Normalize to (r, g, b, a). Accepts hex string, RGBA (to_tuple), or 3/4-int tuple/list."""
    if isinstance(color, (tuple, list)) and len(color) >= 3:
        t = tuple(color)[:4]
        if len(t) == 3:
            t = (*t, 255)
        return t  # type: ignore[return-value]
    return parse_color_to_tuple(color)


def fg(color: str | ColorTuple | Any) -> Any:
    """OpenTUI-style: fg(color)(content) — apply foreground color to string or Span. Combining: fg(\"#FF0000\")(bold(\"text\"))."""

    def apply(content: str | Span) -> Span:
        c = _to_color_tuple(color)
        if isinstance(content, Span):
            return Span(
                text=content.text,
                fg=c,
                bg=content.bg,
                bold=content.bold,
                italic=content.italic,
                underline=content.underline,
                strikethrough=content.strikethrough,
                dim=content.dim,
                reverse=content.reverse,
                blink=content.blink,
                href=content.href,
            )
        return Span(text=content, fg=c)

    return apply


def bg(color: str | ColorTuple | Any) -> Any:
    """OpenTUI-style: bg(color)(content) — apply background color to string or Span."""

    def apply(content: str | Span) -> Span:
        c = _to_color_tuple(color)
        if isinstance(content, Span):
            return Span(
                text=content.text,
                fg=content.fg,
                bg=c,
                bold=content.bold,
                italic=content.italic,
                underline=content.underline,
                strikethrough=content.strikethrough,
                dim=content.dim,
                reverse=content.reverse,
                blink=content.blink,
                href=content.href,
            )
        return Span(text=content, bg=c)

    return apply


def _normalize_spans(spans: list[Span | str]) -> list[Span]:
    out: list[Span] = []
    for s in spans:
        if isinstance(s, str):
            out.append(Span(text=s))
        else:
            out.append(s)
    return out


class TextNode(Renderable):
    """内联富文本组件。Aligns with OpenTUI TextNodeRenderable: add, clear, get_children, fg, bg, attributes, link."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        raw = options.get("spans", options.get("content", ""))
        if isinstance(raw, str):
            self._spans: list[Span] = [Span(text=raw)] if raw else []
        else:
            self._spans = _normalize_spans(list(raw))
        self._default_fg = parse_color_to_tuple(options.get("fg", "#ffffff"))
        self._default_bg = parse_color_to_tuple(options.get("bg", "transparent"))
        attrs = options.get("attributes", 0)
        self._attributes = attrs if isinstance(attrs, int) else 0
        self._link: dict[str, str] | None = options.get("link")

    @property
    def fg(self):
        return self._default_fg

    @fg.setter
    def fg(self, value) -> None:
        self._default_fg = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple("#ffffff")
        self.request_render()

    @property
    def bg(self):
        return self._default_bg

    @bg.setter
    def bg(self, value) -> None:
        self._default_bg = parse_color_to_tuple(value) if value is not None else parse_color_to_tuple("transparent")
        self.request_render()

    @property
    def attributes(self) -> int:
        return self._attributes

    @attributes.setter
    def attributes(self, value: int) -> None:
        self._attributes = int(value)
        self.request_render()

    @property
    def link(self) -> dict[str, str] | None:
        return self._link

    @link.setter
    def link(self, value: dict[str, str] | None) -> None:
        self._link = value
        self.request_render()

    def add(self, obj: Span | str, index: int | None = None) -> int:
        """Align with OpenTUI add(obj, index?). Accepts Span or str."""
        span = obj if isinstance(obj, Span) else Span(text=obj)
        if index is not None:
            self._spans.insert(index, span)
            self.request_render()
            return index
        self._spans.append(span)
        self.request_render()
        return len(self._spans) - 1

    def clear(self) -> None:
        """Align with OpenTUI clear()."""
        self._spans.clear()
        self.request_render()

    def get_children(self) -> list[Span]:
        """Align with OpenTUI getChildren(). Returns list of Span (pytui uses spans, not nested TextNode)."""
        return list(self._spans)

    def set_spans(self, spans: list[Span | str]) -> None:
        self._spans = _normalize_spans(spans)
        self.request_render()

    def set_content(self, content: str) -> None:
        self._spans = [Span(text=content)] if content else []
        self.request_render()

    def _chunks(
        self,
    ) -> list[tuple[str, ColorTuple, ColorTuple, bool, bool, bool, bool, bool, bool, bool]]:
        """扁平化为 (char, fg, bg, bold, italic, underline, strikethrough, dim, reverse, blink) 序列，\\n 单独。"""
        result: list[
            tuple[str, ColorTuple, ColorTuple, bool, bool, bool, bool, bool, bool, bool]
        ] = []
        for span in self._spans:
            fg = span.fg if span.fg is not None else self._default_fg
            bg = span.bg if span.bg is not None else self._default_bg
            for c in span.text:
                result.append(
                    (
                        c,
                        fg,
                        bg,
                        span.bold,
                        span.italic,
                        span.underline,
                        span.strikethrough,
                        span.dim,
                        span.reverse,
                        span.blink,
                    )
                )
        return result

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        chunks = self._chunks()
        x, y = 0, 0
        for (
            char,
            fg,
            bg,
            bold_,
            italic_,
            underline_,
            strikethrough_,
            dim_,
            reverse_,
            blink_,
        ) in chunks:
            if char == "\n":
                x = 0
                y += 1
                if y >= self.height:
                    break
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
                    char=char,
                    fg=fg,
                    bg=bg,
                    bold=bold_,
                    italic=italic_,
                    underline=underline_,
                    strikethrough=strikethrough_,
                    dim=dim_,
                    reverse=reverse_,
                    blink=blink_,
                ),
            )
            x += 1
