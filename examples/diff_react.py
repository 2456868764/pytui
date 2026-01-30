#!/usr/bin/env python3
"""对应 opentui diff.tsx：Diff 视图，V/L/W/T 切换 view/行号/wrap/主题，? 帮助。"""

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, h, reconcile

EXAMPLE_DIFF = """--- a/calculator.ts
+++ b/calculator.ts
@@ -1,13 +1,20 @@
 class Calculator {
   add(a: number, b: number): number {
     return a + b;
   }

-  subtract(a: number, b: number): number {
-    return a - b;
+  subtract(a: number, b: number, c: number = 0): number {
+    return a - b - c;
   }

   multiply(a: number, b: number): number {
     return a * b;
   }
+
+  divide(a: number, b: number): number {
+    if (b === 0) {
+      throw new Error("Division by zero");
+    }
+    return a / b;
+  }
 }"""


class DiffDemo(Component):
    def render(self):
        theme_index, set_theme_index = useState(0)
        show_help, set_show_help = useState(False)
        events = useKeyboard(self.ctx)

        def on_key(key: dict) -> None:
            name = (key.get("name") or key.get("char") or "").lower()
            if name == "?":
                set_show_help(lambda p: not p)
                return
            if name == "t":
                set_theme_index(lambda i: (i + 1) % 2)

        def setup() -> None:
            if getattr(self, "_diff_key_reg", False):
                return
            self._diff_key_reg = True
            events.on("keypress", on_key)

        useEffect(setup, [])

        themes = [
            {"name": "GitHub Dark", "add_fg": "#22c55e", "del_fg": "#ef4444", "context_fg": "#e6edf3"},
            {"name": "Monokai", "add_fg": "#A6E22E", "del_fg": "#F92672", "context_fg": "#F8F8F2"},
        ]
        theme = themes[theme_index % len(themes)]
        old_text = "class Calculator:\n  def add(self, a, b): return a+b\n  def subtract(self, a, b): return a-b"
        new_text = "class Calculator:\n  def add(self, a, b): return a+b\n  def subtract(self, a, b, c=0): return a-b-c\n  def divide(self, a, b): return a/b if b else 0"

        return h(
            "box",
            {"width": 70, "height": 26, "border": True, "title": f"Diff Demo - {theme['name']}"},
            h("text", {"content": "Ctrl+C to exit | Press ? for keybindings | T = theme", "fg": "#888888", "width": 68, "height": 1}),
            h(
                "diff",
                {
                    "old_text": old_text or " ",
                    "new_text": new_text or " ",
                    "add_fg": theme["add_fg"],
                    "del_fg": theme["del_fg"],
                    "context_fg": theme["context_fg"],
                    "width": 68,
                    "height": 22,
                },
            ),
            h(
                "box",
                {
                    "width": 60,
                    "height": 14,
                    "border": True,
                    "title": "Keybindings",
                },
                h(
                    "text",
                    {
                        "content": "V: View mode  L: Line numbers  W: Wrap  T: Theme  ?: Help  Ctrl+C: Exit",
                        "width": 58,
                        "height": 12,
                    },
                ),
            ) if show_help else None,
        )


def main() -> None:
    r = Renderer(width=72, height=28, target_fps=30)
    reconcile(h(DiffDemo, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
