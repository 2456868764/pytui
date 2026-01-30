#!/usr/bin/env python3
"""Hello World 示例：Box + Text。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Text


def main() -> None:
    r = Renderer(width=60, height=16, target_fps=30)
    box = Box(
        r.context,
        {
            "width": 60,
            "height": 16,
            "border": True,
            "border_style": "rounded",
            "title": "Hello pytui",
        },
    )
    text = Text(
        r.context,
        {"content": "Hello, Python TUI!", "width": 58, "height": 14},
    )
    box.add(text)
    r.root.add(box)
    r.start()


if __name__ == "__main__":
    main()
