# pytui.components.text_node - 内联富文本：TextNode、Span、Bold/Italic/Underline/LineBreak、Link
#
# Link 支持：使用 link(text, url, fg?, bg?) 创建带 href 的 Span，在 TextNode 中按行渲染；
# Span.href 为 URL，样式与普通 Span 相同，可设 fg/bg/underline 等。点击或键盘激活链接
# 由上层（焦点管理、keypress 处理）根据 href 处理；本组件仅负责渲染。
#

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable

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
    href: str | None = None  # 可选 Link

    def __post_init__(self) -> None:
        if self.fg is not None and isinstance(self.fg, str):
            self.fg = parse_color(self.fg)
        if self.bg is not None and isinstance(self.bg, str):
            self.bg = parse_color(self.bg)


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


def _normalize_spans(spans: list[Span | str]) -> list[Span]:
    out: list[Span] = []
    for s in spans:
        if isinstance(s, str):
            out.append(Span(text=s))
        else:
            out.append(s)
    return out


class TextNode(Renderable):
    """内联富文本组件：由 Span 列表（含 Bold/Italic/Underline/LineBreak/Link）组成，按行渲染。"""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        raw = options.get("spans", options.get("content", ""))
        if isinstance(raw, str):
            self._spans: list[Span] = [Span(text=raw)] if raw else []
        else:
            self._spans = _normalize_spans(list(raw))
        self._default_fg = parse_color(options.get("fg", "#ffffff"))
        self._default_bg = parse_color(options.get("bg", "transparent"))

    def set_spans(self, spans: list[Span | str]) -> None:
        self._spans = _normalize_spans(spans)
        self.request_render()

    def set_content(self, content: str) -> None:
        self._spans = [Span(text=content)] if content else []
        self.request_render()

    def _chunks(self) -> list[tuple[str, ColorTuple, ColorTuple, bool, bool, bool]]:
        """扁平化为 (char, fg, bg, bold, italic, underline) 序列，\n 单独。"""
        result: list[tuple[str, ColorTuple, ColorTuple, bool, bool, bool]] = []
        for span in self._spans:
            fg = span.fg if span.fg is not None else self._default_fg
            bg = span.bg if span.bg is not None else self._default_bg
            for c in span.text:
                result.append((c, fg, bg, span.bold, span.italic, span.underline))
        return result

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        chunks = self._chunks()
        x, y = 0, 0
        for char, fg, bg, bold_, italic_, underline_ in chunks:
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
                Cell(char=char, fg=fg, bg=bg, bold=bold_, italic=italic_, underline=underline_),
            )
            x += 1
