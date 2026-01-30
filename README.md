# pytui

<p align="center">
  <img src="icon.png" alt="pytui icon" width="80" height="80">
</p>

**pytui** is a Python TUI framework (Option A) based on the [OpenTUI](https://github.com/sst/opentui) architecture. See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for phases and roadmap.

## Features

- **core**: Buffer, ANSI, colors, layout (Yoga or stub), events, renderable, renderer, terminal, keyboard, mouse, console, edit_buffer, editor_view
- **components**: Text, Box, Input, Select, Textarea, Scrollbox, Code, Diff, ASCIIFont, LineNumber, TabSelect, Slider, FrameBuffer
- **react**: Component, useState, useEffect, h(), reconcile (declarative API)
- **syntax**: Themes, highlighter (plain; tree-sitter optional)
- **utils**: diff_lines, extmarks, scroll_acceleration
- **native** (optional): Rust extension `pytui_native` — build with `maturin develop` in `src/pytui/native/`

## Setup

```bash
cd pytui
pip install -e ".[dev]"
# Optional: build native extension
cd src/pytui/native && maturin develop && cd ../../..
```

## Examples

```bash
# Imperative
python examples/hello.py
python examples/counter.py
python examples/login_form.py
python examples/code_viewer.py
python examples/diff_viewer.py
python examples/textarea_demo.py
python examples/dashboard.py

# Declarative (React-style)
python examples/hello_react.py
python examples/counter_react.py
python examples/timer_react.py
python examples/todo_react.py
python examples/ascii_react.py
python examples/opencode_react.py
python examples/scroll_react.py
```

See [examples/README.md](examples/README.md) for the full list and descriptions.

## Tests & Lint

```bash
pytest tests/unit/ tests/integration/ -v
pytest tests/ --cov=src/pytui --cov-report=term-missing --cov-fail-under=70
pytest tests/benchmarks/ --benchmark-only   # benchmarks
ruff check src/ && ruff format src/
```

CI (GitHub Actions) runs on push/PR to `main`/`master`: ruff, pytest (unit + integration), coverage (≥70%).

## Docs

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [OpenTUI vs pytui comparison](docs/opentui-pytui-comparison.md)
- [AGENTS.md](AGENTS.md) — guide for AI agents contributing to this repo
