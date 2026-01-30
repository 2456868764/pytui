# OpenTUI vs pytui – Feature comparison

> Comparison of OpenTUI (TypeScript/Zig) and pytui (Python) implementations.  
> Last updated: after Phase 7–11 and recent component updates.

---

## 1. Overview

| Aspect | OpenTUI (TS/Zig) | pytui (Python) | Notes |
|--------|------------------|----------------|-------|
| **Runtime** | Bun / Node | CPython 3.11+ | - |
| **Native layer** | Zig (FFI) | Rust + PyO3 (optional) | pytui falls back to pure Python Buffer when native is absent |
| **Layout** | Yoga binding | poga optional / stub | pytui stub supports padding, vertical stacking |
| **Declarative** | React + Solid reconciler | Component + h() + reconcile | pytui is React-like only; Solid is placeholder |
| **Syntax highlighting** | Tree-sitter (WASM) + multi-language | Tree-sitter optional, syntax/languages placeholder | pytui does not ship prebuilt language bundles |

---

## 2. Core

| Capability | OpenTUI | pytui | Status |
|------------|---------|-------|--------|
| **Renderer** | createCliRenderer, start/stop, FPS | Renderer, start/stop, target_fps, terminal=, render_once() | ✅ Aligned |
| **Double buffer / output** | FrameBuffer, diff output | OptimizedBuffer, full first frame + diff | ✅ Aligned |
| **Renderable tree** | BaseRenderable, add/remove, layout, render | Renderable, add/remove, calculate_layout, render | ✅ Aligned |
| **Layout** | Yoga, position/flex/margins | LayoutNode, poga or stub (width/height/padding) | ✅ Present; stub has no full flex |
| **Terminal** | size, alternate screen, raw, cursor, mouse | Terminal, same | ✅ Aligned |
| **Keyboard** | KeyHandler, keypress/paste, Kitty | KeyboardHandler, keypress, Kitty CSI u | ✅ Present; Kitty supported |
| **Mouse** | parse.mouse, MouseEvent | MouseHandler, SGR 1006, mouse event | ✅ Present |
| **Colors** | RGBA, fromHex/fromInts, parseColor | parse_color, RGBA (from_hex/from_ints/from_values) | ✅ Present |
| **ANSI** | cursor, colors, screen control | ANSI, cursor_to, rgb_fg/bg, CLEAR, etc. | ✅ Aligned |
| **Events** | EventEmitter, RenderContext | pyee, EventBus, ctx | ✅ Aligned |
| **Console** | overlay, capture console.log, position/size | ConsoleBuffer, ConsoleOverlay, capture_stdout | ✅ Present |
| **Buffer** | setCell, drawText, fillRect, alpha | set_cell, draw_text, fill_rect, blend_color, set_cell_with_alpha | ✅ Present |
| **EditBuffer / EditorView** | Edit buffer and view | EditBuffer, EditorView (viewport, cursor, selection, undo/redo) | ✅ Implemented |
| **Animation** | Timeline | Timeline (core/animation), useTimeline hook | ✅ Implemented |
| **Post filters** | post/filters | post/filters (apply_dim, apply_blur_placeholder) | ✅ Placeholder implemented |
| **Terminal palette** | terminal-palette | core/terminal_palette (detect_capability, get_palette_color) | ✅ Implemented |

---

## 3. Components – Feature comparison

### 3.1 Component overview

| Component | OpenTUI | pytui | Status |
|-----------|---------|-------|--------|
| **Text** | TextRenderable, StyledText/TextNode | Text, content/fg/bg/bold/italic/underline | ✅ Present; no Link (use TextNode+link) |
| **TextNode** | TextNode, Span, Bold/Italic/Underline, LineBreak, Link | TextNode, Span, bold/italic/underline/line_break/link | ✅ Implemented |
| **Box** | Box, border, title, background | Box, border, border_style, title, padding | ✅ Aligned |
| **Input** | value, placeholder, cursor, input/change/enter, keyBindings, maxLength | value, placeholder, cursor, input/change/enter, keyBindings | ✅ Present |
| **Select** | options, selectedIndex, description, font, keyBindings, wrapSelection | options, selectedIndex, showDescription, keyBindings, wrapSelection, showScrollIndicator | ✅ Present; focus() listens on keyboard for up/down/enter |
| **TabSelect** | TabSelect, tabs, selection event | TabSelect, tabs, onSelect | ✅ Implemented |
| **Textarea** | Multi-line, scroll, selection, undo/redo, highlight, extmarks, keyBindings | Multi-line, scroll, buffer/editor_view, cursor/selection, undo/redo; focus() for up/down scroll when no editor_view | ✅ Present; extmarks store/style_map options; keyboard on focus |
| **ScrollBox** | ScrollBox, viewport scroll | Scrollbox, scroll_x/scroll_y, focus() for up/down/j/k | ✅ Present; render() applies scroll offset and viewport clip |
| **ScrollBar** | ScrollBar (standalone) | ScrollBar, scroll_max, scroll_value | ✅ Implemented |
| **LineNumber** | LineNumberRenderable | LineNumber, line_count, scroll_offset | ✅ Implemented |
| **Code** | Code, syntax highlight + line numbers | Code, highlight + line numbers, show_diff, show_diagnostics, diagnostics | ✅ Present |
| **Diff** | Diff, add/remove/context lines | Diff, diff_lines + add/del/context | ✅ Aligned |
| **Slider** | Slider, min/max/step, events | Slider, min/max/value/step, onScroll/change | ✅ Implemented |
| **ASCIIFont** | ASCIIFont, multiple fonts, selection | ASCIIFont, tiny/block/slick/shade, load_font_from_json, register_font, selectable, selectionBg/Fg | ✅ Implemented |
| **FrameBuffer** | Renderable canvas | FrameBuffer, get_buffer, blit on render | ✅ Implemented |
| **Composition** | VRenderable, constructs, vnode | None | ⚠️ pytui uses h() instead |

