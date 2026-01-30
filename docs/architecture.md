# Architecture

## Overview

```
pytui/
├── core/          # Buffer, layout, render tree, renderer, terminal, keyboard, mouse,
│                  # edit_buffer, editor_view, console, animation, terminal_palette
├── components/    # Text, Box, Input, Select, Textarea, Scrollbox, Code, Diff,
│                  # ASCIIFont, LineNumber, TabSelect, Slider, ScrollBar, FrameBuffer
├── react/         # Component, hooks (useState, useEffect, useRenderer, useResize,
│                  # useKeyboard, useTimeline), create_element/h, reconciler
├── syntax/        # themes, highlighter (optional tree-sitter), languages
├── utils/         # diff_lines, extmarks, scroll_acceleration, validation
└── native/        # Optional Rust extension: Cell, Buffer (maturin develop)
```

## Render flow

1. **Renderer** main loop: `_process_input` → `_check_resize` → `_render_frame` if dirty or scheduled.
2. **\_render_frame**: Clear back_buffer → `root.calculate_layout()` → `root.render(back_buffer)` → `_diff_and_output` → swap buffers.
3. **Renderable tree**: Root is `RootRenderable`; children are Box, Text, etc. Each node has `layout_node` (Yoga or stub), `x/y/width/height`; `render` calls `render_self` then recurses into children.
4. **Output**: First frame full repaint (CLEAR + full screen); later frames only output cells that differ from the previous frame (cursor_to + ANSI).

## Layout

- **LayoutNode**: Wraps yoga-layout (if installed) or a built-in stub. The stub supports width/height, padding, and vertical stacking of children.
- **Stub without Yoga**: Children without an explicit `height` receive the full inner height from the parent, which can push siblings off-screen. In declarative UIs, set `height: 1` on title/hint Text and give content areas (Code, Diff, Scrollbox) explicit heights.
- **Box** with `border=True` sets padding=1 automatically; content is drawn inside the border.

## Declarative API (React-like)

- **Component**: Base class with `props`, `state`, `set_state`, `update()`; subclasses implement `render()` and return a virtual tree.
- **h(type, props, *children)** / **create_element**: Build a virtual node; `type` is `"text"`, `"box"`, `"input"`, `"select"`, `"code"`, `"diff"`, `"scrollbox"`, etc., or a Component subclass.
- **reconcile(elements, container)**: Mount or update the virtual tree into a Renderable container; supports host nodes (text, box, input, select, code, diff, scrollbox, …) and component nodes; component output is mounted as a subtree under the parent.
- **useState / useEffect**: Hook order matches `_hook_state_list` / `_effect_list`. Use **functional setState** (`set_xxx(lambda prev: ...)`) in handlers registered once (e.g. in `useEffect(setup, [])`) to avoid stale state.
- **Event props**: `onInput`, `onChange`, `onSelect`, `onSelectionChanged`, `onScroll` are bound at mount; pass `focused: True` so the reconciler calls `focus()` and components like Select/Scrollbox/Textarea receive keyboard input.
- **Controlled components**: In declarative UIs, pass `selectedIndex` (or `selected`) to Select and scroll state to Scrollbox/Textarea from component state so that re-renders do not reset selection or scroll position.

## Input

- **KeyboardHandler**: Parses stdin (or `/dev/tty` when stdin is not a TTY), emits `keypress` events with `name`, `char`, `ctrl`, `alt`, `shift`. Supports Kitty CSI u and common escape sequences (arrows, Enter, etc.).
- **Focus and keyboard**: Components that must receive arrow keys or Enter (Select, Scrollbox, Textarea) subscribe in `focus()` with `ctx.renderer.keyboard.on("keypress", self._on_keypress)` and remove the listener in `blur()`.
- **MouseHandler**: Parses SGR 1006 mouse sequences, emits `mouse` events. Enable with `use_mouse=True` on the Renderer and feed input through the same path as keyboard.

## Terminal

- **Terminal**: get_size, alternate screen, raw mode, cursor hide/show, mouse enable/disable.
