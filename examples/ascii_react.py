#!/usr/bin/env python3
"""对应 opentui ascii.tsx：Select 选字体（Tiny/Block/Slick/Shade）+ ASCIIFont 显示艺术字。
↑/↓ 选字体、Enter 确认。从 IDE 运行时若方向键无反应，请用终端执行：python examples/ascii_react.py"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, h, reconcile


class AsciiDemo(Component):
    def render(self):
        text = "ASCII"
        font, set_font = useState("tiny")

        options = [
            {"name": "Tiny", "description": "Tiny font", "value": "tiny"},
            {"name": "Block", "description": "Block font", "value": "block"},
            {"name": "Slick", "description": "Slick font", "value": "slick"},
            {"name": "Shade", "description": "Shade font", "value": "shade"},
        ]

        def on_select(_idx: int, _n: str, value: str) -> None:
            set_font(value if value else "tiny")

        # 与 font 状态同步的选中索引，否则重渲染后 Select 会重置为 0
        selected_index = next((i for i, o in enumerate(options) if o["value"] == font), 0)

        # 对应 TSX: box(padding) -> box(height 8, border) -> select; ascii-font
        return h(
            "box",
            {"width": 52, "height": 16, "border": False, "padding": 1},
            h(
                "box",
                {"width": 50, "height": 8, "border": True, "margin_bottom": 1},
                h(
                    "select",
                    {
                        "options": options,
                        "width": 48,
                        "height": 6,
                        "focused": True,
                        "selectedIndex": selected_index,
                        "showScrollIndicator": True,
                        "showDescription": True,
                        "onSelect": on_select,
                    },
                ),
            ),
            h("ascii_font", {"text": text, "font": font, "width": 50, "height": 6}),
        )


def main() -> None:
    r = Renderer(width=52, height=16, target_fps=30)
    reconcile(h(AsciiDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
