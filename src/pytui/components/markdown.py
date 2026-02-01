# pytui.components.markdown - Aligns with OpenTUI packages/core/src/renderables/Markdown.ts
# MarkdownRenderable: content, syntaxStyle, conceal, streaming, clearCache, renderSelf.
# PyTUI: minimal stub - renders content as single Text block (full markdown parsing 待后续).

from __future__ import annotations

from typing import Any

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.components.text import Text


class MarkdownRenderable(Renderable):
    """Markdown renderable. API aligns OpenTUI MarkdownRenderable; content rendered as single Text block."""

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        super().__init__(ctx, {**options, "flex_direction": "column"})
        self._content = options.get("content", "")
        self._syntax_style = options.get("syntax_style", options.get("syntaxStyle"))
        self._conceal = options.get("conceal", True)
        self._streaming = options.get("streaming", False)
        self._block_children: list[Renderable] = []
        self._update_blocks()

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        if self._content != value:
            self._content = value
            self._update_blocks()
            self.request_render()

    @property
    def syntax_style(self) -> Any:
        return self._syntax_style

    @syntax_style.setter
    def syntax_style(self, value: Any) -> None:
        if self._syntax_style != value:
            self._syntax_style = value
            self.request_render()

    @property
    def conceal(self) -> bool:
        return self._conceal

    @conceal.setter
    def conceal(self, value: bool) -> None:
        if self._conceal != value:
            self._conceal = value
            self.request_render()

    @property
    def streaming(self) -> bool:
        return self._streaming

    @streaming.setter
    def streaming(self, value: bool) -> None:
        if self._streaming != value:
            self._streaming = value
            self._update_blocks()
            self.request_render()

    def _update_blocks(self) -> None:
        for child in self._block_children:
            self.remove(child)
        self._block_children.clear()
        if not self._content.strip():
            return
        text_child = Text(self.ctx, {"content": self._content, "width": "100%"})
        self.add(text_child)
        self._block_children.append(text_child)

    def clear_cache(self) -> None:
        self._update_blocks()
        self.request_render()

    def render_self(self, buffer: OptimizedBuffer, delta_time: float = 0.0) -> None:
        # Children (Text block) rendered by Renderable.render()
        pass
