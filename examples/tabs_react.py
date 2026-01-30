#!/usr/bin/env python3
"""声明式标签页：TabSelect 组件 + useState，←/→ 切换，q 退出。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile

TABS = [
    ("Home", "Welcome home. Press ←/→ to switch tabs."),
    ("Settings", "Settings panel. Not implemented yet."),
    ("About", "pytui declarative TUI. Ctrl+C to exit."),
]


class TabsApp(Component):
    def render(self):
        tab_index, set_tab_index = useState(0)
        renderer = self.ctx.renderer
        tab_labels = [t for t, _ in TABS]

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            n = len(TABS)
            if name == "left" or (name == "tab" and key.get("shift")):
                set_tab_index(lambda prev: (prev - 1 + n) % n)
            elif name == "right" or (name == "tab" and not key.get("shift")):
                set_tab_index(lambda prev: (prev + 1) % n)

        def setup() -> None:
            renderer.events.on("keypress", on_key)

        useEffect(setup, [])
        title, body = TABS[tab_index]
        return h(
            "box",
            {"width": 56, "height": 14, "border": True, "title": "Tabs (TabSelect)"},
            h("tab_select", {"tabs": tab_labels, "selected": tab_index, "width": 54, "height": 1}),
            h("text", {"content": "", "width": 54, "height": 1}),
            h("text", {"content": f"  {body}", "width": 54, "height": 2}),
            h("text", {"content": "  ←/→ or Tab / Shift+Tab  |  q = quit", "width": 54, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=56, height=14, target_fps=30)
    reconcile(h(TabsApp, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
