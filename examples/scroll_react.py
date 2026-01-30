#!/usr/bin/env python3
"""对应 opentui scroll.tsx：Scrollbox 内多色 Box，Lorem 文本，↑/↓ 或 j/k 滚动。"""

import random

from pytui.core.renderer import Renderer
from pytui.react import Component, h, reconcile

LOREM = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Proin dictum rutrum mi, ac egestas elit dictum ac.",
    "Aliquam erat volutpat. Nullam in nisi vitae turpis consequat ultrices.",
    "Sed posuere pretium metus, a posuere est consequat nec.",
    "Curabitur nec quam sed augue congue vestibulum.",
    "Suspendisse tincidunt, augue at rhoncus cursus, urna felis malesuada leo.",
    "Nam molestie euismod faucibus. Quisque id odio in pede ornare luctus.",
    "Integer consequat, quam at congue cursus, magna eros pretium enim.",
    "Vivamus cursus, ex eu tincidunt cursus, libero massa dictum arcu.",
    "Morbi auctor magna a ultricies consequat.",
]

BOX_COLORS = [
    "#2e3440", "#bf616a", "#a3be8c", "#ebcb8b", "#81a1c1", "#b48ead",
    "#88c0d0", "#5e81ac", "#d08770", "#e5e9f0", "#414868", "#7aa2f7",
    "#292e42", "#373d52", "#24283b", "#cdd6f4",
]


def get_random_lorem(num: int) -> list[str]:
    return [random.choice(LOREM) for _ in range(num)]


class ScrollDemo(Component):
    def render(self):
        boxes = []
        for i in range(16):
            num_lines = 2 + random.randint(0, 3)
            lines = get_random_lorem(num_lines)
            bg = BOX_COLORS[i % len(BOX_COLORS)]
            box_children = [h("text", {"content": f"Box {i + 1}", "width": 56})]
            for txt in lines:
                box_children.append(h("text", {"content": txt[:58], "width": 56}))
            boxes.append(
                h(
                    "box",
                    {"width": 58, "height": 2 + num_lines, "background_color": bg, "border": True},
                    *box_children,
                )
            )
        return h(
            "box",
            {"width": 62, "height": 26, "border": True, "title": "Scroll Demo"},
            h("text", {"content": "↑/↓ 或 j/k 滚动  Ctrl+C 退出", "fg": "#888888", "width": 60, "height": 1}),
            h(
                "scrollbox",
                {"width": 60, "height": 23, "focused": True},
                *boxes,
            ),
        )


def main() -> None:
    r = Renderer(width=62, height=26, target_fps=30)
    reconcile(h(ScrollDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
