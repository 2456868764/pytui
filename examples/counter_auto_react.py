#!/usr/bin/env python3
"""对应 opentui counter.tsx：自动递增计数器，每 50ms +1，显示 'N tests passed...'。"""

import time

from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, h, reconcile


class CounterAuto(Component):
    def render(self):
        counter, set_counter = useState(0)

        def setup() -> None:
            last = [time.time()]

            def on_frame(now: float) -> None:
                if now - last[0] >= 0.05:
                    set_counter(lambda c: c + 1)
                    last[0] = now

            r = self.ctx.renderer
            if hasattr(r, "events") and r.events:
                r.events.on("frame", on_frame)
            return None

        useEffect(setup, [])

        return h(
            "text",
            {"content": f"{counter} tests passed...", "fg": "#00FF00", "width": 40, "height": 1},
        )


def main() -> None:
    r = Renderer(width=50, height=5, target_fps=20)
    reconcile(h(CounterAuto, {}), r.root)
    r.start()


if __name__ == "__main__":
    main()
