#!/usr/bin/env python3
"""对应 opentui animation.tsx：System Monitor 进度条，useTimeline 驱动 0→目标值 动画。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useTimeline, h, reconcile


class AnimationDemo(Component):
    def render(self):
        timeline = useTimeline(self.ctx)
        elapsed = timeline["elapsed"]
        t = min(1.0, elapsed / 3.0)
        stats = {
            "cpu": min(85, int(85 * t)),
            "memory": min(70, int(70 * t)),
            "network": min(95, int(95 * t)),
            "disk": min(60, int(60 * t)),
        }
        stats_map = [
            ("CPU", "cpu", "#6a5acd"),
            ("Memory", "memory", "#4682b4"),
            ("Network", "network", "#20b2aa"),
            ("Disk", "disk", "#daa520"),
        ]
        children = []
        for name, key, color in stats_map:
            val = stats.get(key, 0)
            bar_w = max(0, min(48, int(48 * val / 100)))
            children.append(
                h(
                    "box",
                    {"width": 50, "height": 3},
                    h("box", {"width": 50, "height": 1}, h("text", {"content": name, "width": 10}), h("text", {"content": f"{val}%", "width": 8})),
                    h(
                        "box",
                        {"width": 50, "height": 1, "background_color": "#333333"},
                        h("box", {"width": bar_w, "height": 1, "background_color": color}),
                    ),
                ),
            )
        return h(
            "box",
            {
                "title": "System Monitor",
                "width": 54,
                "height": 18,
                "border": True,
                "border_style": "single",
                "margin": 1,
            },
            *children,
        )


def main() -> None:
    r = Renderer(width=56, height=24, target_fps=30)
    reconcile(h(AnimationDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
