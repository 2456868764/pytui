# pytui.components.diff - Aligns with OpenTUI packages/core/src/renderables/Diff.ts
# Full alignment with OpenTUI DiffRenderable (Diff.ts): diff, view, parse error view,
# unified/split view, hunks with line numbers, syntax highlight, wrap_mode, all property setters, destroy_recursively.

from __future__ import annotations

from typing import Optional

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.renderable import Renderable
from pytui.lib import parse_color_to_tuple
from pytui.core.syntax_style import get_theme_scope_colors
from pytui.lib.tree_sitter import highlight as syntax_highlight
from pytui.utils.diff import (
    ParsedPatch,
    build_split_logical_lines,
    diff_lines,
    flattened_unified_lines,
    parse_patch,
    parse_unified_diff,
)


class Diff(Renderable):
    """Diff view: unified diff string or old/new text. Full alignment with OpenTUI DiffRenderable.

    OpenTUI Diff.ts: diff, view (unified|split), parse error view, hunks with line numbers,
    split view (left removed / right added), syntax highlight (filetype/syntax_style),
    wrap_mode (word|char|none), all styling options and property setters, destroy_recursively.
    """

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        opts = dict(options)
        for camel, snake in [
            ("syntaxStyle", "syntax_style"),
            ("wrapMode", "wrap_mode"),
            ("showLineNumbers", "show_line_numbers"),
            ("lineNumberFg", "line_number_fg"),
            ("lineNumberBg", "line_number_bg"),
            ("addedBg", "added_bg"),
            ("removedBg", "removed_bg"),
            ("contextBg", "context_bg"),
            ("addedContentBg", "added_content_bg"),
            ("removedContentBg", "removed_content_bg"),
            ("contextContentBg", "context_content_bg"),
            ("addedSignColor", "added_sign_color"),
            ("removedSignColor", "removed_sign_color"),
            ("addedLineNumberBg", "added_line_number_bg"),
            ("removedLineNumberBg", "removed_line_number_bg"),
            ("selectionBg", "selection_bg"),
            ("selectionFg", "selection_fg"),
            ("treeSitterClient", "tree_sitter_client"),
        ]:
            if camel in opts and snake not in opts:
                opts[snake] = opts[camel]
        super().__init__(ctx, opts)

        self._diff_raw: str = opts.get("diff", "")
        self.old_text = opts.get("old_text", "")
        self.new_text = opts.get("new_text", "")
        self._view: str = opts.get("view", "unified")
        self._parse_error: Optional[str] = None
        self._parsed_patch: Optional[ParsedPatch] = None
        self._ensure_parsed()

        # Line backgrounds (OpenTUI defaults)
        self._added_bg = parse_color_to_tuple(opts.get("added_bg", opts.get("add_bg", "#1a4d1a")))
        self._removed_bg = parse_color_to_tuple(opts.get("removed_bg", opts.get("del_bg", "#4d1a1a")))
        self._context_bg = parse_color_to_tuple(opts.get("context_bg", opts.get("bg", "transparent")))
        self._added_content_bg = parse_color_to_tuple(opts.get("added_content_bg")) if opts.get("added_content_bg") else None
        self._removed_content_bg = parse_color_to_tuple(opts.get("removed_content_bg")) if opts.get("removed_content_bg") else None
        self._context_content_bg = parse_color_to_tuple(opts.get("context_content_bg")) if opts.get("context_content_bg") else None

        self._added_sign_color = parse_color_to_tuple(opts.get("added_sign_color", opts.get("add_fg", "#22c55e")))
        self._removed_sign_color = parse_color_to_tuple(opts.get("removed_sign_color", opts.get("del_fg", "#ef4444")))
        self._add_fg = parse_color_to_tuple(opts.get("add_fg", "#00ff00"))
        self._del_fg = parse_color_to_tuple(opts.get("del_fg", "#ff0000"))
        self._ctx_fg = parse_color_to_tuple(opts.get("context_fg", opts.get("fg", "#ffffff")))
        self._fg = parse_color_to_tuple(opts.get("fg", "#cccccc"))

        self._line_number_fg = parse_color_to_tuple(opts.get("line_number_fg", "#888888"))
        self._line_number_bg = parse_color_to_tuple(opts.get("line_number_bg", "transparent"))
        self._added_line_number_bg = parse_color_to_tuple(opts.get("added_line_number_bg", "transparent"))
        self._removed_line_number_bg = parse_color_to_tuple(opts.get("removed_line_number_bg", "transparent"))

        self._show_line_numbers = opts.get("show_line_numbers", True)
        self._filetype = opts.get("filetype", opts.get("language", ""))
        self._syntax_style = opts.get("syntax_style", opts.get("theme", "default"))
        self._wrap_mode = opts.get("wrap_mode", "none")
        self._conceal = opts.get("conceal", False)
        self._selection_bg = parse_color_to_tuple(opts.get("selection_bg")) if opts.get("selection_bg") else None
        self._selection_fg = parse_color_to_tuple(opts.get("selection_fg")) if opts.get("selection_fg") else None
        self._tree_sitter_client = opts.get("tree_sitter_client")
        self._theme = get_theme_scope_colors(self._syntax_style)

    def _ensure_parsed(self) -> None:
        if not self._diff_raw:
            self._parse_error = None
            self._parsed_patch = None
            return
        patch, err = parse_patch(self._diff_raw)
        self._parsed_patch = patch
        # Fallback: no @@ hunks (e.g. simple "+a\n-b") -> use line-by-line, no error view
        self._parse_error = None if (err == "No valid hunks found") else err

    # --- Property getters/setters (all trigger request_render where OpenTUI rebuildView) ---
    @property
    def diff(self) -> str:
        return self._diff_raw

    @diff.setter
    def diff(self, value: str) -> None:
        if self._diff_raw != value:
            self._diff_raw = value
            self._ensure_parsed()
            self.request_render()

    @property
    def view(self) -> str:
        return self._view

    @view.setter
    def view(self, value: str) -> None:
        if self._view != value and value in ("unified", "split"):
            self._view = value
            self.request_render()

    def set_texts(self, old_text: str, new_text: str) -> None:
        if self.old_text != old_text or self.new_text != new_text:
            self.old_text = old_text
            self.new_text = new_text
            self._diff_raw = ""
            self._ensure_parsed()
            self.request_render()

    @property
    def added_bg(self):
        return self._added_bg

    @added_bg.setter
    def added_bg(self, value):
        p = parse_color_to_tuple(value)
        if self._added_bg != p:
            self._added_bg = p
            self.request_render()

    @property
    def removed_bg(self):
        return self._removed_bg

    @removed_bg.setter
    def removed_bg(self, value):
        p = parse_color_to_tuple(value)
        if self._removed_bg != p:
            self._removed_bg = p
            self.request_render()

    @property
    def context_bg(self):
        return self._context_bg

    @context_bg.setter
    def context_bg(self, value):
        p = parse_color_to_tuple(value)
        if self._context_bg != p:
            self._context_bg = p
            self.request_render()

    @property
    def added_sign_color(self):
        return self._added_sign_color

    @added_sign_color.setter
    def added_sign_color(self, value):
        p = parse_color_to_tuple(value)
        if self._added_sign_color != p:
            self._added_sign_color = p
            self.request_render()

    @property
    def removed_sign_color(self):
        return self._removed_sign_color

    @removed_sign_color.setter
    def removed_sign_color(self, value):
        p = parse_color_to_tuple(value)
        if self._removed_sign_color != p:
            self._removed_sign_color = p
            self.request_render()

    @property
    def show_line_numbers(self) -> bool:
        return self._show_line_numbers

    @show_line_numbers.setter
    def show_line_numbers(self, value: bool) -> None:
        if self._show_line_numbers != value:
            self._show_line_numbers = value
            self.request_render()

    @property
    def line_number_fg(self):
        return self._line_number_fg

    @line_number_fg.setter
    def line_number_fg(self, value):
        p = parse_color_to_tuple(value)
        if self._line_number_fg != p:
            self._line_number_fg = p
            self.request_render()

    @property
    def line_number_bg(self):
        return self._line_number_bg

    @line_number_bg.setter
    def line_number_bg(self, value):
        p = parse_color_to_tuple(value)
        if self._line_number_bg != p:
            self._line_number_bg = p
            self.request_render()

    @property
    def filetype(self) -> str:
        return self._filetype

    @filetype.setter
    def filetype(self, value: str) -> None:
        if self._filetype != value:
            self._filetype = value
            self.request_render()

    @property
    def syntax_style(self) -> str:
        return self._syntax_style

    @syntax_style.setter
    def syntax_style(self, value: str) -> None:
        if self._syntax_style != value:
            self._syntax_style = value
            self._theme = get_theme_scope_colors(value)
            self.request_render()

    @property
    def wrap_mode(self) -> str:
        return self._wrap_mode

    @wrap_mode.setter
    def wrap_mode(self, value: str) -> None:
        if self._wrap_mode != value and value in ("word", "char", "none"):
            self._wrap_mode = value
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
    def added_content_bg(self):
        return self._added_content_bg

    @added_content_bg.setter
    def added_content_bg(self, value):
        p = parse_color_to_tuple(value) if value else None
        if self._added_content_bg != p:
            self._added_content_bg = p
            self.request_render()

    @property
    def removed_content_bg(self):
        return self._removed_content_bg

    @removed_content_bg.setter
    def removed_content_bg(self, value):
        p = parse_color_to_tuple(value) if value else None
        if self._removed_content_bg != p:
            self._removed_content_bg = p
            self.request_render()

    @property
    def context_content_bg(self):
        return self._context_content_bg

    @context_content_bg.setter
    def context_content_bg(self, value):
        p = parse_color_to_tuple(value) if value else None
        if self._context_content_bg != p:
            self._context_content_bg = p
            self.request_render()

    @property
    def added_line_number_bg(self):
        return self._added_line_number_bg

    @added_line_number_bg.setter
    def added_line_number_bg(self, value):
        p = parse_color_to_tuple(value)
        if self._added_line_number_bg != p:
            self._added_line_number_bg = p
            self.request_render()

    @property
    def removed_line_number_bg(self):
        return self._removed_line_number_bg

    @removed_line_number_bg.setter
    def removed_line_number_bg(self, value):
        p = parse_color_to_tuple(value)
        if self._removed_line_number_bg != p:
            self._removed_line_number_bg = p
            self.request_render()

    @property
    def fg(self):
        return self._fg

    @fg.setter
    def fg(self, value):
        p = parse_color_to_tuple(value) if value else None
        if p is not None and self._fg != p:
            self._fg = p
            self.request_render()

    def destroy_recursively(self) -> None:
        """Aligns with OpenTUI destroyRecursively: clear state; remove children if any."""
        self._parse_error = None
        self._parsed_patch = None
        self.remove_all()

    def _line_bg(self, tag: str):
        if tag == "+":
            return self._added_content_bg or self._added_bg
        if tag == "-":
            return self._removed_content_bg or self._removed_bg
        return self._context_content_bg or self._context_bg

    def _line_fg(self, tag: str):
        if tag == "+":
            return self._added_sign_color
        if tag == "-":
            return self._removed_sign_color
        return self._ctx_fg

    def _wrap_line(self, text: str, width: int) -> list[str]:
        """Break line into visual rows. wrap_mode: none -> one row; word/char -> break at width."""
        if width <= 0 or self._wrap_mode == "none":
            return [text] if text else [""]
        out: list[str] = []
        while text:
            if len(text) <= width:
                out.append(text)
                break
            out.append(text[:width])
            text = text[width:]
        return out if out else [""]

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self._parse_error:
            self._render_error_view(buffer)
            return
        if self._view == "split" and self._parsed_patch:
            self._render_split_view(buffer)
            return
        self._render_unified_view(buffer)

    def _render_error_view(self, buffer: OptimizedBuffer) -> None:
        """Error message on first line(s), then raw diff. Aligns with OpenTUI buildErrorView."""
        err_msg = f"Error parsing diff: {self._parse_error}\n"
        content_lines = (err_msg + self._diff_raw).splitlines()
        row = 0
        for line in content_lines:
            if row >= self.height:
                break
            fg = self._removed_sign_color
            for x_off, ch in enumerate(line[: self.width]):
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg, bg=self._context_bg))
            for x_off in range(len(line), self.width):
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=" ", fg=fg, bg=self._context_bg))
            row += 1
        while row < self.height:
            for x_off in range(self.width):
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=" ", fg=self._fg, bg=self._context_bg))
            row += 1

    def _render_unified_view(self, buffer: OptimizedBuffer) -> None:
        # Build lines with optional line numbers from hunks
        if self._parsed_patch:
            flat = flattened_unified_lines(self._parsed_patch)
            lines_with_nums: list[tuple[str, str, Optional[int], Optional[int]]] = flat
        else:
            raw_list = diff_lines(self.old_text, self.new_text) if not self._diff_raw else parse_unified_diff(self._diff_raw)
            lines_with_nums = [(tag, content, None, None) for tag, content in raw_list]

        line_w = 0
        if self._show_line_numbers and lines_with_nums:
            max_num = max(
                (ln or 0 for _, _, old_n, new_n in lines_with_nums for ln in (old_n, new_n) if ln is not None),
                default=len(lines_with_nums),
            )
            line_w = min(len(str(max_num)) + 1, max(0, (self.width - 3) // 4))
        content_width = self.width - 2 - line_w  # "+ " or "  " then line numbers
        if content_width <= 0:
            content_width = max(1, self.width - 2 - line_w)

        row = 0
        for tag, line, old_num, new_num in lines_with_nums:
            if row >= self.height:
                break
            bg = self._line_bg(tag)
            fg = self._line_fg(tag)
            prefix = "+ " if tag == "+" else "- " if tag == "-" else "  "
            wrapped = self._wrap_line(line, content_width)
            display_num = new_num if new_num is not None else old_num
            for wi, part in enumerate(wrapped):
                if row >= self.height:
                    break
                x_off = 0
                for ch in prefix:
                    if x_off >= self.width:
                        break
                    buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg, bg=bg))
                    x_off += 1
                if self._show_line_numbers and line_w > 0:
                    num_str = (str(display_num) if (display_num is not None and wi == 0) else "").rjust(line_w)[:line_w]
                    ln_bg = self._added_line_number_bg if tag == "+" else self._removed_line_number_bg if tag == "-" else self._line_number_bg
                    for ch in num_str:
                        if x_off >= self.width:
                            break
                        buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=self._line_number_fg, bg=ln_bg))
                        x_off += 1
                # Content: syntax highlight if filetype else plain
                if self._filetype and part:
                    spans = syntax_highlight(part, self._filetype)
                    for text, token_type in spans:
                        color = self._theme.get(token_type, self._theme["plain"])
                        for ch in text:
                            if x_off >= self.width:
                                break
                            buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=color, bg=bg))
                            x_off += 1
                else:
                    for ch in part:
                        if x_off >= self.width:
                            break
                        buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg, bg=bg))
                        x_off += 1
                while x_off < self.width:
                    buffer.set_cell(self.x + x_off, self.y + row, Cell(char=" ", fg=fg, bg=bg))
                    x_off += 1
                row += 1

    def _render_split_view(self, buffer: OptimizedBuffer) -> None:
        """Left column = removed/context, right column = added/context. Aligns with OpenTUI buildSplitView."""
        left_lines, right_lines = build_split_logical_lines(self._parsed_patch)
        half = max(1, self.width // 2)
        line_w = 3
        left_w = max(0, half - 2 - line_w)  # sign + line number + content
        right_w = max(0, self.width - half - 1 - 2 - line_w)
        max_rows = max(
            sum(len(self._wrap_line(ll.content, left_w)) for ll in left_lines),
            sum(len(self._wrap_line(rl.content, right_w)) for rl in right_lines),
        )
        left_visual: list[tuple[str, Optional[int], str]] = []  # (content, line_num, type)
        right_visual: list[tuple[str, Optional[int], str]] = []
        idx_l, idx_r = 0, 0
        for ll, rl in zip(left_lines, right_lines):
            l_parts = self._wrap_line(ll.content, left_w)
            r_parts = self._wrap_line(rl.content, right_w)
            n = max(len(l_parts), len(r_parts))
            for i in range(n):
                lc = l_parts[i] if i < len(l_parts) else ""
                rc = r_parts[i] if i < len(r_parts) else ""
                ln = ll.line_num if i == 0 else None
                rn = rl.line_num if i == 0 else None
                left_visual.append((lc, ln if not ll.hide_line_number else None, ll.type))
                right_visual.append((rc, rn if not rl.hide_line_number else None, rl.type))
        # Pad to same length
        while len(left_visual) < len(right_visual):
            left_visual.append(("", None, "empty"))
        while len(right_visual) < len(left_visual):
            right_visual.append(("", None, "empty"))

        row = 0
        for (lc, ln, lt), (rc, rn, rt) in zip(left_visual, right_visual):
            if row >= self.height:
                break
            # Left column
            x_off = 0
            bg_l = self._removed_bg if lt == "remove" else self._context_bg
            fg_l = self._removed_sign_color if lt == "remove" else self._ctx_fg
            sign_l = "- " if lt == "remove" else "  "
            for ch in sign_l:
                if x_off >= half:
                    break
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg_l, bg=bg_l))
                x_off += 1
            if self._show_line_numbers and line_w > 0 and ln is not None:
                num_str = str(ln).rjust(line_w)[:line_w]
                for ch in num_str:
                    if x_off >= half:
                        break
                    buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=self._line_number_fg, bg=self._line_number_bg))
                    x_off += 1
            for ch in lc[: left_w - x_off]:
                if x_off >= half:
                    break
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg_l, bg=bg_l))
                x_off += 1
            while x_off < half:
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=" ", fg=fg_l, bg=bg_l))
                x_off += 1
            # Gap
            if half < self.width:
                buffer.set_cell(self.x + half, self.y + row, Cell(char=" ", fg=self._fg, bg=self._context_bg))
            # Right column
            x_off = half + 1
            bg_r = self._added_bg if rt == "add" else self._context_bg
            fg_r = self._added_sign_color if rt == "add" else self._ctx_fg
            sign_r = "+ " if rt == "add" else "  "
            for ch in sign_r:
                if x_off >= self.width:
                    break
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg_r, bg=bg_r))
                x_off += 1
            if self._show_line_numbers and line_w > 0 and rn is not None:
                num_str = str(rn).rjust(line_w)[:line_w]
                for ch in num_str:
                    if x_off >= self.width:
                        break
                    buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=self._line_number_fg, bg=self._line_number_bg))
                    x_off += 1
            for ch in rc[:right_w]:
                if x_off >= self.width:
                    break
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=ch, fg=fg_r, bg=bg_r))
                x_off += 1
            while x_off < self.width:
                buffer.set_cell(self.x + x_off, self.y + row, Cell(char=" ", fg=fg_r, bg=bg_r))
                x_off += 1
            row += 1
