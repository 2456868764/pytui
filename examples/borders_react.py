#!/usr/bin/env python3
"""对应 opentui borders.tsx：四种边框样式 - single / double / rounded / heavy。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, h, reconcile


class BordersDemo(Component):
    def render(self):
        return h(
            "box",
            {"width": 60, "height": 10, "border": False, "flex_direction": "row"},
            h(
                "box",
                {"border": True, "border_style": "single", "width": 14, "height": 3},
                h("text", {"content": "Single", "width": 12}),
            ),
            h(
                "box",
                {"border": True, "border_style": "double", "width": 14, "height": 3},
                h("text", {"content": "Double", "width": 12}),
            ),
            h(
                "box",
                {"border": True, "border_style": "rounded", "width": 14, "height": 3},
                h("text", {"content": "Rounded", "width": 12}),
            ),
            h(
                "box",
                {"border": True, "border_style": "bold", "width": 14, "height": 3},
                h("text", {"content": "Heavy", "width": 12}),
            ),
        )


def main() -> None:
    r = Renderer(width=62, height=12, target_fps=30)
    reconcile(h(BordersDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
