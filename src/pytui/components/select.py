# pytui.components.select


from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any

from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable

# options 项：支持 { name, description?, value? } 或 str
SelectOption = dict[str, Any] | str

DEFAULT_SELECT_KEY_BINDINGS = {
    "move-up": "up",
    "move-down": "down",
    "select-current": "enter",
}


def _normalize_options(raw: list[SelectOption]) -> list[dict[str, Any]]:
    """将 options 规范为 list[{name, description, value}]。"""
    out: list[dict[str, Any]] = []
    for o in raw:
        if isinstance(o, str):
            out.append({"name": o, "description": None, "value": o})
        elif isinstance(o, dict):
            out.append({
                "name": o.get("name", str(o.get("value", ""))),
                "description": o.get("description"),
                "value": o.get("value", o.get("name", "")),
            })
        else:
            out.append({"name": str(o), "description": None, "value": o})
    return out


@dataclass
class _OptionRow:
    name: str
    description: str | None
    value: Any


class Select(Renderable):
    """选项列表。支持 options 为 list[str] 或 list[{name, description?, value?}]；
    showDescription、descriptionColor、keyBindings、wrapSelection、fastScrollStep、showScrollIndicator。
    """

    def __init__(self, ctx: Any, options: dict | None = None) -> None:
        options = options or {}
        super().__init__(ctx, options)
        raw_opts = list(options.get("options", []))
        self._options: list[_OptionRow] = [
            _OptionRow(o["name"], o.get("description"), o.get("value"))
            for o in _normalize_options(raw_opts)
        ]
        n = len(self._options)
        self.selected_index = max(0, min(options.get("selected", options.get("selectedIndex", 0)), n - 1 if n else 0))
        self.fg = parse_color(options.get("fg", "#ffffff"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.selected_fg = parse_color(options.get("selected_fg", "#000000"))
        self.selected_bg = parse_color(options.get("selected_bg", "#ffffff"))
        self.show_description = options.get("show_description", options.get("showDescription", False))
        self.description_color = parse_color(
            options.get("description_color", options.get("descriptionColor")) or "#888888"
        )
        self._key_bindings = {
            **DEFAULT_SELECT_KEY_BINDINGS,
            **options.get("key_bindings", options.get("keyBindings") or {}),
        }
        self.wrap_selection = options.get("wrap_selection", options.get("wrapSelection", True))
        self.fast_scroll_step = max(1, options.get("fast_scroll_step", options.get("fastScrollStep", 5)))
        self.show_scroll_indicator = options.get("show_scroll_indicator", options.get("showScrollIndicator", True))
        # 可选 font（ASCIIFont）：渲染选项标签用艺术字；None 则普通文本。预留，当前仍用普通文本。
        self._font = options.get("font") or options.get("font_dict")

    @property
    def options(self) -> list[str]:
        """选项显示名列表（兼容旧用法）。"""
        return [r.name for r in self._options]

    def _action_for_key(self, key: dict) -> str | None:
        name = key.get("name") or key.get("char")
        for action, bound in self._key_bindings.items():
            if bound == name:
                return action
        return None

    @property
    def selected(self) -> str | None:
        if 0 <= self.selected_index < len(self._options):
            return self._options[self.selected_index].name
        return None

    @property
    def selected_value(self) -> Any:
        if 0 <= self.selected_index < len(self._options):
            return self._options[self.selected_index].value
        return None

    def select_next(self, step: int = 1) -> None:
        if not self._options:
            return
        n = len(self._options)
        if self.wrap_selection:
            self.selected_index = (self.selected_index + step) % n
        else:
            self.selected_index = min(self.selected_index + step, n - 1)
        self.emit("select", self.selected_index, self.selected, self.selected_value)
        self.request_render()

    def select_prev(self, step: int = 1) -> None:
        if not self._options:
            return
        n = len(self._options)
        if self.wrap_selection:
            self.selected_index = (self.selected_index - step) % n
        else:
            self.selected_index = max(self.selected_index - step, 0)
        self.emit("select", self.selected_index, self.selected, self.selected_value)
        self.request_render()

    def select_current(self) -> None:
        """确认当前选项（如 Enter）。"""
        self.emit("select", self.selected_index, self.selected, self.selected_value)
        self.request_render()

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            # 直接监听 keyboard，确保在 Mac 等终端上能收到 ↑/↓（不依赖 events 转发）
            self.ctx.renderer.keyboard.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.keyboard.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _on_keypress(self, key: dict) -> None:
        if os.environ.get("PYTUI_DEBUG"):
            print(f"[pytui:select] _on_keypress focused={self.focused} key={key}", file=sys.stderr, flush=True)
        if not self.focused:
            return
        name = key.get("name") or key.get("char")
        action = self._action_for_key(key)
        if action == "move-up" or name == "up":
            step = self.fast_scroll_step if key.get("ctrl") else 1
            if os.environ.get("PYTUI_DEBUG"):
                print(f"[pytui:select] handling up -> select_prev({step})", file=sys.stderr, flush=True)
            self.select_prev(step)
            return
        if action == "move-down" or name == "down":
            step = self.fast_scroll_step if key.get("ctrl") else 1
            if os.environ.get("PYTUI_DEBUG"):
                print(f"[pytui:select] handling down -> select_next({step})", file=sys.stderr, flush=True)
            self.select_next(step)
            return
        if action == "select-current" or name == "enter" or name in ("\r", "\n"):
            self.select_current()
            return

    def render_self(self, buffer: OptimizedBuffer) -> None:
        # 可选滚动：只显示以 selected_index 为中心的一屏
        n_opts = len(self._options)
        if n_opts == 0:
            return
        if self.height <= 0 or self.width <= 0:
            return

        # 视口：保证选中项可见，可滚动
        max_scroll = max(0, n_opts - self.height)
        scroll_y = getattr(self, "_scroll_y", 0)
        if self.selected_index < scroll_y:
            scroll_y = self.selected_index
        if self.selected_index >= scroll_y + self.height:
            scroll_y = self.selected_index - self.height + 1
        scroll_y = max(0, min(scroll_y, max_scroll))
        self._scroll_y = scroll_y

        for dy in range(self.height):
            idx = scroll_y + dy
            if idx >= n_opts:
                break
            row = self._options[idx]
            is_selected = idx == self.selected_index
            fg = self.selected_fg if is_selected else self.fg
            bg = self.selected_bg if is_selected else self.bg
            # 一行：name（+ 可选 description 用 descriptionColor）
            name_part = row.name[: self.width]
            rest = self.width - len(name_part)
            if self.show_description and row.description and rest > 1:
                desc_part = (" " + row.description)[: rest]
            else:
                desc_part = ""
            line = (name_part + desc_part + " " * self.width)[: self.width]
            name_len = len(name_part)
            for dx, char in enumerate(line):
                if dx >= self.width:
                    break
                in_desc = self.show_description and name_len <= dx < name_len + len(desc_part)
                cell_fg = self.description_color if in_desc else fg
                buffer.set_cell(self.x + dx, self.y + dy, Cell(char=char, fg=cell_fg, bg=bg))

        if self.show_scroll_indicator and max_scroll > 0 and self.width > 0:
            # 右侧一列显示滚动指示
            bar_x = self.x + self.width - 1
            bar_h = self.height
            thumb = max(1, bar_h * bar_h // (n_opts + 1))
            thumb_y = bar_h * scroll_y // (max_scroll + 1) if max_scroll else 0
            for dy in range(bar_h):
                in_thumb = thumb_y <= dy < thumb_y + thumb
                c = "█" if in_thumb else "░"
                buffer.set_cell(bar_x, self.y + dy, Cell(char=c, fg=self.fg, bg=self.bg))
