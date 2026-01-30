#!/usr/bin/env python3
"""声明式计数器：使用 Component + useState + useEffect + h() + reconcile。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile


class Counter(Component):
    def render(self):
        count, set_count = useState(0)
        renderer = self.ctx.renderer

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            if name == " ":
                set_count(count + 1)

        def setup() -> None:
            renderer.events.on("keypress", on_key)

        useEffect(setup, [])
        return h(
            "box",
            {"width": 50, "height": 14, "border": True, "border_style": "rounded", "title": "Counter"},
            h("text", {"content": f"Count: {count}", "width": 48, "height": 2}),
            h("text", {"content": "SPACE = +1  |  q = quit", "width": 48, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=50, height=14, target_fps=30)
    reconcile(h(Counter, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
