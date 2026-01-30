#!/usr/bin/env python3
"""多行文本示例：Textarea 长内容 + 滚动提示。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Text, Textarea

LONG_TEXT = """Line 1:  pytui is a Python TUI framework.
Line 2:  It provides Box, Text, Input, Select, and more.
Line 3:  Use Textarea for multi-line content with scroll.
Line 4:  Press Ctrl+C to exit.
Line 5:  You can scroll if the content is long.
Line 6:  This is line six.
Line 7:  And line seven.
Line 8:  Line eight.
Line 9:  Line nine.
Line 10: The last line.
"""


def main() -> None:
    r = Renderer(width=58, height=18, target_fps=30)
    box = Box(
        r.context,
        {
            "width": 58,
            "height": 18,
            "border": True,
            "border_style": "rounded",
            "title": "Textarea Demo",
        },
    )
    hint = Text(
        r.context,
        {"content": "Up/Down to scroll (when wired)", "width": 56, "height": 1},
    )
    area = Textarea(
        r.context,
        {"content": LONG_TEXT.strip(), "width": 56, "height": 8},
    )
    box.add(hint)
    box.add(area)
    r.root.add(box)

    def on_key(key: dict) -> None:
        name = key.get("name")
        if name == "up":
            area.scroll_up()
            r.schedule_render()
        elif name == "down":
            area.scroll_down()
            r.schedule_render()

    r.events.on("keypress", on_key)
    r.start()


if __name__ == "__main__":
    main()