### 3.2 Input

| Feature | OpenTUI | pytui |
|---------|---------|-------|
| value / placeholder | Yes | Yes |
| cursor position | Yes | Yes |
| events input/change | Yes | Yes |
| event enter | Yes | Yes (emit on Enter) |
| Backspace/DEL/arrows/printable | keyBindings | Handled in component |
| keyBindings configurable | Yes | Yes |
| maxLength | Yes | Yes |
| placeholderColor / cursorStyle | Yes | Yes (placeholderColor, cursorStyle) |

### 3.3 Select

| Feature | OpenTUI | pytui |
|---------|---------|-------|
| options | SelectOption[] (name/description/value) | list[str] or list[{name, description?, value?}] |
| selectedIndex | Yes | selectedIndex / selected |
| up/down / j/k | keyBindings | Built-in when focused (keyboard listener) |
| event selectionChanged/itemSelected | Yes | select (index, name, value) |
| description, showDescription | Yes | Yes |
| ASCIIFont per option | Optional font | No (plain text options) |
| wrapSelection / fastScrollStep | Yes | Yes |
| showScrollIndicator | Yes | Yes |

### 3.4 Textarea

| Feature | OpenTUI | pytui |
|---------|---------|-------|
| Multi-line / scroll | Yes | Yes |
| Bind EditBuffer/EditorView | EditBufferRenderable | buffer / editor_view options |
| Cursor and selection drawing | Yes | Yes (when editor_view provided) |
| undo/redo | Yes | Yes (delegated to buffer/editor_view) |
| Key bindings (move, select, delete, undo) | Built-in keyBindings | Built-in when editor_view; when no editor_view, up/down/page scroll only |
| Syntax highlight / theme | StyledText/highlight | syntax_language, syntax_theme options |
| extmarks | ExtmarksController | extmarks_store, extmark_style_map options |

### 3.5 ScrollBox / ScrollBar / LineNumber

| Feature | OpenTUI | pytui |
|---------|---------|-------|
| ScrollBox viewport scroll | Yes | Scrollbox, scroll_x/scroll_y; focus() for up/down/j/k |
| ScrollBar standalone | ScrollBar | ScrollBar, scroll_max, scroll_value |
| LineNumber + content | LineNumberRenderable | LineNumber, line_count, scroll_offset |
| Scroll acceleration | scroll-acceleration | utils/scroll_acceleration (Linear/MacOS), optional on Scrollbox |

### 3.6 Code / Diff

| Feature | OpenTUI | pytui |
|---------|---------|-------|
| Code syntax + line numbers | Yes | Code, highlighter, line numbers, show_diff, show_diagnostics, diagnostics |

---

## 4. Declarative API (React / Solid)

| Capability | OpenTUI | pytui | Notes |
|------------|---------|-------|------|
| **React** | React reconciler, host-config, JSX | Component, h(), reconcile, TYPE_MAP | ✅ Present |
| **Solid** | Solid reconciler, createComponent, control flow | react/solid_placeholder placeholder | ⚠️ Placeholder only |
| **Component** | props/state | Component, props, state, set_state, update | ✅ Present |
| **Hooks** | useEvent, useKeyboard, useRenderer, useResize, useTerminalDimensions, useTimeline | useState, useEffect, useRenderer, useResize, useKeyboard, useTimeline | ✅ Common hooks implemented |
| **createElement / h** | JSX, type → Renderable | h(type, props, *children), TYPE_MAP | ✅ Present |
| **Event props onXxx** | onInput, onChange, onSelect, etc. | onInput, onChange, onSelect, onSelectionChanged, onScroll bound at mount | ✅ Implemented |
| **focused** | Focus management | focused: True on host so reconciler calls focus(); Select/Scrollbox/Textarea listen on keyboard when focused | ✅ Implemented |

