#!/usr/bin/env python3
"""声明式 Hello World：仅用 h() + reconcile，无 state。"""

from pytui.core.renderer import Renderer
from pytui.react import h, reconcile


def main() -> None:
    r = Renderer(width=40, height=10, target_fps=30)
    tree = h(
        "box",
        {"width": 40, "height": 10, "border": True, "border_style": "rounded", "title": "Hello"},
        h("text", {"content": "Hello, pytui!", "width": 38, "height": 2}),
        h("text", {"content": "Ctrl+C to exit", "width": 38, "height": 1}),
    )
    reconcile(tree, r.root)
    r.start()


if __name__ == "__main__":
    main()
