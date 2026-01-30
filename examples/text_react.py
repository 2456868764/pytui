#!/usr/bin/env python3
"""对应 opentui text.tsx：Color Showcase、Span 颜色/背景、粗体/斜体/下划线、Link、嵌套。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, h, reconcile
from pytui.components.text_node import bold, italic, underline, link, Span


class TextShowcase(Component):
    def render(self):
        return h(
            "box",
            {"width": 72, "height": 24, "border": True, "title": "Color Showcase"},
            h(
                "text_node",
                {
                    "spans": [
                        Span("Red text", fg="#ff0000"),
                        " ",
                        Span("Green text", fg="#00ff00"),
                        " ",
                        Span("Blue text", fg="#0000ff"),
                        " ",
                        Span("Yellow text", fg="#ffff00"),
                        "\n",
                        Span("Magenta", fg="#ff00ff"),
                        " ",
                        Span("Cyan", fg="#00ffff"),
                        " ",
                        Span("White", fg="#ffffff"),
                        "\n",
                        "Background colors:\n",
                        Span("Red on Yellow", fg="#ff0000", bg="#ffff00"),
                        " ",
                        Span("Blue on Green", fg="#0000ff", bg="#00ff00"),
                        " ",
                        Span("White on Magenta", fg="#ffffff", bg="#ff00ff"),
                        "\n",
                        Span("Yellow on Blue", fg="#ffff00", bg="#0000ff"),
                        " ",
                        Span("Green on Red", fg="#00ff00", bg="#ff0000"),
                        " ",
                        Span("Cyan on Black", fg="#00ffff", bg="#000000"),
                        "\n",
                        "Hyperlinks:\n",
                        link("opentui.com", "https://opentui.com", fg="#0000ff"),
                        " - Click if terminal supports OSC 8\n",
                        "Text Formatting:\n",
                        bold("Strong/Bold text"),
                        " - ",
                        italic("Emphasized/Italic text"),
                        " - ",
                        underline("Underlined text"),
                        "\n",
                        bold("Bold yellow", fg="#ffff00"),
                        " - ",
                        italic("Italic green", fg="#00ff00"),
                        " - ",
                        underline("Underlined magenta", fg="#ff00ff"),
                        "\n",
                        "Complex nesting:\n",
                        bold("Bold red with nested", fg="#ff0000"),
                        "\n",
                    ],
                    "width": 70,
                    "height": 22,
                },
            ),
        )


def main() -> None:
    r = Renderer(width=74, height=26, target_fps=30)
    reconcile(h(TextShowcase, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
