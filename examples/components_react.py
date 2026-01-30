#!/usr/bin/env python3
"""Phase 7 组件示例：TabSelect、Slider、ScrollBar、LineNumber，声明式 h() 驱动。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile


class Phase7Demo(Component):
    def render(self):
        tab_index, set_tab_index = useState(0)
        volume, set_volume = useState(50)
        scroll_pos, set_scroll_pos = useState(0)
        renderer = self.ctx.renderer
        tabs = ["Overview", "Slider", "Editor"]
        scroll_max = 20
        line_count = 25

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q" or name == "Q":
                renderer.stop()
                return
            n = len(tabs)
            if name == "left" or (name == "tab" and key.get("shift")):
                set_tab_index(lambda prev: (prev - 1 + n) % n)
            elif name == "right" or (name == "tab" and not key.get("shift")):
                set_tab_index(lambda prev: (prev + 1) % n)
            elif name in ("j", "J"):
                set_volume(max(0, volume - 5))
            elif name in ("k", "K"):
                set_volume(min(100, volume + 5))
            elif name == "up":
                set_scroll_pos(max(0, scroll_pos - 1))
            elif name == "down":
                set_scroll_pos(min(scroll_max, scroll_pos + 1))

        def setup() -> None:
            renderer.events.on("keypress", on_key)

        useEffect(setup, [])

        return h(
            "box",
            {
                "width": 62,
                "height": 22,
                "border": True,
                "border_style": "single",
                "title": "Phase 7: TabSelect / Slider / ScrollBar / LineNumber",
            },
            h("tab_select", {"tabs": tabs, "selected": tab_index, "width": 60, "height": 1}),
            h("text", {"content": f" Volume: {volume}/100 (j/k)", "width": 60, "height": 1}),
            h("slider", {"min": 0, "max": 100, "value": volume, "width": 60, "height": 1}),
            h("text", {"content": f" Scroll: {scroll_pos}/{scroll_max} (↑/↓)", "width": 60, "height": 1}),
            h(
                "box",
                {"width": 60, "height": 8, "flex_direction": "row"},
                h("line_number", {"line_count": line_count, "scroll_offset": scroll_pos, "line_number_width": 4, "width": 4, "height": 8}),
                h("scrollbar", {"scroll_max": scroll_max, "scroll_value": scroll_pos, "width": 1, "height": 8}),
                h("text", {"content": f"  Tab: {tabs[tab_index]}  |  Line {scroll_pos + 1}-{scroll_pos + 8}", "width": 54, "height": 8}),
            ),
            h("text", {"content": " Tab/Shift+Tab or ←/→ tab  |  j/k volume  |  ↑/↓ scroll  |  q = quit", "width": 60, "height": 1}),
        )


def main() -> None:
    r = Renderer(width=62, height=22, target_fps=30)
    reconcile(h(Phase7Demo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
