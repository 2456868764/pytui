#!/usr/bin/env python3
"""对应 opentui box.tsx：Box 示例 - 标准/标题/背景色/内边距/外边距/居中/嵌套。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, h, reconcile


class BoxExamples(Component):
    def render(self):
        return h(
            "box",
            {"width": 60, "height": 28, "border": False},
            h("text", {"content": "Box Examples", "width": 58, "height": 1}),
            h("box", {"border": True, "width": 58, "height": 3}, h("text", {"content": "1. Standard Box", "width": 56})),
            h(
                "box",
                {"border": True, "title": "Title", "width": 58, "height": 3},
                h("text", {"content": "2. Box with Title", "width": 56}),
            ),
            h(
                "box",
                {"border": True, "background_color": "#0000ff", "width": 58, "height": 3},
                h("text", {"content": "3. Box with Background Color", "width": 56}),
            ),
            h(
                "box",
                {"border": True, "width": 58, "height": 3},
                h("text", {"content": "4. Box with Padding", "width": 56}),
            ),
            h(
                "box",
                {"border": True, "width": 58, "height": 3},
                h("text", {"content": "5. Box with Margin", "width": 56}),
            ),
            h(
                "box",
                {"border": True, "width": 58, "height": 3},
                h("text", {"content": "6. Centered Text", "width": 56}),
            ),
            h(
                "box",
                {"border": True, "width": 58, "height": 5},
                h("text", {"content": "7. Justified Center", "width": 56}),
            ),
            h(
                "box",
                {"border": True, "title": "Nested Boxes", "background_color": "#ff0000", "width": 58, "height": 5},
                h(
                    "box",
                    {"border": True, "background_color": "#0000ff", "width": 54, "height": 3},
                    h("text", {"content": "8. Nested Box", "width": 52}),
                ),
            ),
        )


def main() -> None:
    r = Renderer(width=62, height=30, target_fps=30)
    reconcile(h(BoxExamples, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