---

## 5. Syntax highlighting and themes

| Capability | OpenTUI | pytui | Notes |
|------------|---------|-------|------|
| **Tree-sitter** | TreeSitterClient, WASM, multi-language | syntax/languages (get_language, get_parser) optional | ⚠️ No prebuilt language bundles |
| **Themes / styles** | SyntaxStyle, convertThemeToStyles | themes, syntax/style (SyntaxStyle, convert_theme_to_styles) | ✅ Present |
| **StyledText** | styled-text, tree-sitter-styled-text | highlighter returns (text, token_type) | ✅ Concept aligned |

---

## 6. Utils and lib

| Capability | OpenTUI | pytui | Notes |
|------------|---------|-------|------|
| **Diff** | Line diff | diff_lines, LCS | ✅ Present |
| **Validation** | renderable.validations | validate_positive_int, validate_hex_color, etc. | ✅ Present |
| **RGBA** | RGBA, fromHex/fromInts | core/rgba (RGBA, from_hex/from_ints/from_values) | ✅ Present |
| **Key parsing** | parse.keypress, Kitty | KeyboardHandler, Kitty CSI u | ✅ Present |
| **Mouse parsing** | parse.mouse | MouseHandler, SGR 1006 | ✅ Present |
| **Scroll acceleration** | scroll-acceleration | utils/scroll_acceleration (Linear, MacOS) | ✅ Implemented |
| **extmarks** | extmarks, ExtmarksController | utils/extmarks (Extmark, ExtmarksStore); Textarea options | ✅ Extension point; Textarea accepts store/style_map |
| **Terminal palette** | terminal-palette | core/terminal_palette | ✅ Implemented |
| **data-paths** | data-paths | utils/data_paths (get_data_dir, get_cache_dir, etc.) | ✅ Implemented |
| **ASCII fonts** | ascii.font, multiple JSON | components/ascii_font (TINY_FONT, BLOCK_FONT, load_font_from_json, register_font) | ✅ Implemented |
| **Selection** | selection (text selection) | EditorView selection, Textarea selection drawing | ⚠️ Selection in EditorView/Textarea; no standalone selection lib |

---

## 7. Testing and CI

| Capability | OpenTUI | pytui | Notes |
|------------|---------|-------|------|
| **Unit tests** | Jest | pytest, tests/unit/* | ✅ Present |
| **Integration tests** | Partial | tests/integration/* | ✅ Present |
| **Benchmarks** | benchmark/ | pytest-benchmark | ✅ Present |
| **TestRenderer** | createTestRenderer, no TTY | create_test_renderer, MockTerminal, render_once | ✅ Implemented |
| **Mock input** | createMockKeys, createMockMouse | create_mock_keys, create_mock_mouse | ✅ Implemented |
| **Snapshot** | Jest snapshot | buffer_snapshot_lines, assert_buffer_snapshot | ✅ Custom |
| **CI** | build-core, etc. | .github/workflows, ruff + pytest + cov | ✅ Present |

---

## 8. Summary

| Category | Status | Notes |
|----------|--------|-------|
| **Core render and layout** | ✅ Covered | Including EditBuffer/EditorView, Timeline, post, Console overlay, Buffer alpha, terminal palette |
| **Base components** | ✅ Covered | Text, TextNode, Box, Input, Select, TabSelect, Textarea, Scrollbox, ScrollBar, LineNumber, Code, Diff, Slider, ASCIIFont, FrameBuffer |
| **Declarative API** | ✅ Covered (React-like) | useState, useEffect, useRenderer, useResize, useKeyboard, useTimeline, h(), reconcile, onXxx, focused |
| **Syntax highlighting** | ⚠️ Partial | themes, SyntaxStyle; Tree-sitter optional, no prebuilt bundles |
| **Utils and extensions** | ✅ Covered | extmarks, data_paths, scroll_acceleration, terminal_palette, ascii_font |
| **Testing and CI** | ✅ Covered | TestRenderer, MockKeys, MockMouse, Snapshot, CI |

pytui is **largely aligned** with OpenTUI on component set and core capabilities. Remaining gaps are mainly **component details** (e.g. Input/Select/Textarea keyBindings and options are now implemented; extmarks are optional on Textarea), **Solid/Composition**, and **Tree-sitter language bundles**. See [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) for Phase 12+ candidates.
