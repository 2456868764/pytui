# Getting Started

## Install

```bash
cd pytui
pip install -e ".[dev]"
```

Optional: build the Rust native extension for faster Buffer performance:

```bash
cd src/pytui/native && maturin develop && cd ../../..
```

Optional: enable Tree-sitter syntax highlighting (used by the Code component and `pytui.lib.tree_sitter.highlight`):

```bash
pip install tree-sitter tree-sitter-languages
```

The `tree-sitter-languages` package provides prebuilt parsers for Python, JavaScript, TypeScript, Go, Rust, JSON, HTML, CSS, Bash, C, and C++. Alternatively, you can place compiled `.so` (or `.dll` on Windows) language libraries under your data directory at `tree-sitter/languages/<name>.so`; see `pytui.lib.data_paths.get_data_dir()`. Use `pytui.lib.tree_sitter.list_available_languages()` to see which languages load successfully.

## Minimal example (imperative)

```python
from pytui.core.renderer import Renderer
from pytui.components import Box, Text

r = Renderer(width=40, height=10, target_fps=30)
box = Box(r.context, {"width": 40, "height": 10, "border": True, "title": "Hello"})
box.add(Text(r.context, {"content": "Hello, pytui!", "width": 38, "height": 1}))
r.root.add(box)
r.start()
```

Press `Ctrl+C` to exit.

## Declarative example (React-like)

```python
from pytui.core.renderer import Renderer
from pytui.react import Component, useState, useEffect, useKeyboard, h, reconcile

class Counter(Component):
    def render(self):
        count, set_count = useState(0)
        events = useKeyboard(self.ctx)

        def on_key(key: dict) -> None:
            name = key.get("name") or key.get("char")
            if name == " ":
                set_count(lambda prev: prev + 1)

        def setup() -> None:
            if getattr(self, "_reg", False):
                return
            self._reg = True
            events.on("keypress", on_key)
        useEffect(setup, [])

        return h("box", {"width": 40, "height": 10, "border": True, "title": "Counter"},
                 h("text", {"content": f"Count: {count}  (SPACE +1)", "width": 38, "height": 1}))

r = Renderer(width=40, height=10, target_fps=30)
reconcile(h(Counter, {}), r.root)
r.start()
```

Use **functional setState** (`set_count(lambda prev: prev + 1)`) when the key handler is registered once, so the count updates on every keypress. See [AGENTS.md](../AGENTS.md) for conventions.

## Running examples

See [examples/README.md](../examples/README.md). Common commands:

- `python examples/hello.py` — minimal Box + Text
- `python examples/counter_react.py` — declarative counter
- `python examples/timer_react.py` — timer (SPACE +1 sec)
- `python examples/ascii_react.py` — Select + ASCIIFont
- `python examples/opencode_react.py` — OpenCode-style dialog (Yes/No)
- `python examples/scroll_react.py` — Scrollbox (↑/↓ or j/k to scroll)
- `python examples/line_number_react.py` — Code + line numbers (L/H/D toggle)
- `python examples/diff_react.py` — Diff view
- `python examples/dashboard.py` — dashboard panel

## Tests and benchmarks

```bash
pytest tests/ -v
pytest tests/benchmarks/ --benchmark-only
ruff check src/ && ruff format src/
```

## Next steps

- [Architecture](architecture.md)
- [API Reference](api-reference.md)
- [AGENTS.md](../AGENTS.md) — guide for contributors and AI agents
