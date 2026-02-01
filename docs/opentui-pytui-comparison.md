# OpenTUI vs pytui – Feature comparison

> Comparison of OpenTUI (TypeScript/Zig) and pytui (Python) implementations.  
> Last updated: based on latest code in both repos.  
> OpenTUI docs: [Getting started](https://opentui.com/docs/getting-started/), [Layout](https://opentui.com/docs/core-concepts/layout/), [Components](https://opentui.com/docs/getting-started/).

---

## 0. Alignment with OpenTUI Getting Started (docs)

The [OpenTUI Getting Started](https://opentui.com/docs/getting-started/) page introduces installation, Hello world, composing components, core concepts, components, and bindings. Below is a direct mapping and **functional differences**.

| OpenTUI (docs) | pytui | Aligned? | Difference |
|----------------|-------|----------|------------|
| **Install** | `pip install -e ".[dev]"` | ✅ | Runtime: Bun/Node vs CPython; package: `@opentui/core` vs `pytui` |
| **Hello world** | `Renderer` + `Box`/`Text` + `root.add()` + `r.start()` | ✅ | OpenTUI: `createCliRenderer()` + factory `Text({ content, fg })`; pytui: class `Text(ctx, { content, fg })`, explicit `width`/`height` often required |
| **Composing** | `Box({ borderStyle, padding, flexDirection, gap }, Text(...), Text(...))` | ✅ | pytui: `border_style`, `padding`, `flex_direction` (row/column), `gap`; stub layout implements flexbox-like justify/align/flex_grow and % sizing. See [Layout](#0a-alignment-with-opentui-layout-docs). |
| **Core concepts** | Renderer, Renderables, Constructs, Layout, Keyboard, Console, Colors | ✅ | See §1–2; Constructs → pytui uses `h()` + reconcile instead of TS Constructs |
| **Components (docs)** | Text, Box, Input, Select, ScrollBox, Code | ✅ | All present; see §3 |
| **Bindings** | React, Solid.js | ⚠️ Partial | React-like (Component + h() + reconcile) ✅; Solid placeholder only |

**Functional gaps vs Getting Started:**

1. **API style** — OpenTUI uses **factory functions** (`Text({ ... })`, `Box({ ... }, child1, child2)`); pytui uses **class constructors** (`Text(ctx, { ... })`) and `box.add(child)`. Declarative usage in pytui is via `h("text", props, ...)` and `reconcile(h(Component, {}), root)`.
2. **exitOnCtrlC** — OpenTUI `createCliRenderer({ exitOnCtrlC: true })`; pytui `Renderer(..., exit_on_ctrl_c=True)` (default). Set `exit_on_ctrl_c=False` to handle Ctrl+C manually. See [Keyboard §0B](#0b-alignment-with-opentui-keyboard-docs).
3. **Sizing** — OpenTUI layout often infers size from content/flex; pytui frequently requires explicit `width`/`height` on components when using the stub layout.

### 0A. Alignment with OpenTUI Layout (docs)

The [OpenTUI Layout System](https://opentui.com/docs/core-concepts/layout/) uses Yoga for CSS Flexbox-like layout. Below is the mapping to pytui (stub layout when Yoga/poga is not used).

| OpenTUI (Layout docs) | pytui | Status |
|----------------------|-------|--------|
| **Flex direction** | `flexDirection: "column" \| "row" \| "row-reverse" \| "column-reverse"` | ✅ `flex_direction` (stub + Yoga) |
| **Justify content** | `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly` | ✅ `justify_content` (stub: all six; Yoga: space-evenly if binding has it) |
| **Align items** | `flex-start`, `flex-end`, `center`, `stretch`, `baseline` | ✅ `align_items` (stub: flex-start/end/center/stretch; Yoga: full) |
| **Sizing – fixed** | `width: 30`, `height: 10` | ✅ `width` / `height` (int) |
| **Sizing – percentage** | `width: "100%"`, `height: "50%"` | ✅ stub resolves % from parent inner size; Yoga via set_width_percent |
| **Flex grow/shrink/basis** | `flexGrow: 1`, `flexShrink: 0`, `flexBasis: 100` | ✅ stub: `flex_grow` (distributes extra space); `flex_shrink`/`flex_basis` stored, stub does not shrink; Yoga full when present |
| **Position** | `position: "relative" \| "absolute"`, `left`, `top`, `right`, `bottom` | ⚠️ Options applied; stub does not position absolute (Yoga does when present) |
| **Padding** | `padding: 2`, `paddingTop`, `paddingRight`, etc. | ✅ `padding` / `padding_left` / `padding_top` / etc. |
| **Margin** | `margin: 1`, `marginTop`, etc. | ⚠️ Options applied; stub ignores margin (Yoga uses when present) |
| **Gap** | (Getting Started Box: `gap: 1`) | ✅ `gap` (stub: space between children; LayoutNode.set_gap, Renderable option `gap`) |
| **Responsive** | `renderer.on("resize", (width, height) => ...)` | ✅ `useResize` / `useTerminalDimensions`; renderer resize events |

**Summary:** Stub layout implements flex direction (row/column/reverse), justify (all six), align (flex-start/end/center/stretch), flex_grow, gap, padding, and % width/height. Margin and absolute positioning are not applied by the stub; use Yoga/poga for full parity.

### 0B. Alignment with OpenTUI Keyboard (docs)

The [OpenTUI Keyboard](https://opentui.com/docs/core-concepts/keyboard/) documents key handling, KeyEvent properties, paste events, exit on Ctrl+C, and focus/key routing. Mapping to pytui:

| OpenTUI (Keyboard docs) | pytui | Status |
|-------------------------|-------|--------|
| **Basic key handling** | `renderer.keyboard.on("keypress", handler)` or `renderer.events.on("keypress", handler)` | ✅ keyboard emits keypress; renderer forwards to events |
| **KeyEvent properties** | name, sequence, ctrl, shift, meta, option | ✅ key dict: name, char, ctrl, shift, alt, **sequence**, **meta** (=alt), **option** (=alt) |
| **Single keys** | escape, return, space | ✅ name: "escape", "enter", "space" (pytui uses "enter" not "return") |
| **Modifier combinations** | Ctrl+C, Ctrl+S, Shift+F1, Alt+Enter | ✅ key.ctrl, key.shift, key.meta/key.alt |
| **Function keys** | F1–F12 | ✅ SS3/CSI maps f1–f4; Kitty f13/f14; extend as needed |
| **Arrow keys** | up, down, left, right | ✅ name: "up", "down", "left", "right" |
| **Paste events** | `keyHandler.on("paste", (event) => { event.text })` | ✅ keyboard emits "paste" with `{ text }`; bracketed paste (ESC [ 200 ~ ... 201 ~); renderer forwards to events |
| **Exit on Ctrl+C** | `createCliRenderer({ exitOnCtrlC: true })` | ✅ `Renderer(..., exit_on_ctrl_c=True)` (default); set False to handle manually |
| **Focus and key routing** | input.focus() to receive key events | ✅ Input/Select/Textarea/Scrollbox focus() → subscribe to keyboard/events for keypress |

**Summary:** KeyEvent shape aligned (name, sequence, ctrl, shift, meta, option); paste event and exit_on_ctrl_c implemented; focus-based routing unchanged.

### 0C. Alignment with OpenTUI Console (docs)

The [OpenTUI Console overlay](https://opentui.com/docs/core-concepts/console/) documents console capture, position/size, colors by level, toggle, scroll/size shortcuts, and keybinding. Mapping to pytui:

| OpenTUI (Console docs) | pytui | Status |
|------------------------|-------|--------|
| **Basic usage** | createCliRenderer({ consoleOptions }) | Renderer + ConsoleBuffer + ConsoleOverlay; capture via `capture_stdout(buffer)` |
| **Capture** | console.log/info/warn/error/debug | `capture_stdout(buffer)` → stdout; `stderr_to_buffer=True` → stderr as level "error"; buffer lines are `(text, level)` |
| **Position** | ConsolePosition.TOP/BOTTOM/LEFT/RIGHT | ConsoleOverlay `position`: "top" \| "bottom" \| "left" \| "right" (layout by app) |
| **Size** | sizePercent: 30 | Use layout (e.g. Box with height="30%" or fixed height); overlay gets width/height from parent |
| **Colors** | colorInfo, colorWarn, colorError | ConsoleOverlay: `color_info`, `color_warn`, `color_error` (info=cyan, warn=yellow, error=red) |
| **Toggle** | renderer.console.toggle() | ConsoleController(overlay, renderer).toggle() — focuses overlay when not focused, blurs when focused |
| **Scroll when focused** | Arrow keys scroll log history | ConsoleOverlay focus() → keyboard listener; up/down → scroll_up/scroll_down |
| **+/- size when focused** | + increase, - decrease console size | ⚠️ Not implemented; app can wire resize via overlay or parent Box |
| **Keybinding for toggle** | keyInput.on("keypress", key => if key.name=='\`' renderer.console.toggle()) | `renderer.events.on("keypress", lambda k: controller.toggle() if k.get("name")=="\`" else None)` |
| **Env vars** | OTUI_USE_CONSOLE, SHOW_CONSOLE, OTUI_DUMP_CAPTURES | Document as PYTUI_USE_CONSOLE, SHOW_CONSOLE, PYTUI_DUMP_CAPTURES (optional; app can read os.environ) |

**Summary:** ConsoleBuffer (lines with level), ConsoleOverlay (position, color by level, focus + arrow scroll), ConsoleController.toggle(), capture_stdout(stderr_to_buffer). +/- resize and env-driven behavior left to app.

### 0D. Alignment with OpenTUI Colors (docs)

The [OpenTUI Colors](https://opentui.com/docs/core-concepts/colors/) document describes RGBA, creation from ints/values/hex, string colors, parseColor, alpha blending, and text attributes with colors. Mapping to pytui:

| OpenTUI (Colors docs) | pytui | Status |
|-----------------------|-------|--------|
| **RGBA.fromInts(0–255)** | RGBA.from_ints(r, g, b, a=255) | ✅ |
| **RGBA.fromValues(0.0–1.0)** | RGBA.from_values(r, g, b, a=1.0) | ✅ |
| **RGBA.fromHex("#800080")** | RGBA.from_hex("#800080") | ✅ |
| **RGBA.fromHex("#FF000080")** (alpha) | RGBA.from_hex("#ff000080") | ✅ #rrggbbaa supported |
| **String colors** | Components accept hex strings and CSS names; parse_color() normalizes | ✅ fg/bg etc. use parse_color |
| **parseColor(hex, name, transparent, RGBA)** | parse_color(value): hex (#rrggbb, #rgb, #rrggbbaa), CSS names (red, white, black, green, blue, yellow, cyan, magenta, orange, gray, grey, purple), "transparent", RGBA pass-through (to_tuple()) | ✅ |
| **Alpha blending** | OptimizedBuffer.blend_color(fg, bg, alpha), set_cell_with_alpha(x, y, cell, alpha) | ✅ |
| **Text attributes with colors** | Text/TextNode fg, bg with parse_color or RGBA (via parse_color pass-through) | ✅ |

**Summary:** parse_color supports hex (6/3/8 chars), CSS names, transparent, RGBA pass-through; RGBA.from_hex supports #rrggbbaa; buffer has blend_color and set_cell_with_alpha.

### 0E. Alignment with OpenTUI Text (docs)

The [OpenTUI Text](https://opentui.com/docs/components/text/) document describes the Text component: content, fg/bg, text attributes (bold, dim, italic, underline, blink, inverse, hidden, strikethrough), template literals for rich text (`t` with bold/italic/underline/fg/bg), positioning, and text selection. Mapping to pytui:

| OpenTUI (Text docs) | pytui | Status |
|---------------------|-------|--------|
| **Basic usage** | `Text(ctx, { content, fg })`, `renderer.root.add(text)`; content: string \| StyledText | ✅ Text accepts content as str or StyledText (list of Span or str); rich content uses per-span fg/bg/attributes |
| **Text attributes** | `TextAttributes` bitmask (BOLD, DIM, ITALIC, UNDERLINE, BLINK, INVERSE, HIDDEN, STRIKETHROUGH) or props bold/dim/italic/underline/blink/reverse/strikethrough | ✅ Text supports attributes bitmask OR separate props; selectable prop (default True) |
| **Rich text (template)** | OpenTUI: `t` template with bold/italic/underline/fg/bg | ✅ TextNode with spans; style helpers: bold, italic, underline, strikethrough, dim, reverse, blink, **fg(color)**, **bg(color)** (callables: `fg("#FF0000")("text")` or `fg("#FF0000")(bold("text"))`), link, line_break |
| **Positioning** | position: "relative" \| "absolute", left/top/right/bottom (number \| "auto" \| "{number}%") | ✅ Text and Renderable accept position, left, top, right, bottom; layout stub stores them (absolute layout applied by Yoga when present) |
| **Text selection** | selectable: true/false | ✅ Option on Text (default True); selection behavior wired by app/focus |
| **HIDDEN attribute** | TextAttributes.HIDDEN | ⚠️ Cell has no hidden field; app can render as space or omit |

**Summary:** Text has content, fg, bg, TextAttributes (bitmask) or bold/dim/italic/underline/blink/reverse/strikethrough, selectable. TextNode supports Span list with **fg(color)** and **bg(color)** style functions (OpenTUI-style: apply to string or Span, combining e.g. `fg("#FFFF00")(bold("bold yellow"))`). HIDDEN not in Cell; positioning/selection same as rest of stack.

### 0F. Alignment with OpenTUI Box (Box.ts)

OpenTUI `BoxRenderable` (Box.ts): backgroundColor, borderStyle, border (bool \| BorderSides[]), borderColor, customBorderChars, shouldFill, title, titleAlignment, focusedBorderColor, gap, rowGap, columnGap; all have property getters/setters; initializeBorder when style/color/chars set with border false; getScissorRect; applyYogaBorders/applyYogaGap. pytui Box is **fully aligned** on options, API, and behaviour.

| OpenTUI (Box.ts) | pytui | Status |
|------------------|-------|--------|
| **Options / defaults** | backgroundColor (transparent), borderStyle (single), border (false), borderColor (#FFFFFF), shouldFill (true), titleAlignment (left), focusedBorderColor (#00AAFF) | _default_options; same defaults; camelCase aliases | ✅ Aligned |
| **Auto-enable border** | If border false but borderStyle \|\| borderColor \|\| focusedBorderColor \|\| customBorderChars, set border true | Same in __init__ | ✅ Aligned |
| **Property getters/setters** | backgroundColor, border, borderStyle, borderColor, focusedBorderColor, customBorderChars, title, titleAlignment; all → requestRender | background_color, border, border_style, border_color, focused_border_color, custom_border_chars, should_fill, title, title_alignment; all → request_render | ✅ Aligned |
| **initializeBorder** | If border false, set border true, borderSides, applyYogaBorders | _initialize_border(); _apply_border_padding() | ✅ Aligned |
| **getScissorRect** | Inner rect inset by border (left/right/top/bottom) | get_scissor_rect() → {x, y, width, height} | ✅ Aligned |
| **gap / rowGap / columnGap** | setGap(Gutter.All/Row/Column), requestRender | gap, row_gap, column_gap options and property setters; _apply_gap(); layout set_gap (stub: single gap) | ✅ Aligned |
| **Mouse events** | (not in Box.ts) | Not on Box; use renderer mouse if needed | N/A |

**Summary:** Box has full property alignment; camelCase option names; _initialize_border; get_scissor_rect; gap/row_gap/column_gap options and setters; all setters trigger request_render.

### 0G. Alignment with OpenTUI Diff (Diff.ts)

OpenTUI `DiffRenderable` (Diff.ts) takes a **unified diff string** (`diff`), supports **view: "unified" | "split"**, parse error view, hunks with line numbers, syntax highlight, and wrap. pytui Diff is **fully aligned** on options, behaviour, and API.

| OpenTUI (Diff.ts) | pytui | Status |
|-------------------|-------|--------|
| **Input** | `diff` (unified string only) | `diff` (unified) **or** `old_text` / `new_text` (LCS diff) | ✅ API aligned; pytui adds dual input |
| **view** | "unified" \| "split" | "unified" \| "split" (property + rendering) | ✅ Aligned |
| **Unified parsing** | parsePatch (hunks, @@, file line numbers) | parse_patch (hunks, @@), flattened_unified_lines; line numbers from hunks | ✅ Aligned |
| **Split view** | Left (removed) / Right (added), line numbers, signs | build_split_logical_lines; left/right columns, line numbers, +/- signs | ✅ Aligned |
| **Parse error** | buildErrorView: error message + raw diff | _render_error_view: first line error message, then raw diff | ✅ Aligned |
| **Syntax in diff** | CodeRenderable (filetype, syntaxStyle) | syntax_highlight(line, filetype) + theme in unified view | ✅ Aligned |
| **wrap_mode** | word / char / none; wrap long lines | _wrap_line (break at content_width); word/char/none stored and used | ✅ Aligned |
| **Options** | fg, filetype, syntaxStyle, wrapMode, conceal, selectionBg/Fg, treeSitterClient, showLineNumbers, lineNumberFg/Bg, added/removed/context Bg, addedContentBg, etc., addedSignColor, removedSignColor, added/removedLineNumberBg | All options + camelCase aliases | ✅ Aligned |
| **Setters** | diff, view, filetype, syntaxStyle, wrapMode, showLineNumbers, addedBg, removedBg, contextBg, addedSignColor, removedSignColor, … → rebuildView | All property setters → request_render | ✅ Aligned |
| **Lifecycle** | destroyRecursively detaches listeners | destroy_recursively clears state, remove_all | ✅ Aligned |

**Summary:** Options, property names (camelCase aliases), unified/split view, parse error view, hunks with line numbers, syntax highlight, wrap_mode, all setters, and destroy_recursively are aligned.

### 0H. Alignment with OpenTUI ASCIIFont (ASCIIFont.ts)

OpenTUI `ASCIIFontRenderable` extends FrameBufferRenderable: text, font, color, backgroundColor, selectionBg, selectionFg, selectable (default true); width/height from measureText; shouldStartSelection, onSelectionChanged, getSelectedText, hasSelection; renderFontToBuffer + renderSelectionHighlight. pytui ASCIIFont is **fully aligned** on options, API, and behaviour.

| OpenTUI (ASCIIFont.ts) | pytui | Status |
|------------------------|-------|--------|
| **Options** | text, font, color, backgroundColor, selectionBg, selectionFg, selectable (default true) | text, font, color, background_color, selection_bg, selection_fg, selectable (default True); camelCase: backgroundColor, selectionBg, selectionFg | ✅ Aligned |
| **Width/height** | From measureText in constructor and updateDimensions | From measure_text in _update_dimensions; update_dimensions() public | ✅ Aligned |
| **Property getters/setters** | text, font, color, backgroundColor, selectionBg, selectionFg | text, font, color, background_color, selection_bg, selection_fg; set_text, set_font | ✅ Aligned |
| **shouldStartSelection(localX, localY)** | coordinateToCharacterIndex, bounds check | should_start_selection(local_x, local_y) | ✅ Aligned |
| **onSelectionChanged(selection)** | convertGlobalToLocalSelection, selectionHelper.onLocalSelectionChanged | on_selection_changed(selection); accepts local (anchorX/focusX) or global (anchor/focus) | ✅ Aligned |
| **getSelectedText / hasSelection** | getSelection(), slice text | get_selected_text(), has_selection() | ✅ Aligned |
| **renderFontToBuffer + renderSelectionHighlight** | fillRect selectionBg, render selected text with selectionFg/Bg | _ensure_buffer + _render_selection_highlight; fill_rect + render_font_to_buffer | ✅ Aligned |
| **onResize** | super.onResize, renderFontToBuffer | on_resize(width, height) invalidates buffer | ✅ Aligned |
| **getCharacterPositions** | lib/ascii.font | get_character_positions(text, font) module-level | ✅ Aligned |

**Summary:** Options (color, backgroundColor, selectionBg/Fg, selectable default true), property setters, should_start_selection, on_selection_changed, get_selected_text, has_selection, selection highlight in buffer, update_dimensions, on_resize, and get_character_positions are aligned.

---

## 1. Overview

| Aspect | OpenTUI (TS/Zig) | pytui (Python) | Notes |
|--------|------------------|----------------|-------|
| **Runtime** | Bun / Node | CPython 3.11+ | - |
| **Native layer** | Zig (FFI) | Rust + PyO3 (optional) | pytui falls back to pure Python Buffer when native is absent |
| **Layout** | Yoga binding | poga optional / stub | stub: flex_direction, justify_content, align_items, flex_grow, gap, padding, % width/height; see [Layout docs](#0a-alignment-with-opentui-layout-docs) |
| **Declarative** | React + Solid reconciler | Component + h() + reconcile | pytui is React-like only; Solid is placeholder |
| **Syntax highlighting** | Tree-sitter (WASM) + multi-language | Tree-sitter optional; syntax/languages (get_language, get_parser, list_available_languages); tree-sitter-languages or data_paths | pytui uses tree-sitter-languages or .so in data_paths |

---

## 2. Core

| Capability | OpenTUI | pytui | Status |
|------------|---------|-------|--------|
| **Renderer** | createCliRenderer, start/stop, FPS | Renderer, start/stop, target_fps, terminal=, render_once() | ✅ Aligned |
| **Double buffer / output** | FrameBuffer, diff output | OptimizedBuffer, full first frame + diff | ✅ Aligned |
| **Renderable tree** | BaseRenderable, add/remove, layout, render | Renderable, add/remove, calculate_layout, render | ✅ Aligned |
| **Layout** | Yoga, position/flex/margins | LayoutNode, poga or stub (width/height/padding) | ✅ Present; stub has no full flex |
| **Terminal** | size, alternate screen, raw, cursor, mouse | Terminal, same | ✅ Aligned |
| **Keyboard** | KeyHandler, keypress/paste, KeyEvent, exitOnCtrlC | KeyboardHandler, keypress/paste, KeyEvent (name, sequence, ctrl, shift, meta, option), exit_on_ctrl_c, Kitty | ✅ Aligned; see [Keyboard §0B](#0b-alignment-with-opentui-keyboard-docs) |
| **Mouse** | parse.mouse, MouseEvent | MouseHandler, SGR 1006, mouse event | ✅ Present |
| **Colors** | RGBA, fromHex/fromInts/fromValues, parseColor, alpha blending | parse_color (hex, CSS names, transparent, RGBA pass-through), RGBA.from_hex/from_ints/from_values (#rrggbbaa), blend_color, set_cell_with_alpha | ✅ Aligned; see [Colors §0D](#0d-alignment-with-opentui-colors-docs) |
| **ANSI** | cursor, colors, screen control | ANSI, cursor_to, rgb_fg/bg, CLEAR, etc. | ✅ Aligned |
| **Events** | EventEmitter, RenderContext | pyee, EventBus, ctx | ✅ Aligned |
| **Console** | overlay, position/size, color by level, toggle, scroll | ConsoleBuffer (level), ConsoleOverlay (position, color_info/warn/error, focus+scroll), ConsoleController.toggle(), capture_stdout(stderr_to_buffer) | ✅ Aligned; see [Console §0C](#0c-alignment-with-opentui-console-docs) |
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
| **Box** | Box, border, title, titleAlignment, background | Box, border, border_style, title, title_alignment, padding | ✅ Aligned; see [§0F](#0f-alignment-with-opentui-box-docs) |
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
| **Tree-sitter** | TreeSitterClient, WASM, multi-language | syntax/languages (get_language, get_parser, list_available_languages) optional; tree-sitter-languages or data_paths | ✅ Prebuilt via tree-sitter-languages or .so in data_paths |
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
| **Syntax highlighting** | ✅ Present | themes, SyntaxStyle; Tree-sitter optional (tree-sitter-languages or data_paths) |
| **Utils and extensions** | ✅ Covered | extmarks, data_paths, scroll_acceleration, terminal_palette, ascii_font |
| **Testing and CI** | ✅ Covered | TestRenderer, MockKeys, MockMouse, Snapshot, CI |

pytui is **largely aligned** with OpenTUI on component set and core capabilities. Remaining gaps are mainly **component details**, **Solid/Composition**, **post filters**, and **StyledText attributes**. Tree-sitter and language loading (tree-sitter-languages or data_paths) are implemented.

**Vs [OpenTUI Getting Started](https://opentui.com/docs/getting-started/)**: see **§0** for mapping; **§0A** [Layout](https://opentui.com/docs/core-concepts/layout/); **§0B** [Keyboard](https://opentui.com/docs/core-concepts/keyboard/); **§0C** [Console](https://opentui.com/docs/core-concepts/console/); **§0D** [Colors](https://opentui.com/docs/core-concepts/colors/). See [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) for Phase 12+ candidates.

---

## 9. Implementation differences (detailed)

Based on the latest code in both repositories.

### 9.1 Post filters

| OpenTUI | pytui |
|---------|-------|
| `applyScanlines`, `applyGrayscale`, `applySepia`, `applyInvert`, `applyNoise`, `applyAsciiArt` | ✅ apply_scanlines, apply_grayscale, apply_sepia, apply_invert, apply_noise, apply_ascii_art |
| `applyChromaticAberration` | ❌ Not implemented |
| `DistortionEffect`, `VignetteEffect`, `BrightnessEffect`, `BlurEffect`, `BloomEffect` | ❌ Not implemented |
| — | apply_dim, apply_blur_placeholder (placeholder) |

pytui has dim, grayscale, sepia, invert, scanlines, noise, ascii_art; chromatic aberration and advanced effects (Distortion, Vignette, Blur, Bloom) not implemented.

### 9.2 React hooks

| Hook | OpenTUI | pytui |
|------|---------|-------|
| useState | ✅ (React) | ✅ useState |
| useEffect | ✅ (React) | ✅ useEffect |
| useRenderer | ✅ | ✅ useRenderer |
| useResize | ✅ | ✅ useResize |
| useKeyboard | ✅ | ✅ useKeyboard |
| useTimeline | ✅ | ✅ useTimeline |
| useTerminalDimensions | ✅ | ✅ useTerminalDimensions(ctx) (same as useResize) |
| useEvent (useEffectEvent) | ✅ used by use-resize/use-keyboard | ✅ useEvent(fn) returns stable callback invoking latest fn |

pytui has useTerminalDimensions and useEvent; size from useResize/useTerminalDimensions.

### 9.3 StyledText / TextNode attributes

| Attribute | OpenTUI StyledText/TextNode | pytui TextNode |
|----------|----------------------------|----------------|
| fg, bg, bold, italic, underline | ✅ | ✅ |
| strikethrough | ✅ | ✅ (SGR 9) |
| dim | ✅ | ✅ (SGR 2) |
| reverse | ✅ | ✅ (SGR 7) |
| blink | ✅ | ✅ (SGR 5) |
| link, line_break | ✅ | ✅ |

pytui TextNode supports bold, italic, underline, strikethrough, dim, reverse, blink, link, line_break; helpers: strikethrough(), dim(), reverse(), blink().

### 9.4 Declarative API and composition

| Capability | OpenTUI | pytui |
|------------|---------|-------|
| React reconciler + host-config + JSX | ✅ | ❌ JSX; ✅ h() + reconcile + TYPE_MAP |
| Solid reconciler (control flow, createComponent) | ✅ packages/solid | ⚠️ react/solid_placeholder only |
| VRenderable, delegate(), constructs (Box/Text/… as functions) | ✅ composition/vnode, constructs | ❌ h() maps types to Renderables; no VRenderable/delegate |

pytui is React-like only (Component + h() + reconcile); no Solid, no VRenderable/delegate/constructs.

### 9.5 Syntax highlighting and Tree-sitter

| Capability | OpenTUI | pytui |
|------------|---------|-------|
| Tree-sitter client | ✅ lib/tree-sitter (client, workers) | ✅ syntax/languages optional (get_language, get_parser) |
| Prebuilt language bundles | ✅ WASM (e.g. js, ts, zig, markdown in assets) | ✅ tree-sitter-languages package or data_paths/tree-sitter/languages/*.so |
| list available languages | — | ✅ list_available_languages(), COMMON_LANGUAGE_NAMES |
| tree-sitter-styled-text | ✅ | ❌ Highlighter returns (text, token_type); no StyledText pipeline |
| Themes / SyntaxStyle | ✅ | ✅ |

pytui has themes and highlighter; Tree-sitter is optional. Use `pip install tree-sitter tree-sitter-languages` for Python/JS/TS/Go/Rust/JSON/HTML/CSS/Bash/C/C++ or place `.so`/`.dll` under `get_data_dir()/tree-sitter/languages/`. See [Getting started](getting-started.md) and [API Reference](api-reference.md) (syntax).

### 9.6 3D / WebGPU and native

| Capability | OpenTUI | pytui |
|------------|---------|-------|
| 3D / WebGPU (WGPURenderer, sprites, physics) | ✅ packages/core/src/3d/ | ❌ |
| Zig native (buffer, etc.) | ✅ zig/ | ❌ |
| Rust native (buffer) | ❌ | ✅ src/pytui/native/ (optional) |

OpenTUI uses Zig for native and has a 3D/WebGPU layer; pytui has an optional Rust extension only.

### 9.7 Selection and extmarks

| Capability | OpenTUI | pytui |
|------------|---------|-------|
| Standalone Selection class (lib/selection.ts) | ✅ Selection, convertGlobalToLocalSelection, ASCIIFontSelectionHelper | ✅ utils/selection: Selection, convert_global_to_local_selection, ASCIIFontSelectionHelper |
| Selection in EditorView/Textarea | ✅ | ✅ |
| extmarks (store, controller, style_map) | ✅ | ✅ utils/extmarks; Textarea options |

pytui has standalone Selection (anchor/focus, to_local), convert_global_to_local_selection, and ASCIIFontSelectionHelper (coordinate ↔ character index); extmarks and EditorView/Textarea selection unchanged.

### 9.8 ASCII fonts

| OpenTUI | pytui |
|---------|-------|
| lib/fonts: tiny, block, grid, huge, pallet, shade, slick (JSON) | TINY_FONT, BLOCK_FONT, SLICK_FONT, SHADE_FONT, GRID_FONT, HUGE_FONT, PALLET_FONT (+ load_font_from_json, register_font) |

pytui has all seven font names (grid/huge/pallet use block-style until user loads JSON); load_font_from_json and register_font supported; coordinate_to_character_index for selection helpers.

### 9.9 Testing and CI

| OpenTUI | pytui |
|---------|-------|
| Jest, createTestRenderer, createMockKeys, createMockMouse, snapshots | pytest, create_test_renderer, create_mock_keys, create_mock_mouse, buffer_snapshot_lines |
| Multiple workflows (build-core, build-react, build-solid, opencode, etc.) | Single CI (ruff, pytest, coverage) |

Both have test renderer, mock I/O, and snapshots; OpenTUI has more granular workflows and Solid/OpenCode builds.
