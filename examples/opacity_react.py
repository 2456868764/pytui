#!/usr/bin/env python3
"""对应 opentui opacity.tsx：四层 Box 透明度切换，A 自动动画，1-4 键切换单框透明度。
pytui 的 buffer 支持 alpha 混合，但 Box 无 opacity 属性；演示 1-4 切换「高亮」状态（用背景色深浅模拟）。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, useTimeline, h, reconcile

COLORS = ["#e94560", "#0f3460", "#533483", "#16a085"]


class OpacityDemo(Component):
    def render(self):
        animating, set_animating = useState(False)
        opacities, set_opacities = useState([1.0, 0.8, 0.5, 0.3])
        timeline = useTimeline(self.ctx)
        phase = timeline["elapsed"] * 0.5
        events = useKeyboard(self.ctx)

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "a":
                set_animating(lambda x: not x)
            elif name == "1":
                set_opacities(lambda p: [0.3 if p[0] == 1.0 else 1.0, p[1], p[2], p[3]])
            elif name == "2":
                set_opacities(lambda p: [p[0], 0.3 if p[1] == 1.0 else 1.0, p[2], p[3]])
            elif name == "3":
                set_opacities(lambda p: [p[0], p[1], 0.3 if p[2] == 1.0 else 1.0, p[3]])
            elif name == "4":
                set_opacities(lambda p: [p[0], p[1], p[2], 0.3 if p[3] == 1.0 else 1.0])

        def setup() -> None:
            if getattr(self, "_op_reg", False):
                return
            self._op_reg = True
            events.on("keypress", lambda k: None)

        useEffect(setup, [])

        import math
        if animating:
            op = [
                0.3 + 0.7 * abs(math.sin(phase)),
                0.3 + 0.7 * abs(math.sin(phase + 0.5)),
                0.3 + 0.7 * abs(math.sin(phase + 1.0)),
                0.3 + 0.7 * abs(math.sin(phase + 1.5)),
            ]
        else:
            op = opacities if isinstance(opacities, (list, tuple)) else [1.0, 0.8, 0.5, 0.3]

        return h(
            "box",
            {"width": 72, "height": 20, "border": False, "flex_direction": "column"},
            h(
                "box",
                {"width": 70, "height": 3, "background_color": "#16213e", "border": True, "title": "Opacity Demo"},
                h("text", {"content": "1-4: Toggle  A: Animate  Ctrl+C: Exit", "fg": "#e94560", "width": 68}),
            ),
            h(
                "box",
                {"width": 70, "height": 14, "flex_direction": "row"},
                *[
                    h(
                        "box",
                        {
                            "width": 16,
                            "height": 8,
                            "background_color": COLORS[i],
                            "border": True,
                            "border_style": "double",
                            "title": f"Box {i+1}",
                        },
                        h("text", {"content": f"Box {i+1}", "fg": "#ffffff"}),
                        h("text", {"content": f"Opacity: {op[i]:.1f}", "fg": "#ffffff"}),
                    )
                    for i in range(4)
                ],
            ),
        )


def main() -> None:
    r = Renderer(width=74, height=22, target_fps=30)
    reconcile(h(OpacityDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
