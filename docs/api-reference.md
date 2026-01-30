# API Reference

## core

### Renderer

- `Renderer(width=None, height=None, target_fps=60, use_alternate_screen=True, use_mouse=False)`  
  Create the renderer; width/height default to terminal size.
- `renderer.start()` / `renderer.stop()`  
  Enter main loop / stop.
- `renderer.root`  
  Root Renderable; use `root.add(child)` to mount UI.
- `renderer.context`  
  RenderContext passed to components as `ctx`.
- `renderer.events`  
  EventBus; e.g. `on("keypress", handler)`.
- `renderer.keyboard`  
  KeyboardHandler; components with focus often listen here for reliable key delivery.
- `renderer.schedule_render()`  
  Request a repaint on the next frame.
- `renderer.render_once()`  
  One layout + render pass without reading input (for tests).

### Renderable

- `Renderable(ctx, options)`  
  options: id, visible, z_index, width, height, padding, margin, focused, and layout/style keys.
- `add(child, index=None)` / `remove(child)` / `remove_all()`  
  Child management.
- `request_render()`  
  Mark dirty and bubble up; at root, calls schedule_render.
- `calculate_layout()`  
  Recursively compute layout and set x, y, width, height.
- `render(buffer)`  
  Calls `render_self(buffer)` then renders children in z_index order.
- `focus()` / `blur()`  
  Override in components that register keyboard (or other) listeners.

### Buffer

- `OptimizedBuffer(width, height, use_native=True)`  
  Double-buffer; use_native and pytui_native use Rust when available.
- `set_cell(x, y, cell)` / `get_cell(x, y)`  
  Read/write Cell (char, fg, bg, etc.).
- `clear()` / `draw_text(text, x, y, fg)`  
  Clear buffer, draw text.

### Terminal

- `get_size()` → (width, height)
- `enter_alternate_screen()` / `exit_alternate_screen()`
- `set_raw_mode()` / `restore_mode()`
- `hide_cursor()` / `show_cursor()`
- `enable_mouse()` / `disable_mouse()`

### KeyboardHandler

- `feed(data: str | bytes)`  
  Feed input; parses escape sequences and emits `keypress` with {name, char, ctrl, alt, shift}.
- `on("keypress", handler)` / `remove_listener("keypress", handler)`  
  Subscribe/unsubscribe to keypress events.

### MouseHandler

- `feed(data: bytes | str)` → bytes  
  Parse SGR 1006 mouse sequences, emit `mouse` events; returns unconsumed bytes.
- `on("mouse", handler)`  
  event: x, y, button, release, motion.

### EditBuffer / EditorView

- **EditBuffer**: `set_text`, `get_lines`, `insert`, `delete`, `undo`, `redo`, `pos_to_line_col`, `line_col_to_pos`.
- **EditorView**: Binds to EditBuffer; `cursor_pos`, `scroll_y`, `view_width`/`view_height`, `get_visible_lines`, `set_cursor`, `set_cursor_line_col`, `get_selection_range`, `insert`, `delete_backward`, `delete_forward`, `undo`, `redo`, `ensure_cursor_visible`.

### Console

- `Console(width=None, height=None, target_fps=30, ...)`  
  Wraps Terminal + Renderer.
- `console.run(mount=None)`  
  If mount is provided, add it to root and start().

---

## components

- **Text(ctx, options)**  
  options: content, width, height, fg, bg, bold, italic, underline.  
  `set_content(text)` to update.
- **TextNode(ctx, options)**  
  options: spans (list of Span / bold/italic/underline/line_break/link), width, height.
- **Box(ctx, options)**  
  options: width, height, border, border_style, title, border_color, background_color.  
  border=True sets padding=1.
- **Input(ctx, options)**  
  options: value, placeholder, width, height, focused.  
  `set_value`, `insert_char`, `backspace`; events: input, change, enter.
- **Select(ctx, options)**  
  options: options (list of str or {name, description?, value?}), selectedIndex/selected, width, height, focused, keyBindings, showDescription, showScrollIndicator, wrapSelection.  
  `selected`, `selected_value`, `select_next` / `select_prev` / `select_current`; event: select.  
  When focused, listens on `ctx.renderer.keyboard` for up/down/enter.
