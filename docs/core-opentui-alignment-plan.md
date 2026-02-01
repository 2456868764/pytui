# PyTUI core 与 OpenTUI core 逐文件对齐计划

## 一、目标

1. **逐文件对齐**：`pytui/src/pytui/core/`  下每个 Python 模块与 `opentui/packages/core/src/` 当前目录下对应 TypeScript 文件一一对应（属性、功能、行为、API、测试）。
2. **命名对应**：TS 文件 `kebab-case.ts` / `PascalCase.ts` 对应 Python 文件 `snake_case.py`（如 `edit-buffer.ts` → `edit_buffer.py`，`Renderable.ts` → `renderable.py`）。
3. **测试一一对应**：每个 OpenTUI `*.test.ts` 对应 PyTUI `tests/unit/core/test_*.py`，用例名称与行为与 TS 一致。
4. **子目录**：`animation/`、`post/`、`renderables/`、`testing/` 与 PyTUI 对应目录/模块逐项对齐。

## 二、文件映射表（core/src 顶层及一级子目录）

| OpenTUI 文件 | PyTUI 文件 | 说明 | 状态 |
|--------------|------------|------|------|
| `index.ts` | `core/__init__.py` | 导出清单、顺序 | 已对齐 |
| `types.ts` | `core/types.py` | 类型/接口 | 已对齐 |
| `utils.ts` |  `core/utils.py` | 工具函数 | 已对齐 |
| `ansi.ts` | `core/ansi.py` | ANSI 序列 | 已对齐 |
| `buffer.ts` | `core/buffer.py` | 帧缓冲、Cell、drawTextBuffer 等 | 已对齐 |
| `buffer.test.ts` | `tests/unit/core/test_buffer.py` | 单元测试 | 已对齐 |
| `text-buffer.ts` | `core/text_buffer.py` | TextBuffer, TextChunk, createTextBuffer, setText | 已对齐 |
| `text-buffer.test.ts` | `tests/unit/core/test_text_buffer.py` | 单元测试 | 已对齐 |
| `text-buffer-view.ts` | `core/text_buffer_view.py`  | TextBufferView | 已对齐 |
| `text-buffer-view.test.ts` | `tests/unit/core/test_text_buffer_view.py`  | 单元测试 | 已对齐 |
| `edit-buffer.ts` | `core/edit_buffer.py` | EditBuffer | 已对齐 |
| `edit-buffer.test.ts` | `tests/unit/core/test_edit_buffer.py` | 单元测试 | 已对齐 |
| `editor-view.ts` | `core/editor_view.py` | EditorView | 已对齐 |
| `editor-view.test.ts` | `tests/unit/core/test_editor_view.py` | 单元测试 | 已对齐 |
| `syntax-style.ts` | `core/syntax_style.py` | SyntaxStyle, mergeStyles, registerStyle | 已对齐 |
| `syntax-style.test.ts` | `tests/unit/core/test_syntax_style.py` | 单元测试 | 已对齐 |
| `Renderable.ts` | `core/renderable.py` | Renderable, LayoutEvents, RenderableEvents | 已对齐 |
| `renderer.ts` | `core/renderer.py` | Renderer | 已对齐 |
| `console.ts` | `core/console.py` | Console | 已对齐 |
| `console.test.ts` | `tests/unit/core/test_console.py` | 单元测试 | 已对齐 |
| `animation/Timeline.ts` | `core/animation.py` | Timeline, createTimeline | 已对齐 |
| `animation/Timeline.test.ts` | `tests/unit/core/test_animation.py` | 单元测试 | 已对齐 |
| `post/filters.ts` | `post/filters.py` | 后处理滤镜 | 已对齐 |
| `testing.ts` | `testing/` 或 `core/testing` | 测试入口 | 已对齐 |
| `testing/test-renderer.ts` | `testing/test_renderer.py` | 测试用 Renderer | 已对齐 |
| `testing/mock-keys.ts` | `testing/mock_keys.py` | 模拟按键 | 已对齐 |
| `testing/mock-mouse.ts` | `testing/mock_mouse.py` | 模拟鼠标 | 已对齐 |
| `testing/spy.ts` | `testing/spy.py` 或等价 | Spy 工具 | 可选 |
| `testing/test-recorder.ts` | `testing/` 等价 | 测试录制 | 可选 |
| `zig.ts` / `zig-structs.ts` | （无 Zig） | PyTUI 使用 native/Rust，接口对齐 types | 已对齐（N/A） |
| `renderables/index.ts` | `components/` | 导出所有 renderables | 已对齐 |
| `renderables/Box.ts` | `components/box.py` | Box | 已对齐 |
| `renderables/Box.test.ts` | `tests/unit/components/test_box.py`  | 单元测试 | 已对齐 |
| `renderables/FrameBuffer.ts` | `components/frame_buffer.py` | FrameBuffer | 已对齐 |
| `renderables/Text.ts` | `components/text.py` | Text | 已对齐 |
| `renderables/Text.test.ts` | `tests/unit/components/test_text.py` | 单元测试 | 已对齐 |
| `renderables/Textarea.ts` | `components/textarea.py` | Textarea | 已对齐 |
| `renderables/TextNode.ts` | `components/text_node.py` | TextNode | 已对齐 |
| `renderables/EditBufferRenderable.ts` | `components/edit_buffer_renderable.py` | EditBufferRenderable | 已对齐 |
| `renderables/ScrollBox.ts` | `components/scrollbox.py` | ScrollBox | 已对齐 |
| `renderables/ScrollBar.ts` | `components/scrollbar.py` | ScrollBar | 已对齐 |
| `renderables/Input.ts` | `components/input.py` | Input | 已对齐 |
| `renderables/Select.ts` | `components/select.py` | Select | 已对齐 |
| `renderables/Slider.ts` | `components/slider.py` | Slider | 已对齐 |
| `renderables/TabSelect.ts` | `components/tab_select.py` | TabSelect | 已对齐 |
| `renderables/Diff.ts` | `components/diff.py` | Diff | 已对齐 |
| `renderables/Code.ts` | `components/code.py` | Code | 已对齐 |
| `renderables/LineNumberRenderable.ts` | `components/line_number.py` | LineNumberRenderable | 已对齐 |
| `renderables/Markdown.ts` | `components/markdown.py` | MarkdownRenderable | 已对齐 |
| `renderables/ASCIIFont.ts` | `components/ascii_font.py` | ASCIIFont | 已对齐 |
| `renderables/TextBufferRenderable.ts` | `components/text_buffer_renderable.py` | TextBufferRenderable | 已对齐 |
| `tests/*.test.ts` | `tests/unit/core/` 及 `tests/unit/components/` 下对应 | 快照/集成/单测 | 已对齐（629 passed, 1 skipped） |

