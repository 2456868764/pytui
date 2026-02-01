# Aligns with opentui/packages/core/src/examples/lib/standalone-keys.ts
# Common key bindings for demos: ` console, . debug overlay, Shift+L/A/S, Ctrl+G hit grid, etc.

from __future__ import annotations


def setup_common_demo_keys(renderer) -> None:
    """Register common demo key handlers on renderer.key_input (or equivalent)."""
    key_input = getattr(renderer, "key_input", None) or getattr(renderer, "keyboard", None)
    if key_input is None:
        return

    def on_key(key_event):
        name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
        ctrl = getattr(key_event, "ctrl", False) or (key_event.get("ctrl") if isinstance(key_event, dict) else False)
        shift = getattr(key_event, "shift", False) or (key_event.get("shift") if isinstance(key_event, dict) else False)

        if name == "`" or name == '"':
            if hasattr(renderer, "console") and hasattr(renderer.console, "toggle"):
                renderer.console.toggle()
        elif name == ".":
            if hasattr(renderer, "toggle_debug_overlay"):
                renderer.toggle_debug_overlay()
        elif ctrl and name == "g":
            if hasattr(renderer, "dump_hit_grid"):
                renderer.dump_hit_grid()
        elif shift and name == "l":
            if hasattr(renderer, "start"):
                renderer.start()
        elif shift and name == "s":
            if hasattr(renderer, "stop"):
                renderer.stop()
        elif shift and name == "a":
            if hasattr(renderer, "auto"):
                renderer.auto()

    if hasattr(key_input, "on"):
        key_input.on("keypress", on_key)
    elif hasattr(key_input, "subscribe"):
        key_input.subscribe(on_key)
