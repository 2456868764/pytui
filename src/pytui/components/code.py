# pytui.components.code - Aligns with OpenTUI packages/core/src/renderables/Code.ts
# Aligns with OpenTUI CodeRenderable (Code.ts) and TextBufferOptions: all properties, behavior, and API.

from __future__ import annotations

from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple
from pytui.core.syntax_style import get_theme_scope_colors
from pytui.lib.tree_sitter import highlight as syntax_highlight


# Default options matching OpenTUI Code.ts _contentDefaultOptions
_CONTENT_DEFAULT_OPTIONS = {
    "content": "",
    "conceal": True,
    "draw_unstyled_text": True,
    "streaming": False,
}


class Code(Renderable):
    """Code block: syntax highlight. Aligns with OpenTUI CodeRenderable (Code.ts) and TextBufferOptions.

    CodeOptions (snake_case; camelCase accepted):
    - content, filetype (alias language), syntax_style (alias theme), conceal, draw_unstyled_text, streaming,
    - tree_sitter_client (optional; pytui uses syntax.highlighter when absent).
    TextBufferOptions: fg, bg, selection_bg, selection_fg, selectable, wrap_mode, tab_indicator, tab_indicator_color.
    Read-only: is_highlighting.
    """

    def __init__(self, ctx: Any, options: dict[str, Any] | None = None) -> None:
        options = options or {}
        opts = dict(options)
        for camel, snake in [
            ("syntaxStyle", "syntax_style"),
            ("drawUnstyledText", "draw_unstyled_text"),
            ("treeSitterClient", "tree_sitter_client"),
            ("wrapMode", "wrap_mode"),
            ("selectionBg", "selection_bg"),
            ("selectionFg", "selection_fg"),
            ("tabIndicator", "tab_indicator"),
            ("tabIndicatorColor", "tab_indicator_color"),
        ]:
            if camel in opts and snake not in opts:
                opts[snake] = opts[camel]
        super().__init__(ctx, opts)

        # Code.ts state
        self._content: str = opts.get("content", _CONTENT_DEFAULT_OPTIONS["content"])
        self._filetype: str | None = opts.get("filetype", opts.get("language"))
        self._syntax_style: str = opts.get("syntax_style", opts.get("theme", "default"))
        self._conceal: bool = opts.get("conceal", _CONTENT_DEFAULT_OPTIONS["conceal"])
        self._draw_unstyled_text: bool = opts.get(
            "draw_unstyled_text", _CONTENT_DEFAULT_OPTIONS["draw_unstyled_text"]
        )
        self._streaming: bool = opts.get("streaming", _CONTENT_DEFAULT_OPTIONS["streaming"])
        self._tree_sitter_client: Any = opts.get("tree_sitter_client")
        self._is_highlighting: bool = False
        self._highlights_dirty: bool = len(self._content) > 0
        self._highlight_snapshot_id: int = 0
        self._should_render_text_buffer: bool = True
        self._had_initial_content: bool = False
        self._last_highlights: list[list[tuple[str, str]]] = []  # per-line [(text, token_type), ...]

        if self._content:
            self._should_render_text_buffer = self._draw_unstyled_text or not self._filetype

        # TextBufferOptions (from TextBufferRenderable)
        self._default_fg = parse_color_to_tuple(opts.get("fg", "#cccccc"))
        self._default_bg = parse_color_to_tuple(opts.get("bg", "transparent"))
        self._selection_bg = parse_color_to_tuple(opts.get("selection_bg")) if opts.get("selection_bg") is not None else None
        self._selection_fg = parse_color_to_tuple(opts.get("selection_fg")) if opts.get("selection_fg") is not None else None
        self._selectable: bool = opts.get("selectable", True)
        self._wrap_mode: str = opts.get("wrap_mode", "word")
        self._tab_indicator: str | int | None = opts.get("tab_indicator")
        self._tab_indicator_color: tuple[int, int, int, int] | None = (
            parse_color_to_tuple(opts.get("tab_indicator_color")) if opts.get("tab_indicator_color") is not None else None
        )

        self._theme = get_theme_scope_colors(self._syntax_style)

    # --- content (Code.ts) ---
    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        if self._content != value:
            self._content = value
            self._highlights_dirty = True
            self._highlight_snapshot_id += 1
            if self._streaming and not self._draw_unstyled_text and self._filetype:
                return
            self._update_text_info()

    # --- filetype (Code.ts); language alias ---
    @property
    def filetype(self) -> str | None:
        return self._filetype

    @filetype.setter
    def filetype(self, value: str | None) -> None:
        if self._filetype != value:
            self._filetype = value
            self._highlights_dirty = True
            self.request_render()

    @property
    def language(self) -> str | None:
        return self._filetype

    @language.setter
    def language(self, value: str | None) -> None:
        self.filetype = value

    # --- syntax_style (Code.ts) ---
    @property
    def syntax_style(self) -> str:
        return self._syntax_style

    @syntax_style.setter
    def syntax_style(self, value: str) -> None:
        if self._syntax_style != value:
            self._syntax_style = value
            self._theme = get_theme_scope_colors(value)
            self._highlights_dirty = True
            self.request_render()

    # --- conceal, draw_unstyled_text, streaming (Code.ts) ---
    @property
    def conceal(self) -> bool:
        return self._conceal

    @conceal.setter
    def conceal(self, value: bool) -> None:
        if self._conceal != value:
            self._conceal = value
            self._highlights_dirty = True
            self.request_render()

    @property
    def draw_unstyled_text(self) -> bool:
        return self._draw_unstyled_text

    @draw_unstyled_text.setter
    def draw_unstyled_text(self, value: bool) -> None:
        if self._draw_unstyled_text != value:
            self._draw_unstyled_text = value
            self._highlights_dirty = True
            self.request_render()

    @property
    def streaming(self) -> bool:
        return self._streaming

    @streaming.setter
    def streaming(self, value: bool) -> None:
        if self._streaming != value:
            self._streaming = value
            self._had_initial_content = False
            self._last_highlights = []
            self._highlights_dirty = True
            self.request_render()

    # --- tree_sitter_client (Code.ts) ---
    @property
    def tree_sitter_client(self) -> Any:
        return self._tree_sitter_client

    @tree_sitter_client.setter
    def tree_sitter_client(self, value: Any) -> None:
        if self._tree_sitter_client is not value:
            self._tree_sitter_client = value
            self._highlights_dirty = True
            self.request_render()

    # --- is_highlighting (Code.ts, read-only) ---
    @property
    def is_highlighting(self) -> bool:
        return self._is_highlighting

    # --- TextBufferOptions: fg, bg, selection_bg, selection_fg, wrap_mode, etc. ---
    @property
    def fg(self) -> tuple[int, int, int, int]:
        return self._default_fg

    @fg.setter
    def fg(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value)
        if self._default_fg != new_color:
            self._default_fg = new_color
            self.request_render()

    @property
    def bg(self) -> tuple[int, int, int, int]:
        return self._default_bg

    @bg.setter
    def bg(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value)
        if self._default_bg != new_color:
            self._default_bg = new_color
            self.request_render()

    @property
    def selection_bg(self) -> tuple[int, int, int, int] | None:
        return self._selection_bg

    @selection_bg.setter
    def selection_bg(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value) if value is not None else None
        if self._selection_bg != new_color:
            self._selection_bg = new_color
            self.request_render()

    @property
    def selection_fg(self) -> tuple[int, int, int, int] | None:
        return self._selection_fg

    @selection_fg.setter
    def selection_fg(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value) if value is not None else None
        if self._selection_fg != new_color:
            self._selection_fg = new_color
            self.request_render()

    @property
    def selectable(self) -> bool:
        return self._selectable

    @selectable.setter
    def selectable(self, value: bool) -> None:
        if self._selectable != value:
            self._selectable = value
            self.request_render()

    @property
    def wrap_mode(self) -> str:
        return self._wrap_mode

    @wrap_mode.setter
    def wrap_mode(self, value: str) -> None:
        if self._wrap_mode != value:
            self._wrap_mode = value
            self.request_render()

    @property
    def tab_indicator(self) -> str | int | None:
        return self._tab_indicator

    @tab_indicator.setter
    def tab_indicator(self, value: str | int | None) -> None:
        if self._tab_indicator != value:
            self._tab_indicator = value
            self.request_render()

    @property
    def tab_indicator_color(self) -> tuple[int, int, int, int] | None:
        return self._tab_indicator_color

    @tab_indicator_color.setter
    def tab_indicator_color(self, value: Any) -> None:
        new_color = parse_color_to_tuple(value) if value is not None else None
        if self._tab_indicator_color != new_color:
            self._tab_indicator_color = new_color
            self.request_render()

    def _update_text_info(self) -> None:
        """Mirror TextBufferRenderable.updateTextInfo(): request re-layout and render."""
        self.request_render()

    def _ensure_visible_text_before_highlight(self) -> None:
        """Mirror Code.ts ensureVisibleTextBeforeHighlight()."""
        if not self._filetype:
            self._should_render_text_buffer = True
            return
        is_initial_content = self._streaming and not self._had_initial_content
        should_draw_unstyled_now = (
            (is_initial_content and self._draw_unstyled_text) if self._streaming else self._draw_unstyled_text
        )
        if self._streaming and not is_initial_content:
            self._should_render_text_buffer = True
        elif should_draw_unstyled_now:
            self._should_render_text_buffer = True
        else:
            self._should_render_text_buffer = False

    def _start_highlight(self) -> None:
        """Mirror Code.ts startHighlight(); sync version using syntax_highlight (or tree_sitter_client if async)."""
        content = self._content
        filetype = self._filetype
        snapshot_id = self._highlight_snapshot_id + 1
        self._highlight_snapshot_id = snapshot_id

        if not filetype:
            self._highlights_dirty = False
            self._should_render_text_buffer = True
            return

        if self._streaming and not self._had_initial_content:
            self._had_initial_content = True
        self._is_highlighting = True

        try:
            lines = content.split("\n")
            self._last_highlights = [
                syntax_highlight(line, filetype) for line in lines
            ]
            if snapshot_id != self._highlight_snapshot_id:
                return
            self._should_render_text_buffer = True
            self._is_highlighting = False
            self._highlights_dirty = False
            self._update_text_info()
            self.request_render()
        except Exception:  # noqa: BLE001
            if snapshot_id != self._highlight_snapshot_id:
                return
            self._last_highlights = []
            self._should_render_text_buffer = True
            self._is_highlighting = False
            self._highlights_dirty = False
            self._update_text_info()
            self.request_render()

    def get_line_highlights(self, line_idx: int) -> list[tuple[str, str]]:
        """Return list of (text, token_type) for the given line. Aligns with OpenTUI getLineHighlights(lineIdx)."""
        lines = self._content.split("\n")
        if line_idx < 0 or line_idx >= len(lines):
            return []
        if line_idx < len(self._last_highlights):
            return list(self._last_highlights[line_idx])
        return syntax_highlight(lines[line_idx], self._filetype or "plain")

    def render_self(self, buffer: OptimizedBuffer) -> None:
        """Mirror Code.ts renderSelf(): handle _highlightsDirty then draw when _shouldRenderTextBuffer."""
        if self._highlights_dirty:
            if self._content == "":
                self._should_render_text_buffer = False
                self._highlights_dirty = False
            elif not self._filetype:
                self._should_render_text_buffer = True
                self._highlights_dirty = False
            else:
                self._ensure_visible_text_before_highlight()
                self._highlights_dirty = False
                self._start_highlight()

        if not self._should_render_text_buffer:
            return

        lines = self._content.split("\n")
        if self._last_highlights:
            display_lines = list(self._last_highlights)
            while len(display_lines) < len(lines):
                display_lines.append(syntax_highlight(lines[len(display_lines)], self._filetype or "plain"))
        else:
            display_lines = [syntax_highlight(line, self._filetype or "plain") for line in lines]

        theme = self._theme
        fg_default = self._default_fg
        bg_default = self._default_bg

        for dy, spans in enumerate(display_lines):
            if dy >= self.height:
                break
            col = 0
            for text, token_type in spans:
                color = theme.get(token_type, theme.get("plain", fg_default))
                for ch in text:
                    if col >= self.width:
                        break
                    buffer.set_cell(
                        self.x + col,
                        self.y + dy,
                        Cell(char=ch, fg=color, bg=bg_default),
                    )
                    col += 1
            for c in range(col, self.width):
                buffer.set_cell(
                    self.x + c,
                    self.y + dy,
                    Cell(char=" ", fg=fg_default, bg=bg_default),
                )