## 三、PyTUI core 独有模块（与 OpenTUI 对应关系）

| PyTUI 文件 | 说明 | 对齐策略 | 状态 |
|------------|------|----------|------|
| ~~`core/colors.py`~~ | 颜色常量 | 对应 lib/RGBA 使用方式，删除避免重复 | 已删除，统一使用 `from pytui.lib import parse_color, parse_color_to_tuple` |
| `core/events.py` | EventBus | 对应 OpenTUI events/EventEmitter | 已对齐（EventBus = EventEmitter，事件名一致） |
| `core/keyboard.py` | 键盘相关 | 对应 lib/KeyHandler、parse.keypress 使用 | 已对齐（KeyboardHandler 组合 StdinBuffer + KeyHandler，feed → keypress/keyrelease/paste） |
| `core/layout.py` | 布局 | 对应 yoga-layout / renderable 布局 | 已对齐（Yoga 或 _StubLayoutNode，flexbox API 与 OpenTUI 一致） |
| `core/mouse.py` | 鼠标相关 | 对应 lib/parse.mouse 使用 | 已对齐（MouseHandler 使用 lib.parse_mouse.MouseParser，emit 'mouse'） |
| ~~`core/rgba.py`~~ | 若存在 | 与 lib/rgba 统一，删除避免重复 | 已删除，统一使用 `from pytui.lib import RGBA, hex_to_rgb, rgb_to_hex, parse_color` |
| ~~`core/terminal_palette.py`~~ | 若存在 | 与 lib/terminal_palette 统一，删除避免重复 | 已删除，统一使用 `from pytui.lib import TerminalPalette, create_terminal_palette, detect_capability, get_palette_color` |
| `core/terminal.py` | Terminal | 对应 zig/terminal 或 lib terminal 能力 | 已对齐（get_size、alternate screen、raw、cursor、mouse；能力检测用 lib.terminal_capability_detection） |

## 四、每文件对齐检查项（通用）

对每一对 TS ↔ Python 文件：

1. **属性/类型**：TS interface/type 对应 Python TypedDict/dataclass/Protocol；字段名 snake_case 与 camelCase 映射一致。
2. **API**：每个 export 函数/类在 Python 中有等价实现，签名与语义一致（参数、返回值、副作用）。
3. **行为**：边界条件、默认值、无效输入处理与 OpenTUI 一致。
4. **测试**：每个 `test("...")` / `describe("...")` 对应 pytest 中同名或等价用例，断言行为一致。

