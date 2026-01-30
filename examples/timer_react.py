#!/usr/bin/env python3
"""声明式计时器：useState 存秒数，空格 +1，q 退出。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile


class Timer(Component):
    def render(self):
        seconds, set_seconds = useState(0)
        renderer = self.ctx.renderer

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            if name == " ":
                set_seconds(lambda prev: prev + 1)

        def setup() -> None:
            renderer.events.on("keypress", on_key)

        useEffect(setup, [])
        m, s = divmod(seconds, 60)
        time_str = f"{m:02d}:{s:02d}"
        return h(
            "box",
            {"width": 40, "height": 12, "border": True, "title": "Timer"},
            h("text", {"content": f"  Elapsed: {time_str}", "width": 38, "height": 2}),
            h("text", {"content": "  SPACE = +1 sec  |  q = quit", "width": 38, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=40, height=12, target_fps=30)
    reconcile(h(Timer, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
