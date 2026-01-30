#!/usr/bin/env python3
"""OpenCode 风格 demo：顶部信息、中央 Initialize Project 对话框（Yes/No）、底部状态栏。
参考 OpenCode 界面：↑/↓ 选 Yes/No，Enter 确认。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, h, reconcile


class OpenCodeDemo(Component):
    def render(self):
        choice, set_choice = useState(None)  # None | "yes" | "no"

        options = [
            {"name": "Yes", "description": "", "value": "yes"},
            {"name": "No", "description": "", "value": "no"},
        ]
        selected_index = next((i for i, o in enumerate(options) if o["value"] == (choice or "yes")), 0)

        def on_select(_idx: int, _n: str, value: str) -> None:
            set_choice(value if value in ("yes", "no") else "yes")

        # 顶部信息区
        top_lines = [
            "OpenCode v8.8.44",
            "https://github.com/opencode-ai/opencode",
            "cwd: /Users/you/src/glow",
            "LSP Configuration",
        ]

        # 对话框正文
        dialog_body = (
            "Initialization generates a new OpenCode.md file that contains\n"
            "information about your codebase, this file serves as memory\n"
            "for each project, you can freely add to it to help the agents\n"
            "be better at their job.\n"
            "\n"
            "Would you like to initialize this project?"
        )
        result_line = "→ Initializing..." if choice == "yes" else ("→ Skipped." if choice == "no" else "")
        dialog_content = [
            h("text", {"content": dialog_body, "fg": "#cccccc", "width": 60, "height": 8}),
            h(
                "select",
                {
                    "options": options,
                    "width": 60,
                    "height": 2,
                    "focused": True,
                    "selectedIndex": selected_index,
                    "showScrollIndicator": False,
                    "showDescription": False,
                    "selected_fg": "#000000",
                    "selected_bg": "#ff8800",
                    "onSelect": on_select,
                },
            ),
        ]
        if result_line:
            dialog_content.append(
                h("text", {"content": result_line, "fg": "#22aa22" if choice == "yes" else "#888888", "width": 60, "height": 1})
            )

        return h(
            "box",
            {
                "width": 72,
                "height": 26,
                "border": True,
                "border_style": "single",
                "padding": 1,
            },
            # 顶部
            h("text", {"content": top_lines[0], "fg": "#cccccc", "width": 70, "height": 1}),
            h("text", {"content": top_lines[1], "fg": "#888888", "width": 70, "height": 1}),
            h("text", {"content": top_lines[2], "fg": "#888888", "width": 70, "height": 1}),
            h("text", {"content": top_lines[3], "fg": "#ff8800", "width": 70, "height": 1}),
            h("text", {"content": "", "width": 70, "height": 1}),
            # 中央对话框（Enter 确认后显示 → Initializing... / → Skipped.）
            h(
                "box",
                {
                    "width": 62,
                    "height": 14,
                    "border": True,
                    "border_style": "single",
                    "title": "Initialize Project",
                    "border_color": "#ff8800",
                    "padding": 1,
                },
                *dialog_content,
            ),
            h("text", {"content": "", "width": 70, "height": 1}),
            # 底部状态栏
            h(
                "text",
                {
                    "content": "press `enter` to send the message, write `\\` and `enter` to add a new line",
                    "fg": "#666666",
                    "width": 70,
                    "height": 1,
                },
            ),
            h("text", {"content": "> ", "fg": "#888888", "width": 70, "height": 1}),
            h(
                "text",
                {
                    "content": "ctrl+? help" + " " * 40 + "No diagnostics" + " " * 6 + "Claude 3.7 Sonnet",
                    "fg": "#666666",
                    "width": 70,
                    "height": 1,
                },
            ),
        )


def main() -> None:
    r = Renderer(width=72, height=26, target_fps=30)
    reconcile(h(OpenCodeDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
