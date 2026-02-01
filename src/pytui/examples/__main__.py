# python -m pytui.examples [name]
# If name is given: run that example and block until exit (Ctrl+C).
# If no name: start TUI selector menu (up/down, Enter run, Esc exit).

from __future__ import annotations

import sys

from pytui.examples.registry import EXAMPLES, destroy_example, get_example_names, run_example


def main() -> int:
    args = sys.argv[1:]
    from pytui.core.console import Console
    from pytui.examples.lib.standalone_keys import setup_common_demo_keys

    console = Console(use_mouse=False)
    renderer = console.renderer
    setup_common_demo_keys(renderer)

    if not args:
        from pytui.examples.selector_demo import destroy_selector, run_selector
        while True:
            run_selector(renderer)
            try:
                console.run()
            except KeyboardInterrupt:
                pass
            name = getattr(renderer, "_example_to_run", None)
            destroy_selector(renderer)
            if name is None:
                break
            run, _destroy, _desc = EXAMPLES.get(name, (None, None, ""))
            if run is None:
                break
            run(renderer)
            try:
                console.run()
            except KeyboardInterrupt:
                pass
            destroy_example(name, renderer)
        renderer.destroy()
        return 0

    name = args[0]
    if name not in EXAMPLES:
        print(f"Unknown example: {name}", file=sys.stderr)
        return 1

    run, _destroy, desc = EXAMPLES[name]
    if run is None:
        print(f"{name}: {desc}")
        print("(Not implemented or N/A for TUI)")
        return 0

    run(renderer)
    try:
        console.run()
    except KeyboardInterrupt:
        pass
    finally:
        destroy_example(name, renderer)
        renderer.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
