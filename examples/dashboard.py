#!/usr/bin/env python3
"""仪表盘示例：单面板内 Stats + Log 区块。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Text


def main() -> None:
    r = Renderer(width=60, height=24, target_fps=30)

    root = Box(
        r.context,
        {
            "width": 60,
            "height": 24,
            "border": True,
            "border_style": "single",
            "title": "Dashboard",
        },
    )
    root.add(Text(r.context, {"content": "--- Stats ---", "width": 58, "height": 1}))
    root.add(Text(r.context, {"content": "  Items: 42", "width": 58, "height": 1}))
    root.add(Text(r.context, {"content": "  Status: OK", "width": 58, "height": 1}))
    root.add(Text(r.context, {"content": "  Uptime: 1h 23m", "width": 58, "height": 1}))
    root.add(Text(r.context, {"content": "", "width": 58, "height": 1}))
    root.add(Text(r.context, {"content": "--- Log ---", "width": 58, "height": 1}))
    for i in range(1, 12):
        root.add(
            Text(
                r.context,
                {"content": f"  [{i:02d}] Event #{i}", "width": 58, "height": 1},
            )
        )
    root.add(Text(r.context, {"content": "  Ctrl+C to exit", "width": 58, "height": 1}))
    r.root.add(root)
    r.start()


if __name__ == "__main__":
    main()
