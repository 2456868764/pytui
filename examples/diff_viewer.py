#!/usr/bin/env python3
"""Diff 查看器示例：对比两段文本的增删改。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Diff

OLD = """def old():
    x = 1
    return x
"""

NEW = """def new():
    x = 2
    y = 3
    return x + y
"""


def main() -> None:
    r = Renderer(width=70, height=20, target_fps=30)
    box = Box(
        r.context,
        {
            "width": 70,
            "height": 20,
            "border": True,
            "border_style": "single",
            "title": "Diff (old vs new)",
        },
    )
    diff = Diff(
        r.context,
        {
            "old_text": OLD.strip(),
            "new_text": NEW.strip(),
            "width": 68,
            "height": 18,
        },
    )
    box.add(diff)
    r.root.add(box)
    r.start()


if __name__ == "__main__":
    main()
