# pytui.react.text_components - span, br, b, strong, i, em, u, a (aligns OpenTUI components/text.ts)

from __future__ import annotations

from typing import Any

from pytui.components.text_node import Span
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple

# Text node keys: must be created inside a text node (aligns OpenTUI textNodeKeys)
TEXT_NODE_KEYS = ("span", "br", "b", "strong", "i", "em", "u", "a")


def _options_to_span(
    options: dict,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    href: str | None = None,
) -> Span:
    content = options.get("content", options.get("children", ""))
    if isinstance(content, list):
        content = "".join(str(c) for c in content if isinstance(c, str))
    text = str(content) if content else ""
    fg = options.get("fg")
    bg = options.get("bg")
    if fg is not None:
        fg = parse_color_to_tuple(fg)
    if bg is not None:
        bg = parse_color_to_tuple(bg)
    return Span(text=text, fg=fg, bg=bg, bold=bold, italic=italic, underline=underline, href=href or options.get("href"))


class SpanRenderable(Renderable):
    """Inline span inside <text>. Aligns OpenTUI SpanRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._span = _options_to_span(options)

    def get_span(self) -> Span:
        return self._span

    def render_self(self, buffer: Any) -> None:
        pass  # Parent Text renders from get_span()


class BoldSpanRenderable(SpanRenderable):
    """Bold span (<b> / <strong>). Aligns OpenTUI BoldSpanRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._span = _options_to_span(options, bold=True)


class ItalicSpanRenderable(SpanRenderable):
    """Italic span (<i> / <em>). Aligns OpenTUI ItalicSpanRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._span = _options_to_span(options, italic=True)


class UnderlineSpanRenderable(SpanRenderable):
    """Underline span (<u>). Aligns OpenTUI UnderlineSpanRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._span = _options_to_span(options, underline=True)


class LineBreakRenderable(SpanRenderable):
    """Line break (<br>). Aligns OpenTUI LineBreakRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._span = Span(text="\n")

    def get_span(self) -> Span:
        return self._span


class LinkRenderable(SpanRenderable):
    """Link span (<a href="...">). Aligns OpenTUI LinkRenderable."""

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        self._span = _options_to_span(options, href=options.get("href", ""))


class TextChunkRenderable(Renderable):
    """Raw text instance inside <text> (from createTextInstance). Not in catalogue."""

    def __init__(self, ctx: Any, text: str) -> None:
        super().__init__(ctx, {"id": getattr(ctx, "id", "text-chunk")})
        self._text = text

    def get_span(self) -> Span:
        return Span(text=self._text)

    def render_self(self, buffer: Any) -> None:
        pass
