#!/usr/bin/env python3
"""计数器示例：按空格加一，按 q 退出。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Text


def main() -> None:
    r = Renderer(width=50, height=14, target_fps=30)
    count = [0]  # 用 list 以便闭包内修改

    box = Box(
        r.context,
        {
            "width": 50,
            "height": 14,
            "border": True,
            "border_style": "rounded",
            "title": "Counter",
        },
    )
    text = Text(
        r.context,
        {"content": "Count: 0", "width": 48, "height": 2},
    )
    hint = Text(
        r.context,
        {"content": "SPACE = +1  |  q = quit", "width": 48, "height": 1},
    )
    box.add(text)
    box.add(hint)
    r.root.add(box)

    def on_key(key: dict) -> None:
        name = key.get("name") or key.get("char")
        if name == "q" or name == "Q":
            r.stop()
            return
        if name == " ":
            count[0] += 1
            text.set_content(f"Count: {count[0]}")
            r.schedule_render()

    r.events.on("keypress", on_key)
    r.start()


if __name__ == "__main__":
    main()
