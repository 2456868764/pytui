#!/usr/bin/env python3
"""对应 opentui basic.tsx：OpenTUI with React 风格登录表单。
Styled Text、Username/Password 输入框、Tab 切换焦点、Enter 提交、状态显示。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, useRenderer, h, reconcile
from pytui.components.text_node import bold, italic


class BasicApp(Component):
    def render(self):
        username, set_username = useState("")
        password, set_password = useState("")
        focused, set_focused = useState("username")
        status, set_status = useState("idle")
        renderer = useRenderer(self.ctx)
        events = useKeyboard(self.ctx)

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "tab":
                set_focused(lambda p: "password" if p == "username" else "username")
                return
            if name == "q" or (name and name.lower() == "q" and key.get("ctrl")):
                renderer.stop()
                return

        def setup() -> None:
            if getattr(self, "_key_reg", False):
                return
            self._key_reg = True
            events.on("keypress", on_key)

        useEffect(setup, [])

        def on_username_change(value: str) -> None:
            set_username(value)

        def on_password_change(value: str) -> None:
            set_password(value)

        def on_submit() -> None:
            if username == "admin" and password == "secret":
                set_status("success")
            else:
                set_status("invalid")

        status_fg = "#AAAAAA" if status == "idle" else ("green" if status == "success" else "red")

        return h(
            "box",
            {
                "width": 50,
                "height": 18,
                "border": True,
                "border_style": "single",
                "title": "OpenTUI with React!",
                "padding": 2,
            },
            h("text", {"content": "OpenTUI with React!", "fg": "#FFFF00", "width": 46, "height": 1}),
            h(
                "text_node",
                {"spans": [bold("Styled Text!"), " ", italic("Italic"), " (styled)"], "width": 46, "height": 1},
            ),
            h(
                "box",
                {"title": "Username", "border": True, "width": 46, "height": 3},
                h(
                    "input",
                    {
                        "placeholder": "Enter your username...",
                        "value": username,
                        "width": 44,
                        "height": 1,
                        "focused": focused == "username",
                        "onInput": on_username_change,
                        "onSubmit": on_submit,
                    },
                ),
            ),
            h(
                "box",
                {"title": "Password", "border": True, "width": 46, "height": 3},
                h(
                    "input",
                    {
                        "placeholder": "Enter your password...",
                        "value": password,
                        "width": 44,
                        "height": 1,
                        "focused": focused == "password",
                        "onInput": on_password_change,
                        "onSubmit": on_submit,
                    },
                ),
            ),
            h("text", {"content": status.upper(), "fg": status_fg, "width": 46, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=50, height=20, target_fps=30)
    reconcile(h(BasicApp, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
