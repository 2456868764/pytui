#!/usr/bin/env python3
"""登录表单示例：用户名/密码输入框 + 下拉选择（演示 Input、Select）。
Tab / Shift+Tab 在 Username → Password → Role 间切换焦点；输入/退格/上下键作用在当前焦点。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Text, Input, Select


def main() -> None:
    r = Renderer(width=52, height=18, target_fps=30)

    box = Box(
        r.context,
        {
            "width": 52,
            "height": 18,
            "border": True,
            "border_style": "single",
            "title": "Login",
        },
    )
    user_label = Text(
        r.context,
        {"content": "Username:", "width": 50, "height": 1},
    )
    user_input = Input(
        r.context,
        {"value": "", "placeholder": " enter username ", "width": 50, "height": 1},
    )
    pass_label = Text(
        r.context,
        {"content": "Password:", "width": 50, "height": 1},
    )
    pass_input = Input(
        r.context,
        {"value": "", "placeholder": " enter password ", "width": 50, "height": 1},
    )
    role_label = Text(
        r.context,
        {"content": "Role:", "width": 50, "height": 1},
    )
    role_select = Select(
        r.context,
        {
            "options": ["user", "admin", "guest"],
            "selected": 0,
            "width": 50,
            "height": 3,
        },
    )
    hint = Text(
        r.context,
        {"content": "Tab/Shift+Tab 切换焦点 | Ctrl+C 退出", "width": 50, "height": 1},
    )
    box.add(user_label)
    box.add(user_input)
    box.add(pass_label)
    box.add(pass_input)
    box.add(role_label)
    box.add(role_select)
    box.add(hint)
    r.root.add(box)

    # 可聚焦组件顺序：Username → Password → Role
    focusable = [user_input, pass_input, role_select]
    focus_index = 0
    user_input.focus()

    def on_key(key: dict) -> None:
        nonlocal focus_index
        name = key.get("name") or key.get("char")
        if key.get("ctrl") and name == "c":
            r.stop()
            return
        # Tab 下一个，Shift+Tab 上一个
        if name == "tab":
            focusable[focus_index].blur()
            if key.get("shift"):
                focus_index = (focus_index - 1) % len(focusable)
            else:
                focus_index = (focus_index + 1) % len(focusable)
            focusable[focus_index].focus()
            r.schedule_render()
            return
        # Select 自己只处理上下键；Input 在 focus 时已订阅 keypress，自行处理输入/退格/左右
        current = focusable[focus_index]
        if current is role_select:
            if name == "up":
                role_select.select_prev()
            elif name == "down":
                role_select.select_next()

    r.events.on("keypress", on_key)
    r.start()


if __name__ == "__main__":
    main()
