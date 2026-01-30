#!/usr/bin/env python3
"""声明式登录表单：useState 存 username/password/role，h('input')/h('select') 展示。
使用 useKeyboard/useRenderer，函数式 setState 避免闭包陈旧值。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, useRenderer, h, reconcile


class LoginForm(Component):
    def render(self):
        username, set_username = useState("")
        password, set_password = useState("")
        role_index, set_role_index = useState(0)
        renderer = useRenderer(self.ctx)
        events = useKeyboard(self.ctx)
        roles = ["user", "admin", "guest"]

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            if name and len(name) == 1 and name.isprintable():
                set_username(lambda prev: prev + name)
            if name == "backspace":
                set_username(lambda prev: prev[:-1] if prev else prev)
            if name == "up":
                set_role_index(lambda prev: (prev - 1 + len(roles)) % len(roles))
            if name == "down":
                set_role_index(lambda prev: (prev + 1) % len(roles))

        def setup() -> None:
            # 只注册一次，否则每次 re-render 会重复注册，上下键会触发多次 set_role_index
            if getattr(self, "_keypress_registered", False):
                return
            self._keypress_registered = True
            events.on("keypress", on_key)

        useEffect(setup, [])
        return h(
            "box",
            {"width": 52, "height": 18, "border": True, "border_style": "single", "title": "Login (React)"},
            h("text", {"content": "Username:", "width": 50, "height": 1}),
            h("input", {"value": username, "placeholder": " enter username ", "width": 50, "height": 1}),
            h("text", {"content": "Password:", "width": 50, "height": 1}),
            h("input", {"value": password, "placeholder": " enter password ", "width": 50, "height": 1}),
            h("text", {"content": "Role:", "width": 50, "height": 1}),
            h("select", {"options": roles, "selected": role_index, "width": 50, "height": 3}),
            h("text", {"content": "↑/↓ role  |  type=username  |  q = quit", "width": 50, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=52, height=18, target_fps=30)
    reconcile(h(LoginForm, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
