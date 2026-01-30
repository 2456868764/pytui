#!/usr/bin/env python3
"""滚动加速度示例：Scrollbox + MacOSScrollAccel，连续按键时滚动步长增大。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile
from pytui.utils.scroll_acceleration import MacOSScrollAccel


class ScrollAccelDemo(Component):
    def render(self):
        scroll_y, set_scroll_y = useState(0)
        renderer = self.ctx.renderer
        content_lines = 40
        view_height = 12
        accel = MacOSScrollAccel(
            threshold1=80,
            threshold2=40,
            multiplier1=2,
            multiplier2=4,
            streak_timeout_ms=150,
        )

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            max_y = content_lines - view_height
            if name == "up":
                step = max(1, int(accel.tick()))
                set_scroll_y(lambda prev: max(0, prev - step))
            elif name == "down":
                step = max(1, int(accel.tick()))
                set_scroll_y(lambda prev: min(max_y, prev + step))

        def setup() -> None:
            renderer.events.on("keypress", on_key)

        useEffect(setup, [])

        lines = [f"  Line {i + 1}: scroll with ↑/↓ (acceleration on repeat)" for i in range(content_lines)]
        visible = "\n".join(lines[scroll_y : scroll_y + view_height])

        return h(
            "box",
            {
                "width": 58,
                "height": 16,
                "border": True,
                "border_style": "rounded",
                "title": "Scroll + MacOSScrollAccel",
            },
            h("text", {"content": f" Position: {scroll_y}  (↑/↓ fast = more lines)  q = quit", "width": 56, "height": 1}),
            h("text", {"content": visible, "width": 56, "height": view_height}),
            h("text", {"content": " Hold ↑/↓ for accelerated scroll", "width": 56, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=58, height=16, target_fps=30)
    reconcile(h(ScrollAccelDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
