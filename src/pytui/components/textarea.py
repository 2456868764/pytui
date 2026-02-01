# pytui.components.textarea - aligns with OpenTUI TextareaRenderable (Textarea.ts):
# placeholder, initial_value, backgroundColor, textColor, focusedBackgroundColor, focusedTextColor, onSubmit.

from typing import Any, Callable

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple
from pytui.lib.extmarks import ExtmarksStore

DEFAULT_TEXTAREA_KEY_BINDINGS = {
    "move-left": "left",
    "move-right": "right",
    "move-up": "up",
    "move-down": "down",
    "move-line-start": "home",
    "move-line-end": "end",
    "line-home": "ctrl+a",
    "line-end": "ctrl+e",
    "buffer-home": "home",
    "buffer-end": "end",
    "move-buffer-start": "ctrl+home",
    "move-buffer-end": "ctrl+end",
    "delete-backward": "backspace",
    "delete-forward": "delete",
    "backspace": "backspace",
    "delete": "delete",
    "newline": "return",
    "page-up": "page_up",
    "page-down": "page_down",
    "undo": "ctrl+z",
    "redo": "ctrl+shift+z",
    "submit": "ctrl+return",
}


class Textarea(Renderable):
    """多行文本。Aligns with OpenTUI TextareaRenderable: placeholder, initial_value,
    backgroundColor, textColor, focusedBackgroundColor, focusedTextColor, onSubmit."""

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        initial = options.get("initial_value", options.get("initialValue", options.get("content", "")))
        self.content = initial
        self.scroll_y = 0
        self.buffer = options.get("buffer")
        self.editor_view = options.get("editor_view")
        self._placeholder: str | None = options.get("placeholder")
        self._on_submit: Callable[[], None] | None = options.get("on_submit", options.get("onSubmit"))

        self.fg = parse_color_to_tuple(options.get("fg", options.get("textColor", "#ffffff")))
        self.bg = parse_color_to_tuple(options.get("bg", options.get("backgroundColor", "transparent")))
        foc_fg = options.get("focused_text_color", options.get("focusedTextColor"))
        self._focused_fg = parse_color_to_tuple(foc_fg) if isinstance(foc_fg, str) else (foc_fg if foc_fg is not None else self.fg)
        foc_bg = options.get("focused_background_color", options.get("focusedBackgroundColor"))
        self._focused_bg = parse_color_to_tuple(foc_bg) if isinstance(foc_bg, str) else (foc_bg if foc_bg is not None else self.bg)
        self.selection_bg = parse_color_to_tuple(options.get("selection_bg", "#4444aa"))
        self.cursor_fg = parse_color_to_tuple(options.get("cursor_fg", "#000000"))
        self.cursor_bg = parse_color_to_tuple(options.get("cursor_bg", "#ffffff"))
        self._key_bindings = {
            **DEFAULT_TEXTAREA_KEY_BINDINGS,
            **options.get("key_bindings", options.get("keyBindings") or {}),
        }
        self.extmarks_store: ExtmarksStore | None = options.get("extmarks_store", options.get("extmarksStore"))
        self.extmark_style_map: dict[int, dict[str, Any]] = (
            options.get("extmark_style_map") or options.get("extmarkStyleMap") or {}
        )
        self.syntax_language: str | None = options.get("syntax_language", options.get("syntaxLanguage"))
        self.syntax_theme: str = options.get("syntax_theme", options.get("syntaxTheme", "default"))

        if self.editor_view and initial:
            try:
                self.editor_view.buffer.set_text(initial)
            except Exception:
                pass

    def _get_lines(self) -> list[str]:
        if self.editor_view is not None:
            return self.editor_view.get_visible_lines()
        if self.buffer is not None:
            lines = self.buffer.get_lines()
            start = self.scroll_y
            end = min(start + self.height, len(lines))
            return lines[start:end]
        lines = self.content.split("\n")
        start = self.scroll_y
        end = min(start + self.height, len(lines))
        return lines[start:end]

    def _get_start_line(self) -> int:
        if self.editor_view is not None:
            return self.editor_view.scroll_y
        return self.scroll_y

    def _key_id(self, key: dict) -> str:
        parts = []
        if key.get("ctrl"):
            parts.append("ctrl")
        if key.get("shift"):
            parts.append("shift")
        name = key.get("name") or key.get("char") or ""
        if name:
            parts.append(name.lower() if len(name) == 1 else name)
        return "+".join(parts) if parts else ""

    def _action_for_key(self, key: dict) -> str | None:
        kid = self._key_id(key)
        for action, bound in self._key_bindings.items():
            if bound and bound.lower() == kid:
                return action
        return None

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if not self.focused:
            return
        if self.editor_view is None:
            name = key.get("name") or key.get("char")
            if name == "up":
                self.scroll_up()
                return
            if name == "down":
                self.scroll_down()
                return
            if name == "page_up":
                self.set_scroll_y(max(0, self._get_start_line() - self.height))
                self.request_render()
                return
            if name == "page_down":
                lines = (
                    self.content.split("\n")
                    if self.buffer is None
                    else (self.buffer.get_lines() if self.buffer else [])
                )
                max_scroll = max(0, len(lines) - self.height)
                self.set_scroll_y(min(self._get_start_line() + self.height, max_scroll))
                self.request_render()
                return
            return
        ev = self.editor_view
        buf = ev.buffer
        name = key.get("name") or key.get("char")
        action = self._action_for_key(key)

        def do_move_left():
            if ev.cursor_pos > 0:
                ev.set_cursor(ev.cursor_pos - 1)
                ev.ensure_cursor_visible()

        def do_move_right():
            if ev.cursor_pos < len(buf.text):
                ev.set_cursor(ev.cursor_pos + 1)
                ev.ensure_cursor_visible()

        def do_move_up():
            line, col = ev.cursor_line, ev.cursor_col
            if line > 0:
                lines = buf.get_lines()
                ev.set_cursor_line_col(line - 1, min(col, len(lines[line - 1]) if line - 1 < len(lines) else 0))
                ev.ensure_cursor_visible()

        def do_move_down():
            lines = buf.get_lines()
            line, col = ev.cursor_line, ev.cursor_col
            if line < len(lines) - 1:
                ev.set_cursor_line_col(line + 1, min(col, len(lines[line + 1]) if line + 1 < len(lines) else 0))
                ev.ensure_cursor_visible()

        def do_line_start():
            ev.set_cursor_line_col(ev.cursor_line, 0)
            ev.ensure_cursor_visible()

        def do_line_end():
            line = ev.cursor_line
            lines = buf.get_lines()
            col = len(lines[line]) if line < len(lines) else 0
            ev.set_cursor_line_col(line, col)
            ev.ensure_cursor_visible()

        def do_buffer_start():
            ev.set_cursor(0)
            ev.ensure_cursor_visible()

        def do_buffer_end():
            ev.set_cursor(len(buf.text))
            ev.ensure_cursor_visible()

        if action == "move-left" or name == "left":
            do_move_left()
            return
        if action == "move-right" or name == "right":
            do_move_right()
            return
        if action == "move-up" or name == "up":
            do_move_up()
            return
        if action == "move-down" or name == "down":
            do_move_down()
            return
        if action == "move-line-start" or name == "home":
            do_line_start()
            return
        if action == "move-line-end" or name == "end":
            do_line_end()
            return
        if action == "move-buffer-start":
            do_buffer_start()
            return
        if action == "move-buffer-end":
            do_buffer_end()
            return
        if action == "delete-backward" or name == "backspace" or key.get("char") in ("\x08", "\x7f"):
            ev.delete_backward()
            self.request_render()
            return
        if action == "delete-forward" or name == "delete":
            ev.delete_forward()
            self.request_render()
            return
        if action == "page-up" or name == "page_up":
            ev.scroll_y = max(0, ev.scroll_y - ev.view_height)
            self.request_render()
            return
        if action == "page-down" or name == "page_down":
            ev.scroll_y = min(
                max(0, buf.line_count - ev.view_height),
                ev.scroll_y + ev.view_height,
            )
            self.request_render()
            return
        if action == "undo" or (name == "z" and key.get("ctrl")):
            if ev.undo():
                self.request_render()
            return
        if action == "redo":
            if ev.redo():
                self.request_render()
            return
        if action == "submit":
            if self._on_submit:
                self._on_submit()
            return
        ch = key.get("char")
        if ch and len(ch) == 1 and ch.isprintable():
            ev.insert(ch)
            self.request_render()

    def set_content(self, content: str) -> None:
        if self.content != content:
            self.content = content
            self.request_render()

    def set_scroll_y(self, y: int) -> None:
        if self.editor_view is not None:
            self.editor_view.scroll_y = y
        else:
            lines = self.content.split("\n") if self.buffer is None else self.buffer.get_lines()
            max_scroll = max(0, len(lines) - self.height)
            self.scroll_y = min(max(0, y), max_scroll)
        self.request_render()

    def scroll_down(self) -> None:
        if self.editor_view is not None:
            ev = self.editor_view
            ev.scroll_y = min(
                ev.scroll_y + 1,
                max(0, ev.buffer.line_count - self.height),
            )
        else:
            self.set_scroll_y(self._get_start_line() + 1)
        self.request_render()

    def scroll_up(self) -> None:
        if self.editor_view is not None:
            ev = self.editor_view
            ev.scroll_y = max(0, ev.scroll_y - 1)
        else:
            self.set_scroll_y(self._get_start_line() - 1)
        self.request_render()

    def undo(self) -> bool:
        if self.editor_view is not None:
            return self.editor_view.undo()
        if self.buffer is not None:
            return self.buffer.undo()
        return False

    def redo(self) -> bool:
        if self.editor_view is not None:
            return self.editor_view.redo()
        if self.buffer is not None:
            return self.buffer.redo()
        return False

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        if self.editor_view is not None:
            self.editor_view.view_width = self.width
            self.editor_view.view_height = self.height
        lines = self._get_lines()
        start_line = self._get_start_line()
        sel = self.editor_view.get_selection_range() if self.editor_view else None
        cursor_line = self.editor_view.cursor_line - start_line if self.editor_view else -1
        cursor_col = self.editor_view.cursor_col if self.editor_view else -1
        store = self.extmarks_store
        style_map = self.extmark_style_map
        syntax_lang = self.syntax_language
        syntax_theme_map = None
        if syntax_lang:
            try:
                from pytui.core.syntax_style import get_theme_scope_colors

                syntax_theme_map = get_theme_scope_colors(self.syntax_theme)
            except Exception:
                syntax_lang = None

        use_fg = self._focused_fg if self.focused else self.fg
        use_bg = self._focused_bg if self.focused else self.bg
        for dy in range(self.height):
            line_idx = start_line + dy
            if dy >= len(lines):
                line = ""
            else:
                line = lines[dy]
            line_fg_by_col: list[tuple[int, int, int, int]] = [use_fg] * max(self.width, 1)
            if syntax_lang and syntax_theme_map:
                try:
                    from pytui.lib.tree_sitter import highlight as syntax_highlight

                    tokens = syntax_highlight(line, syntax_lang)
                    col = 0
                    for text, token_type in tokens:
                        fg = syntax_theme_map.get(token_type, syntax_theme_map.get("plain", self.fg))
                        for c in range(col, min(col + len(text), self.width)):
                            line_fg_by_col[c] = fg
                        col += len(text)
                except Exception:
                    pass
            for dx in range(self.width):
                ch = line[dx] if dx < len(line) else " "
                fg, bg = line_fg_by_col[dx], use_bg
                pos = self.editor_view.buffer.line_col_to_pos(line_idx, dx) if self.editor_view else None
                if sel is not None and pos is not None and sel[0] <= pos < sel[1]:
                    bg = self.selection_bg
                if cursor_line == dy and cursor_col == dx and self.editor_view is not None:
                    fg, bg = self.cursor_fg, self.cursor_bg
                if store is not None and pos is not None and self.editor_view is not None:
                    marks = store.get_in_range(pos, pos + 1)
                    if marks:
                        m = marks[0]
                        style = style_map.get(m.style_id or 0, {})
                        if style.get("fg"):
                            fg = parse_color_to_tuple(style["fg"])
                        if style.get("bg"):
                            bg = parse_color_to_tuple(style["bg"])
                buffer.set_cell(
                    self.x + dx,
                    self.y + dy,
                    Cell(char=ch, fg=fg, bg=bg),
                )
