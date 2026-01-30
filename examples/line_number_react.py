#!/usr/bin/env python3
"""对应 opentui line-number.tsx：LineNumber + Code，L/H/D 切换行号、diff 高亮、诊断。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, h, reconcile

CODE_CONTENT = """function fibonacci(n: number): number {
  if (n <= 1) return n
  return fibonacci(n - 1) + fibonacci(n - 2)
}

const results = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  .map(fibonacci)

console.log('Fibonacci sequence:', results)

// Calculate the sum
const sum = results.reduce((acc, val) => acc + val, 0)
console.log('Sum:', sum)

// Find even numbers
const evens = results.filter(n => n % 2 === 0)
console.log('Even numbers:', evens)"""


class LineNumberDemo(Component):
    def render(self):
        show_line_numbers, set_show_line_numbers = useState(True)
        show_diff, set_show_diff = useState(False)
        show_diagnostics, set_show_diagnostics = useState(False)
        events = useKeyboard(self.ctx)

        def on_key(key: dict) -> None:
            name = (key.get("name") or key.get("char") or "").lower()
            if name == "l":
                set_show_line_numbers(lambda x: not x)
            elif name == "h":
                set_show_diff(lambda x: not x)
            elif name == "d":
                set_show_diagnostics(lambda x: not x)

        def setup() -> None:
            if getattr(self, "_ln_reg", False):
                return
            self._ln_reg = True
            events.on("keypress", on_key)

        useEffect(setup, [])

        return h(
            "box",
            {"width": 70, "height": 28, "border": True, "flex_direction": "column"},
            h("text", {"content": "Line Numbers Demo", "fg": "#4ECDC4", "width": 68, "height": 1}),
            h("text", {"content": "L - Toggle line numbers  H - Diff  D - Diagnostics", "fg": "#888888", "width": 68, "height": 1}),
            h(
                "box",
                {"width": 68, "height": 24, "border": True, "border_style": "single", "background_color": "#0D1117"},
                h(
                    "code",
                    {
                        "content": CODE_CONTENT,
                        "language": "typescript",
                        "width": 66,
                        "height": 20,
                        "show_line_numbers": show_line_numbers,
                        "show_diff": show_diff,
                        "show_diagnostics": show_diagnostics,
                        "diagnostics": [(1, "error"), (4, "warning"), (8, "warning")],
                    },
                ),
            ),
        )


def main() -> None:
    r = Renderer(width=72, height=30, target_fps=30)
    reconcile(h(LineNumberDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
