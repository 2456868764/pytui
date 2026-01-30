#!/usr/bin/env python3
"""声明式仪表盘：与 dashboard.py 相同布局，用 Component + h() 构建。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, h, reconcile


class Dashboard(Component):
    def render(self):
        # 可加 useState 做动态统计，这里先静态
        lines = [
            "--- Stats ---",
            "  Items: 42",
            "  Status: OK",
            "  Uptime: 1h 23m",
            "",
            "--- Log ---",
        ]
        for i in range(1, 12):
            lines.append(f"  [{i:02d}] Event #{i}")
        lines.append("  Ctrl+C to exit")
        children = [h("text", {"content": line, "width": 58, "height": 1}) for line in lines]
        return h(
            "box",
            {"width": 60, "height": 24, "border": True, "border_style": "single", "title": "Dashboard"},
            children,
        )


def main() -> None:
    r = Renderer(width=60, height=24, target_fps=30)
    reconcile(h(Dashboard, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