- **Textarea(ctx, options)**  
  options: content, width, height, buffer, editor_view, fg, bg, focused.  
  Without editor_view: scroll only (up/down/page_up/page_down when focused).  
  With editor_view: full editing, cursor, selection, undo/redo.  
  `set_content`, `set_scroll_y`, `scroll_up`, `scroll_down`, `undo`, `redo`.
- **Scrollbox(ctx, options)**  
  options: width, height, focused, scroll_acceleration (optional).  
  When focused, up/down or j/k scroll; `scroll_up`, `scroll_down`, `set_scroll`.  
  Overrides `render()` to apply scroll_y offset and viewport clipping for children.
- **Code(ctx, options)**  
  options: content, language, width, height, show_line_numbers, show_diff, show_diagnostics, diagnostics (list of (line_0based, severity)), theme, fg, bg, line_num_fg, diff_add_fg, diff_remove_fg, diag_error_fg, diag_warning_fg.
- **Diff(ctx, options)**  
  options: old_text, new_text, width, height, add_fg, del_fg, context_fg.
- **ASCIIFont(ctx, options)**  
  options: text, font (tiny/block/slick/shade or registered name), width, height, selectable, selectionBg/selectionFg.
- **LineNumber(ctx, options)**  
  options: line_count, scroll_offset, line_number_width, fg, bg.
- **TabSelect(ctx, options)**  
  options: tabs, selectedIndex, onSelect.
- **Slider(ctx, options)**  
  options: min, max, value, step, width, height; events: change, scroll.
- **ScrollBar(ctx, options)**  
  options: scroll_max, scroll_value, height; event: scroll.
- **FrameBuffer(ctx, options)**  
  Renderable that wraps a buffer; `get_buffer()` for external drawing, blit on render.

---

## react

- **Component(ctx, props)**  
  props, state, `set_state(partial | updater=...)`, `update()`; subclasses implement `render()` returning a virtual tree.
- **useState(initial)**  
  Returns `[value, set_value]`. Supports functional updates: `set_value(lambda prev: new_val)`. Call only inside render.
- **useEffect(effect, deps=None)**  
  effect runs after render commit; simple implementation runs after each render.
- **useRenderer(ctx)**  
  Returns `ctx.renderer`.
- **useResize(ctx)**  
  Returns (width, height); updates on resize event.
- **useKeyboard(ctx)**  
  Returns `ctx.renderer.events` for keypress (use for global handlers; focused components often use `ctx.renderer.keyboard`).
- **useTimeline(ctx)**  
  Returns {elapsed, pause, resume}; elapsed updates each frame.
- **h(type, props=None, *children)** / **create_element(...)**  
  Create virtual node; type is `"text"`, `"box"`, `"input"`, `"select"`, `"textarea"`, `"code"`, `"diff"`, `"scrollbox"`, `"ascii_font"`, etc., or a Component subclass. None in children is filtered out.
- **reconcile(elements, container)**  
  Mount or update the virtual tree into the Renderable container; elements may be a single node or a list.
- **create_reconciler(ctx)**  
  Returns a reconcile function bound to ctx (optional).

---

## syntax

- **highlight(code, language="python")**  
  Returns `[(text, token_type), ...]`; falls back to plain when tree-sitter is unavailable.
- **get_theme(name)**  
  Returns token_type → RGBA color map.

---

## utils

- **diff_lines(old_text, new_text)**  
  Line-based diff; returns `[(tag, line), ...]`, tag is `" "` / `"+"` / `"-"`.
- **ExtmarksStore**  
  Store for extmarks (ranges + style_id); used with Textarea/EditorView for decorations.
- **LinearScrollAccel / MacOSScrollAccel**  
  Scroll acceleration; optional `scroll_acceleration` on Scrollbox.
- **validate_positive_int**, **validate_non_negative_int**, **validate_hex_color**  
  Validation helpers.
