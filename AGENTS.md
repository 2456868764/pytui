# AGENTS.md – pytui

Project guide for AI agents: when modifying or extending this repository, follow this document and [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md).

---

## What the project is

- **pytui**: A Python TUI framework implementing **Option A** based on the [OpenTUI](https://github.com/sst/opentui) architecture.
- Goal: Implement the `src/pytui` package under `pytui/`, including core rendering, Yoga layout, component library, and declarative API, with unit and integration tests.
- Implementation details and code examples follow **[opentui/PYTHON_IMPLEMENTATION_GUIDE.md](./PYTHON_IMPLEMENTATION_GUIDE.md)**.

---

## Key documents

| Document | Purpose |
|----------|---------|
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Implementation phases, steps, unit/integration test plan, acceptance criteria |
| [../opentui/PYTHON_IMPLEMENTATION_GUIDE.md](./PYTHON_IMPLEMENTATION_GUIDE.md) | Option A tech stack, directory layout, per-module code examples |
| [examples/README.md](./examples/README.md) | Example list and run commands |
| This file (AGENTS.md) | Agent collaboration rules and usage guide |

---

## Directories and responsibilities

- **`src/pytui/`**: Main package.  
  - `core/`: buffer, ansi, colors, layout, events, renderable, renderer, terminal, keyboard, mouse, edit_buffer, editor_view, etc.  
  - `native/`: Rust extension (PyO3/maturin), optional; core falls back to pure Python when native is absent.  
  - `components/`: Text, Box, Input, Select, Textarea, Scrollbox, Code, Diff, ASCIIFont, LineNumber, TabSelect, Slider, FrameBuffer, etc.  
  - `syntax/`: Tree-sitter syntax highlighting and themes.  
  - `react/`: Declarative API (Component, useState/useEffect, Reconciler, h/create_element).  
  - `utils/`: diff, extmarks, scroll_acceleration, and other utilities.
- **`tests/`**:  
  - `conftest.py`: Shared fixtures (buffer_10x5, mock_context, etc.).  
  - `unit/`: Unit tests by module (e.g. `unit/core/test_buffer.py`).  
  - `integration/`: End-to-end scenarios (Hello, layout, forms, React flow).  
  - `benchmarks/`: Performance benchmarks (optional).
- **`examples/`**: Runnable examples.  
  - Imperative: hello, counter, login_form, code_viewer, diff_viewer, textarea_demo, dashboard, etc.  
  - Declarative (React-style): hello_react, counter_react, timer_react, todo_react, basic_react, ascii_react, opencode_react, line_number_react, diff_react, scroll_react, etc.; see `examples/README.md`.

When adding features: implement in the corresponding `src/pytui` subpackage and add or update tests under `tests/unit` or `tests/integration`; follow IMPLEMENTATION_PLAN.md for order and scope.

---

## Technical conventions

- **Python**: 3.11+, type hints, prefer `typing` / `typing-extensions`.
- **Style**: ruff (lint + format), line-length 120, target py311.
- **Type checking**: mypy strict (if configured).
- **Testing**: pytest; new logic should have matching unit or integration tests; use `pytest.importorskip("pytui...")` to skip when the package is not installed.
- **Dependencies**: See `pyproject.toml`; optional features via optional-dependencies (yoga, syntax, full, dev).

---

## Common commands

```bash
# Install (development)
cd pytui && pip install -e ".[dev]"

# If using Rust native layer
maturin develop

# Tests
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/ --cov=src/pytui --cov-report=term-missing

# Code quality
ruff check src/ && ruff format src/
mypy src/   # if configured
```

---

## Notes when changing or adding code

1. **Check the plan first**: Before implementing a new phase or module, refer to [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) phases and steps to avoid missing dependencies or tests.
2. **Implementation reference**: API and code structure follow the Option A examples in [opentui/PYTHON_IMPLEMENTATION_GUIDE.md](../opentui/PYTHON_IMPLEMENTATION_GUIDE.md).
3. **Testing**:  
   - Put unit tests under `tests/unit/` mirroring the package layout;  
   - Put integration tests under `tests/integration/`; they should not depend on a real TTY and can use mocks or in-memory buffers.
4. **Compatibility**: The core layer must work without `pytui_native` (e.g. buffer’s `use_native=False`).
5. **Docs**: When making significant API or directory changes, update IMPLEMENTATION_PLAN.md and this AGENTS.md if structure or commands are affected.

---

## Implementation and debugging conventions (recent experience)

- **Layout (stub, no Yoga)**: Children without an explicit `height` receive the full inner height from the parent, so siblings below are pushed off-screen. In declarative examples, set `height: 1` on title/hint Text nodes and give content areas (Code, Diff, Scrollbox) explicit heights.
- **React state and keypress**: A keypress handler registered once in `useEffect(setup, [])` closes over the initial render’s state. Use **functional setState**: `set_xxx(lambda prev: prev + 1)` or `set_xxx(lambda prev: prev[:-1] if prev else prev)` to avoid “only add/remove once” behavior.
- **Focus and keyboard**: Components that must reliably receive arrow keys or Enter (Select, Scrollbox, Textarea) should in `focus()` subscribe with `ctx.renderer.keyboard.on("keypress", self._on_keypress)` and call `remove_listener` in `blur()`; in examples use `focused: True` so the reconciler calls `focus()` on mount.
- **Controlled Select**: When using Select in React, re-renders remount it; pass the current selection back via `selectedIndex` (or `selected`) synced with state, or the highlight will reset to the first item after each setState.
- **Debugging**: Set the environment variable `PYTUI_DEBUG=1` to enable stderr logging on the renderer, keyboard, and select paths for troubleshooting key and event flow.

Following these conventions keeps the codebase aligned with Option A and the current test plan and makes future changes and collaboration easier.
