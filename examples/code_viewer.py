#!/usr/bin/env python3
"""代码查看器示例：Code 组件展示 Python 代码片段。"""

from pytui.core.renderer import Renderer
from pytui.components import Box, Code

SAMPLE_CODE = '''def greet(name: str) -> str:
    return f"Hello, {name}!"

def main():
    msg = greet("pytui")
    print(msg)

if __name__ == "__main__":
    main()
'''


def main() -> None:
    r = Renderer(width=64, height=22, target_fps=30)
    box = Box(
        r.context,
        {
            "width": 64,
            "height": 22,
            "border": True,
            "border_style": "rounded",
            "title": "code_viewer.py",
        },
    )
    code = Code(
        r.context,
        {
            "content": SAMPLE_CODE.strip(),
            "language": "python",
            "show_line_numbers": True,
            "theme": "default",
            "width": 62,
            "height": 20,
        },
    )
    box.add(code)
    r.root.add(box)
    r.start()


if __name__ == "__main__":
    main()
