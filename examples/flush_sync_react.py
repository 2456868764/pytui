#!/usr/bin/env python3
"""对应 opentui flush-sync.tsx：'a' 批量更新（一次渲染），'s' 逐次更新（三次渲染），展示 flushSync 差异。
pytui 无 flushSync，演示 a/b/c 三数 + 渲染次数显示；'a' 一次加三个，'s' 分三次加。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, h, reconcile


class FlushSyncDemo(Component):
    def render(self):
        a, set_a = useState(0)
        b, set_b = useState(0)
        c, set_c = useState(0)
        log, set_log = useState([])
        events = useKeyboard(self.ctx)
        if not hasattr(self, "_render_count"):
            self._render_count = 0
        self._render_count += 1

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == "q":
                self.ctx.renderer.stop()
                return
            if name == "a":
                before = self._render_count
                set_a(lambda x: x + 1)
                set_b(lambda x: x + 1)
                set_c(lambda x: x + 1)
                set_log(lambda l: list(l)[-4:] + [f"batched: renders {before} -> (batch)"])
            if name == "s":
                before = self._render_count
                set_a(lambda x: x + 1)
                set_b(lambda x: x + 1)
                set_c(lambda x: x + 1)
                set_log(lambda l: list(l)[-4:] + [f"sequential: renders {before} -> (+3)"])

        def setup() -> None:
            if getattr(self, "_fs_reg", False):
                return
            self._fs_reg = True
            events.on("keypress", on_key)

        useEffect(setup, [])

        log_list = list(log)[-5:] if isinstance(log, (list, tuple)) else []
        return h(
            "box",
            {"width": 58, "height": 16, "border": True, "title": "flushSync Demo"},
            h("text", {"content": "'a' = batched | 's' = sequential | 'q' = quit", "fg": "#666666", "width": 56}),
            h("text", {"content": f"a={a} b={b} c={c}  (renders: {self._render_count})", "fg": "#00FF00", "width": 56}),
            h(
                "box",
                {"title": "Log", "border": True, "width": 56, "height": 8},
                *[h("text", {"content": line, "fg": "#00FFFF" if "sequential" in str(line) else "#FF8800", "width": 54}) for line in log_list],
            ),
        )


def main() -> None:
    r = Renderer(width=60, height=18, target_fps=30)
    reconcile(h(FlushSyncDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
