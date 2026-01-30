# pytui.components.input


from pytui.core.buffer import Cell, OptimizedBuffer
from pytui.core.colors import parse_color
from pytui.core.renderable import Renderable

# 默认 keyBindings 与 KeyboardHandler 键名一致
DEFAULT_INPUT_KEY_BINDINGS = {
    "move-left": "left",
    "move-right": "right",
    "delete-backward": "backspace",
    "delete-forward": "delete",
    "submit": "enter",
}


class Input(Renderable):
    """单行输入框。获得焦点时订阅 keypress，自行处理：Backspace/DEL、左右箭头、可打印字符。
    支持 enter 事件、maxLength、placeholderColor、cursorStyle、keyBindings。
    """

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self.value = options.get("value", "")
        self.placeholder = options.get("placeholder", "")
        self.max_length = options.get("max_length")  # None = 不限制
        self.fg = parse_color(options.get("fg", "#ffffff"))
        self.bg = parse_color(options.get("bg", "transparent"))
        self.placeholder_color = parse_color(
            options.get("placeholder_color", options.get("placeholderColor")) or "#888888"
        )
        # cursorStyle: "block" | "line"；block 为光标处反色+下划线，line 为竖线
        self.cursor_style = options.get("cursor_style", options.get("cursorStyle", "block"))
        self.cursor_pos = min(len(self.value), len(self.value))
        kb = options.get("key_bindings", options.get("keyBindings") or {})
        self._key_bindings = {**DEFAULT_INPUT_KEY_BINDINGS, **kb}

    def focus(self) -> None:
        super().focus()
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.events.on("keypress", self._on_keypress)

    def blur(self) -> None:
        if hasattr(self.ctx, "renderer") and self.ctx.renderer:
            self.ctx.renderer.events.remove_listener("keypress", self._on_keypress)
        super().blur()

    def _action_for_key(self, key: dict) -> str | None:
        """根据 key 返回 keyBindings 中的 action 名，若无则返回 None。"""
        name = key.get("name") or key.get("char")
        for action, bound in self._key_bindings.items():
            if bound == name:
                return action
        return None

    def _on_keypress(self, key: dict) -> None:
        if not self.focused:
            return
        name = key.get("name") or key.get("char")
        action = self._action_for_key(key)

        if action == "submit" or name == "enter" or key.get("char") in ("\r", "\n"):
            self.emit("enter", self.value)
            return
        if action == "delete-backward" or name == "backspace" or key.get("char") in ("\x08", "\x7f"):
            self.backspace()
            return
        if action == "delete-forward" or name == "delete":
            self.delete_forward()
            return
        if action == "move-left" or name == "left":
            self.cursor_pos = max(0, self.cursor_pos - 1)
            self.request_render()
            return
        if action == "move-right" or name == "right":
            self.cursor_pos = min(len(self.value), self.cursor_pos + 1)
            self.request_render()
            return
        if name and len(name) == 1 and name.isprintable():
            self.insert_char(name)

    def set_value(self, value: str) -> None:
        if self.value != value:
            self.value = value
            self.cursor_pos = len(value)
            self.emit("input", value)
            self.emit("change", value)
            self.request_render()

    def insert_char(self, ch: str) -> None:
        if self.max_length is not None and len(self.value) >= self.max_length:
            return
        self.value = self.value[: self.cursor_pos] + ch + self.value[self.cursor_pos :]
        self.cursor_pos += 1
        self.emit("input", self.value)
        self.emit("change", self.value)
        self.request_render()

    def backspace(self) -> None:
        """删除光标前一个字符。"""
        if self.cursor_pos > 0:
            self.value = self.value[: self.cursor_pos - 1] + self.value[self.cursor_pos :]
            self.cursor_pos -= 1
            self.emit("input", self.value)
            self.emit("change", self.value)
            self.request_render()

    def delete_forward(self) -> None:
        """删除光标处字符（DEL 键）。"""
        if self.cursor_pos < len(self.value):
            self.value = self.value[: self.cursor_pos] + self.value[self.cursor_pos + 1 :]
            self.emit("input", self.value)
            self.emit("change", self.value)
            self.request_render()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        text = self.value if self.value else self.placeholder
        text_fg = self.fg if self.value else self.placeholder_color
        for dx, char in enumerate(text):
            if dx >= self.width:
                break
            c = char if self.value else " "
            buffer.set_cell(self.x + dx, self.y, Cell(char=c, fg=text_fg, bg=self.bg))
        for dx in range(len(text), self.width):
            if dx >= self.width:
                break
            buffer.set_cell(self.x + dx, self.y, Cell(char=" ", fg=self.fg, bg=self.bg))
        if self.focused and self.cursor_pos <= self.width:
            cx = min(self.cursor_pos, self.width - 1)
            if cx < 0:
                cx = 0
            cell = buffer.get_cell(self.x + cx, self.y)
            if cell:
                if self.cursor_style == "line":
                    buffer.set_cell(
                        self.x + cx,
                        self.y,
                        Cell(char="▌", fg=self.fg, bg=cell.bg),
                    )
                else:
                    buffer.set_cell(
                        self.x + cx,
                        self.y,
                        Cell(
                            char=cell.char,
                            fg=cell.fg,
                            bg=self.fg,
                            underline=True,
                        ),
                    )