## 五、执行顺序（按依赖）

1. **无依赖**：types, utils, ansi
2. **buffer, text-buffer, text-buffer-view**：依赖 types、zig/native
3. **edit-buffer, editor-view**：依赖 text-buffer、text-buffer-view
4. **syntax-style**：依赖 lib/RGBA、types
5. **Renderable, renderer**：依赖 buffer、types
6. **animation/Timeline**：独立
7. **console**：依赖 renderer/renderables
8. **post/filters**：依赖 buffer/renderer
9. **renderables/**：依赖 Renderable、buffer、edit-buffer、syntax-style 等
10. **testing/**：依赖 renderer、mock
11. **index/__init__**：最后统一导出顺序与清单

## 六、当前进度

- [x] 计划文档创建
- [x] index.ts → __init__.py 导出顺序
- [x] types.ts → types.py
- [x] utils.ts → utils.py（create_text_attributes, attributes_with_link, get_link_id, visualize_renderable_tree）
- [x] ansi.ts → ansi.py
- [x] buffer.ts → buffer.py（OptimizedBuffer.create, set_respect_alpha, draw_text, set_cell, clear, fill_rect, draw_box 等）
- [x] buffer.test.ts → test_buffer.py（create/destroy/guard）
- [x] text-buffer.ts → text_buffer.py（create, setText, append, setStyledText, getPlainText, clear, reset, destroy）
- [x] text-buffer.test.ts → test_text_buffer.py
- [x] text-buffer-view.ts → text_buffer_view.py（create, line_info, setSelection, getSelection, getSelectedText, destroy）
- [x] text-buffer-view.test.ts → test_text_buffer_view.py
- [x] core/utils → test_utils.py（create_text_attributes, attributes_with_link, get_link_id, visualize_renderable_tree）
- [x] edit-buffer.ts → edit_buffer.py（create, getText, getCursorPosition, setCursorToLineCol, moveCursor*, gotoLine, destroy）
- [x] edit-buffer.test.ts → test_edit_buffer.py
- [x] editor-view.ts → editor_view.py（create, setViewportSize, getViewport, setSelection, getSelection, hasSelection, getVirtualLineCount, destroy）
- [x] editor-view.test.ts → test_editor_view.py（已有用例通过）
- [x] syntax-style.ts → syntax_style.py（已对齐）
- [x] Renderable.ts → renderable.py（LayoutEvents, RenderableEvents, add/remove/get_children, insertBefore, findById, requestRender, focus/blur）
- [x] renderer.ts → renderer.py（RendererControlState, scheduleRender, renderFrame, destroy）
- [x] console.ts → console.py（ConsolePosition, ConsoleOptions, TerminalConsole, capture）
- [x] console.test.ts → test_console.py（已有用例通过）
- [x] animation/Timeline.ts → animation.py（Timeline, createTimeline, EasingFunctions）
- [x] animation/Timeline.test.ts → test_animation.py（已有用例通过）
- [x] post/filters.ts → post/filters.py（applyDim, applyGrayscale, applySepia, applyInvert, applyScanlines, applyNoise, applyAsciiArt）
- [x] testing/test-renderer.ts → testing/test_renderer.py（createTestRenderer）
- [x] testing/mock-keys.ts → testing/mock_keys.py（create_mock_keys）
- [x] testing/mock-mouse.ts → testing/mock_mouse.py（create_mock_mouse）
- [x] renderables/ → components/（Box, FrameBuffer, Text, Textarea, TextNode, EditBufferRenderable, ScrollBox, ScrollBar, Input, Select, Slider, TabSelect, Diff, Code, LineNumberRenderable, ASCIIFont 已对齐）
- [x] Markdown (components/markdown.py) 及 tests/unit/components/test_markdown.py
- [x] TextBufferRenderable (components/text_buffer_renderable.py) 及 tests/unit/components/test_text_buffer_renderable.py
- [x] **三、PyTUI core 独有模块**：colors/rgba/terminal_palette 已删除（统一用 pytui.lib）；events/keyboard/layout/mouse/terminal 已对应 OpenTUI

## 七、运行测试（conda pytui 环境）

```bash
# 全部单元测试（推荐使用 conda pytui 环境）
make test
# 或
conda run -n pytui python -m pytest tests/unit/ -v --tb=short

# 仅 core 目录
make test-core
```

---

执行时：每完成一对文件，在本文档「状态」列更新，并在对应 PyTUI 文件头注释中标明对齐的 OpenTUI 文件与版本/commit（可选）。
