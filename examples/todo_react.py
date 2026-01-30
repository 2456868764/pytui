#!/usr/bin/env python3
"""声明式 Todo：useState 存列表，a=添加 r=删除最后一项，q 退出。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile


class TodoApp(Component):
    def render(self):
        items, set_items = useState(["Learn pytui", "Write examples", "Run tests"])
        renderer = self.ctx.renderer

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            if name == "a":
                set_items(lambda prev: prev + [f"Item #{len(prev) + 1}"])
            if name == "r":
                set_items(lambda prev: prev[:-1] if prev else prev)

        def setup() -> None:
            renderer.events.on("keypress", on_key)

        useEffect(setup, [])
        children = [
            h("text", {"content": "  --- Todo ---", "width": 46, "height": 1}),
            h("text", {"content": "", "width": 46, "height": 1}),
        ]
        for i, label in enumerate(items):
            children.append(h("text", {"content": f"  [{i+1}] {label}", "width": 46, "height": 1}))
        children.append(h("text", {"content": "", "width": 46, "height": 1}))
        children.append(h("text", {"content": "  a = add  |  r = remove last  |  q = quit", "width": 46, "height": 1}))
        return h(
            "box",
            {"width": 50, "height": 18, "border": True, "title": "Todo"},
            *children,
        )


def main() -> None:
    r = Renderer(width=50, height=18, target_fps=30)
    reconcile(h(TodoApp, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
