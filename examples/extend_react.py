#!/usr/bin/env python3
"""对应 opentui extend-example.tsx：自定义组件（继承 Box 的 ConsoleButton），extend 注册后用 h('consoleButton') 渲染。
pytui 无 extend API，用 Component 包装一个带 label 的 Box 模拟。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, h, reconcile


class ConsoleButton(Component):
    """模拟 opentui 的 ConsoleButton：带 label 的 Box，居中显示文字。"""

    def render(self):
        label = self.props.get("label", "Button")
        return h(
            "box",
            {
                "width": 24,
                "height": 5,
                "border": True,
                "border_style": "single",
                "background_color": "#008000",
                "title": label,
            },
            h("text", {"content": label, "width": 22}),
        )


def main() -> None:
    r = Renderer(width=28, height=8, target_fps=30)
    # 使用 Component 子类作为类型，等同于 extend 后使用
    reconcile(h(ConsoleButton, {"label": "Another Button"}), r.root)
    r.start()


if __name__ == "__main__":
    main()
