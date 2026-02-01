# Rust 重构与 OpenTUI Zig 完全对齐执行计划

## 一、目标

1. **功能完全对齐**：`pytui/src/pytui/native/src/` 下每个 Rust 模块与 `opentui/packages/core/src/zig/` 中对应 Zig 文件功能一一对应。
2. **文件与命名对应**：每个 Zig 源文件对应一个 Rust 模块文件（`xxx.zig` → `xxx.rs`），多词文件名用下划线（如 `text_buffer.rs`）。
3. **测试完全对齐**：测试集中到独立测试模块，与 `opentui/packages/core/src/zig/tests/` 中每个 `*_test.zig` 一一对应，测试用例名称与行为与 Zig 测试一致。

## 二、Zig 源文件与 Rust 模块映射表

| Zig 文件 | Rust 模块文件 | 功能概要 | 当前状态 |
|----------|---------------|----------|----------|
| `utils.zig` | `utils.rs` | RGBA、f32PtrToRGBA 等工具 | 未拆出 |
| `ansi.zig` | `ansi.rs` | ANSI 常量、TextAttributes（setLinkId/getLinkId）、SGR 输出 | 部分在 buffer/link 内 |
| `grapheme.zig` | `grapheme.rs` | 字素池 GraphemePool、字素 ID、initGlobalPool/deinitGlobalPool | 未实现 |
| `utf8.zig` | `utf8.rs` | WidthMethod、isAsciiOnly、findWrapBreaks、findTabStops、findLineBreaks、findWrapPosByWidth、findPosByWidth、getWidthAt、getPrevGraphemeStart、calculateTextWidth、findGraphemeInfo 等 | 未实现 |
| `rope.zig` | `rope.rs` | Rope 数据结构（或对接 ropey） | 当前用 ropey，需接口对齐 |
| `buffer.zig` | `buffer.rs` | OptimizedBuffer（Cell、RGBA、get/set、clear、drawText、fillRect、resize、diff 输出、scissor、opacity、drawFrameBuffer）、TextSelection | 当前为简化版 Cell+Buffer |
| `link.zig` | `link.rs` | LinkPool（alloc/get/incref/decref/getRefcount）、SlotHeader、GEN/SLOT 常量、initGlobalLinkPool/deinitGlobalLinkPool | 已实现，需拆出 |
| `terminal.zig` | `terminal.rs` | Terminal、Capabilities、CursorStyle、Options、TerminalInfo、processCapabilityResponse、setCursorPosition/Style/Color、getCursor*、setTerminalTitle、parseXtversion、getTerminalName/Version 等 | 已实现，需拆出 |
| `renderer.zig` | `renderer.rs` | CliRenderer、DebugOverlayCorner、双缓冲、Hit Grid、clipRect、render、dumpBuffers/dumpStdoutBuffer、setDebugOverlay、addToHitGrid/checkHit 等 | 已实现，需拆出 |
| `logger.zig` | `logger.rs` | setLogCallback、log 等级与回调 | 占位 |
| `event-bus.zig` | `event_bus.rs` | setEventCallback、事件总线 | 占位 |
| `event-emitter.zig` | `event_emitter.rs` | EventEmitter 结构 | 占位 |
| `file-logger.zig` | `file_logger.rs` | 文件日志 | 占位 |
| `mem-registry.zig` | `mem_registry.rs` | MemRegistry（内存标记注册） | 未实现 |
| `syntax-style.zig` | `syntax_style.rs` | SyntaxStyle、主题/样式 | 未实现（Python 侧有） |
| `text-buffer-segment.zig` | `text_buffer_segment.rs` | TextChunk、Segment、UnifiedRope(Segment)、WrapMode、Highlight、StyleSpan 等 | 未实现 |
| `text-buffer-iterators.zig` | `text_buffer_iterators.rs` | walkLines、walkLinesAndSegments、getLineCount、getMaxLineWidth、coordsToOffset、offsetToCoords、lineWidthAt、extractTextBetweenOffsets 等 | 未实现 |
| `text-buffer.zig` | `text_buffer.rs` | UnifiedTextBuffer、TextBuffer、setText、insert、delete、高亮与绘制相关 | 当前为 ropey 薄封装，需对齐 |
| `text-buffer-view.zig` | `text_buffer_view.rs` | Viewport、TextBufferView、VirtualLine、MeasureResult、wrap 与视口 | 未实现 |
| `edit-buffer.zig` | `edit_buffer.rs` | EditBuffer、历史、撤销重做、光标与选区 | 未实现 |
| `editor-view.zig` | `editor_view.rs` | EditorView、与 EditBuffer + View 协同 | 未实现 |
| `lib.zig` | `lib.rs` | 仅做 pymodule、mod 声明、pyclass/function 注册与 re-export，不承载业务逻辑 | 当前为单文件，需拆成多 mod |
| `test.zig` | 测试入口见下节 | 仅聚合各测试子模块 | 对应 Rust 的 `tests/` 或 `src/tests.rs` |

**说明**：`build.zig`、`build.zig.zon`、`bench.zig`、`bench-utils.zig` 及 `bench/` 下文件为构建与基准，不要求一一对应 Rust 文件；可选模块（logger、event-bus、event-emitter、file-logger）可先做空壳或最小实现以便编译通过。

### 为何 logger / event_bus / event_emitter 标为「可选」

- **logger.zig → logger.rs**  
  - **在 OpenTUI 中的用途**：`setLogCallback(callback)` 由 TypeScript 在初始化时调用，Zig 内部通过 `logger.warn`/`logger.err`/`logger.debug` 等把诊断信息回传给 JS（例如 renderer.zig 中能力查询失败、text-buffer/view 中分配失败）。  
  - **标为可选的原因**：  
    1. **核心渲染不依赖**：Buffer/Renderer/Terminal/Link 的正确性不依赖“日志是否被上层收到”，只是可观测性。  
    2. **PyTUI 尚未接好**：Python 侧目前没有类似 zig.ts 的 `setLogCallback` 接法，实现完整 logger 暂时没有消费者。  
  - **建议**：先做**空壳/占位**（例如 `set_log_callback` 存指针、`log_message` 内部 no-op 或仅 `eprintln!`），等 Python 需要再接真实回调；这样既与 Zig 文件对应，又不阻塞核心对齐。

- **event-bus.zig → event_bus.rs**  
  - **在 OpenTUI 中的用途**：`setEventCallback(callback)` 由 TypeScript 注册，Zig 通过 `event_bus.emit(name, data)` 向 JS 发事件；当前仅在 **edit-buffer.zig** 中调用（例如发出带 id 的事件）。  
  - **标为可选的原因**：  
    1. **依赖 edit_buffer**：只有实现 EditBuffer 并需要“把事件推到 Python”时，event_bus 才有用。  
    2. **PyTUI 尚未有对等机制**：Python 侧没有像 zig.ts 那样注册 event callback 并处理 name/data。  
  - **建议**：在实现 **edit_buffer** 之前可做**占位**（`set_event_callback` + `emit` 空实现或仅写日志）；实现 edit_buffer 时再补全 event_bus，并与 Python 事件接口对齐。

- **event-emitter.zig → event_emitter.rs**  
  - **在 OpenTUI 中的用途**：**纯 Zig 内部**的泛型 `EventEmitter(EventType)`（on/off/emit），用于枚举事件的订阅/发布，例如 **syntax-style.zig** 里 `emitter.emit(.Destroy)`；**不通过 lib.zig 导出**，没有 C/FFI 层。  
  - **标为可选的原因**：  
    1. **仅被部分模块使用**：当前主要是 syntax_style 使用；text_buffer、renderer、buffer 等核心路径不依赖它。  
    2. **可与 syntax_style 一起实现**：完整移植 syntax_style 时需要 EventEmitter 对等实现；在此之前不影响 Buffer/Renderer/Terminal/Link 的对齐。  
  - **建议**：在实现 **syntax_style** 时一并实现 event_emitter（或等价的 Rust 枚举事件分发）；之前可为空壳或省略，以减小首阶段重构范围。

**总结**：三者都偏“基础设施/可观测性”，不是“画出一帧、处理一次输入”的必经路径；且 PyTUI 侧尚未接好对应回调或事件机制，因此标为可选，便于先完成与 Zig 的**核心模块与测试**对齐，再按需补全。

## 三、Zig 测试文件与 Rust 测试模块映射表

| Zig 测试文件 | Rust 测试模块 | 对应源模块 | 说明 |
|--------------|---------------|------------|------|
| `tests/buffer_test.zig` | `tests/buffer_test.rs` | buffer | OptimizedBuffer、drawText、link、高亮等 |
| `tests/renderer_test.zig` | `tests/renderer_test.rs` | renderer | CliRenderer、双缓冲、drawTextBuffer、link、debug 等 |
| `tests/terminal_test.zig` | `tests/terminal_test.rs` | terminal | xtversion 解析、cursor、capabilities |
| `tests/link.zig`（无独立 test 文件，逻辑在 buffer/renderer 测试中） | 随 buffer_test / renderer_test | link | LinkPool alloc/get/incref/decref |
| `tests/utf8_test.zig` | `tests/utf8_test.rs` | utf8 | isAsciiOnly、line breaks、tab stops、wrap、width、getPrevGraphemeStart、findGraphemeInfo 等 |
| `tests/utf8_wcwidth_test.zig` | `tests/utf8_wcwidth_test.rs` | utf8 | wcwidth 模式下的宽度与字素 |
| `tests/utf8_no_zwj_test.zig` | `tests/utf8_no_zwj_test.rs` | utf8 | 无 ZWJ 相关边界 |
| `tests/grapheme_test.zig` | `tests/grapheme_test.rs` | grapheme | GraphemePool、字素 ID |
| `tests/rope_test.zig` | `tests/rope_test.rs` | rope | Rope 插入、删除、切片 |
| `tests/rope-nested_test.zig` | `tests/rope_nested_test.rs` | rope | 嵌套结构 |
| `tests/rope_fuzz_test.zig` | `tests/rope_fuzz_test.rs` | rope | 随机操作 |
| `tests/syntax-style_test.zig` | `tests/syntax_style_test.rs` | syntax_style | 样式与主题 |
| `tests/mem-registry_test.zig` | `tests/mem_registry_test.rs` | mem_registry | MemRegistry |
| `tests/event-emitter_test.zig` | `tests/event_emitter_test.rs` | event_emitter | EventEmitter |
| `tests/text-buffer-segment_test.zig` | `tests/text_buffer_segment_test.rs` | text_buffer_segment | Segment、TextChunk |
| `tests/text-buffer-iterators_test.zig` | `tests/text_buffer_iterators_test.rs` | text_buffer_iterators | walkLines、coords、offset |
| `tests/text-buffer_test.zig` | `tests/text_buffer_test.rs` | text_buffer | UnifiedTextBuffer、setText、insert、delete |
| `tests/text-buffer-view_test.zig` | `tests/text_buffer_view_test.rs` | text_buffer_view | Viewport、wrap、VirtualLine |
| `tests/text-buffer-drawing_test.zig` | `tests/text_buffer_drawing_test.rs` | buffer + text_buffer | 绘制到 buffer |
| `tests/text-buffer-highlights_test.zig` | `tests/text_buffer_highlights_test.rs` | text_buffer + syntax_style | 高亮 |
| `tests/text-buffer-selection_test.zig` | `tests/text_buffer_selection_test.rs` | text_buffer + buffer | 选区 |
| `tests/text-buffer-selection_viewport_test.zig` | `tests/text_buffer_selection_viewport_test.rs` | text_buffer_view | 选区与视口 |
| `tests/edit-buffer_test.zig` | `tests/edit_buffer_test.rs` | edit_buffer | EditBuffer、编辑与历史 |
| `tests/edit-buffer-history_test.zig` | `tests/edit_buffer_history_test.rs` | edit_buffer | 撤销/重做 |
| `tests/editor-view_test.zig` | `tests/editor_view_test.rs` | editor_view | EditorView |
| `tests/segment-merge.test.zig` | `tests/segment_merge_test.rs` | edit_buffer / segment | 段合并 |
| `tests/word-wrap-editing_test.zig` | `tests/word_wrap_editing_test.rs` | edit_buffer + view | 折行与编辑 |
| `tests/wrap-cache-perf_test.zig` | `tests/wrap_cache_perf_test.rs` | text_buffer_view | 折行缓存性能（可先占位） |
| `tests/memory_leak_regression_test.zig` | `tests/memory_leak_regression_test.rs` | grapheme | 内存泄漏回归 |

## 四、模块依赖顺序（实现顺序建议）

```
Level 0（无 Zig 依赖）:
  utils.rs, logger.rs（可选）, event_emitter.rs（可选）, event_bus.rs（可选）

Level 1:
  ansi.rs（仅常量与 TextAttributes，可依赖 utils）

Level 2:
  utf8.rs（依赖 uucode/unicode-width 等，无内部 zig 依赖）
  grapheme.rs（依赖 utf8 概念，可有自己的池）

Level 3:
  rope.rs 或 rope_adapter.rs（对接 ropey，接口对齐 zig Rope）
  mem_registry.rs
  syntax_style.rs

Level 4:
  text_buffer_segment.rs（依赖 rope, buffer, mem_registry, grapheme, utf8）
  text_buffer_iterators.rs（依赖 text_buffer_segment, utf8, mem_registry）

Level 5:
  buffer.rs（依赖 ansi, grapheme, link；当前已有简化版）
  link.rs（仅依赖 ansi 中 setLinkId/getLinkId，可独立）

Level 6:
  terminal.rs（依赖 ansi）
  text_buffer.rs（依赖 text_buffer_segment, text_buffer_iterators, syntax_style, grapheme, utf8, mem_registry）

Level 7:
  text_buffer_view.rs（依赖 text_buffer, text_buffer_iterators, text_buffer_segment, grapheme, utf8）
  edit_buffer.rs（依赖 text_buffer, text_buffer_view, grapheme）

Level 8:
  editor_view.rs（依赖 edit_buffer, text_buffer_view, buffer）
  renderer.rs（依赖 buffer, terminal, link, ansi；当前已有）
```

**说明**：先拆出已有逻辑（link、terminal、buffer、renderer、cell）到对应 `*.rs`，再按上表从 Level 0 起逐步补齐缺失模块并补全测试。

## 五、详细执行步骤

### 阶段 A：拆分现有 lib.rs 为多文件（不新增 Zig 功能）

**A.1 创建目录与占位模块**

1. 在 `pytui/src/pytui/native/src/` 下确认仅保留 `lib.rs` 为入口，其余为模块文件。
2. 新建与 Zig 对应的空模块文件（仅 `mod xxx;` 或空实现），便于后续迁移：
   - `utils.rs`, `ansi.rs`, `grapheme.rs`, `utf8.rs`, `rope.rs`, `buffer.rs`, `link.rs`, `terminal.rs`, `renderer.rs`, `text_buffer.rs`
   - 可选：`logger.rs`, `event_bus.rs`, `event_emitter.rs`, `file_logger.rs`, `mem_registry.rs`, `syntax_style.rs`, `text_buffer_segment.rs`, `text_buffer_iterators.rs`, `text_buffer_view.rs`, `edit_buffer.rs`, `editor_view.rs`

**A.2 抽取几何与内部类型（对齐 buffer.zig 中的 ClipRect）**

3. 新增 `geometry.rs`（或并入 `buffer.rs`）：从当前 `lib.rs` 移出 `ClipRect`，供 `renderer` 使用。
4. 在 `lib.rs` 中声明 `mod geometry;`，其余模块通过 `use crate::geometry::ClipRect` 使用。

**A.3 抽取 terminal（对齐 terminal.zig）**

5. 新建 `terminal.rs`：将当前 `lib.rs` 中的 `CursorStyle`、`Terminal` 及其全部 `impl`（含 `process_capability_response`、cursor/term name/version、ANSI 生成、`set_term_info_for_test`）移入。
6. `terminal.rs` 内不暴露 PyO3，仅纯 Rust 类型与逻辑；`lib.rs` 或 `renderer.rs` 中 `use crate::terminal::{Terminal, CursorStyle}`。
7. 在 `lib.rs` 中声明 `mod terminal;`，并保留现有对 Terminal 的调用（通过 renderer 或 lib 转发）。

**A.4 抽取 ansi 与 link（对齐 ansi.zig / link.zig）**

8. 新建 `ansi.rs`：定义 ANSI 常量（如 clear、home、hideCursor、showCursor、cursorBlock 等）、`TextAttributes` 相关：`ATTRIBUTE_BASE_MASK`、`LINK_ID_BITS`、`LINK_ID_SHIFT`、`LINK_ID_PAYLOAD_MASK`、`LINK_ID_MASK`，以及 `set_link_id(attr, link_id)`、`get_link_id(attr)`（与当前 `attributes_with_link` / `get_link_id_from_attributes` 行为一致）。
9. 新建 `link.rs`：将当前 `lib.rs` 中的 `GEN_BITS`、`SLOT_BITS`、`SlotHeader`、`LinkPool` 及 `alloc/get/incref/decref/get_refcount` 移入；`attributes_with_link` / `get_link_id_from_attributes` 可留在 `lib.rs` 中调用 `ansi::set_link_id` / `ansi::get_link_id`，或改为 re-export ansi 的函数。
10. 在 `lib.rs` 中声明 `mod ansi;`、`mod link;`，并从 `link` 中 `pub use` 需要在 PyO3 中注册的 `LinkPool` 及常量（如 `MAX_URL_LENGTH`）。

**A.5 抽取 cell 与 buffer（对齐 buffer.zig）**

11. 新建 `cell.rs`：将当前 `lib.rs` 中的 `Cell`、`cell_eq`、`cell_to_ansi_sgr` 移入；`Cell` 保留 `#[pyclass]`，在 `lib.rs` 的 `pymodule` 中继续注册。
12. 新建 `buffer.rs`：将当前 `lib.rs` 中的 `Buffer` 及其实例方法（含 `diff_and_output_ansi`）移入；`Buffer` 依赖 `cell::Cell` 与 `cell_eq`/`cell_to_ansi_sgr`，通过 `use crate::cell` 引用。
13. 在 `lib.rs` 中声明 `mod cell;`、`mod buffer;`，并保留对 `Buffer`、`Cell` 的 PyO3 注册。

**A.6 抽取 renderer（对齐 renderer.zig）**

14. 新建 `renderer.rs`：将当前 `lib.rs` 中的 `DebugOverlayCorner`、`CliRenderer` 及全部方法移入；`CliRenderer` 依赖 `Terminal`、`ClipRect`、`Buffer`（Py<Buffer>）、`link`/`ansi` 按需引用。
15. 在 `lib.rs` 中声明 `mod renderer;`，并保留对 `CliRenderer` 的 PyO3 注册；`renderer.rs` 内通过 `use crate::terminal::CursorStyle` 等引用。

**A.7 抽取 text_buffer（对齐 text-buffer.zig 的当前简化实现）**

16. 新建 `text_buffer.rs`：将当前 `lib.rs` 中的 `TextBuffer`（基于 ropey）及其实例方法移入。
17. 在 `lib.rs` 中声明 `mod text_buffer;`，并保留对 `TextBuffer` 的 PyO3 注册。

**A.8 统一入口 lib.rs**

18. `lib.rs` 仅保留：  
    - `mod ansi;`、`mod buffer;`、`mod cell;`、`mod geometry;`、`mod link;`、`mod renderer;`、`mod terminal;`、`mod text_buffer;`  
    - 以及可选/占位模块声明。  
    - `#[cfg(test)] mod tests;` 指向独立测试模块（见阶段 B）。  
    - `#[pymodule] fn pytui_native(...)` 中：注册各 pyclass、pyfunction，并从对应模块 `pub use` 或直接 `use crate::xxx::Yyy` 注册。
19. 运行 `cargo build`（或带 feature 的 build）与 `cargo test --features test`，确认拆分后行为与拆分前一致。

### 阶段 B：独立测试模块与 OpenTUI 测试一一对应

**B.1 测试目录结构**

20. 在 `pytui/src/pytui/native/src/` 下新建 `tests.rs`（或 `tests/mod.rs` + 子模块），由 `lib.rs` 中 `#[cfg(test)] mod tests;` 引用。
21. 测试模块内部按 Zig 测试文件划分子模块（与“三、测试映射表”一致），例如：
    - `tests::buffer_test`
    - `tests::renderer_test`
    - `tests::terminal_test`
    - `tests::link_test`（或并入 buffer_test/renderer_test）
    - 后续：`tests::utf8_test`、`tests::grapheme_test`、`tests::rope_test` 等。

**B.2 从现有 lib.rs 内联测试迁出**

22. 将当前 `lib.rs` 中 `#[cfg(test)] mod tests { ... }` 内的全部测试函数按主题迁到 `tests.rs` 对应子模块：
    - Buffer 相关 → `tests::buffer_test`
    - CliRenderer / Hit Grid 相关 → `tests::renderer_test`
    - Terminal / xtversion / cursor 相关 → `tests::terminal_test`
    - LinkPool / attributes_with_link 相关 → `tests::link_test` 或 `tests::renderer_test`
23. 在 `tests.rs` 中保留公共辅助函数（如 `with_py`），供各子模块使用。
24. 运行 `cargo test --features test`，确保所有现有测试仍通过。

**B.3 测试命名与用例对齐 Zig**

25. 对照 `opentui/packages/core/src/zig/tests/buffer_test.zig`、`renderer_test.zig`、`terminal_test.zig` 等，将 Rust 测试函数名与 Zig 中 `test "xxx"` 的字符串保持一致（可把空格与特殊字符换成下划线），并在注释中标明对应 Zig 测试名。
26. 对每个已实现的 Zig 测试用例，在 Rust 中补全等价断言与场景（如 buffer 的 clear、drawText、resize、diff、link 高亮等），使行为与 Zig 一致。
27. 新增或调整测试时，以 Zig 测试文件为“单一事实来源”，逐条对齐并注明 `// Aligns: tests/xxx_test.zig - "test name"`。

### 阶段 C：按依赖顺序补齐缺失模块与测试（与 Zig 完全对齐）

**C.1 utils / ansi**

28. 实现 `utils.rs`：RGBA 类型、f32 到 RGBA 的转换等，与 `utils.zig` 一致。
29. 完善 `ansi.rs`：补全 Zig 中使用的 ANSI 常量及 TextAttributes 的 apply 等（若 renderer/buffer 需要）。

**C.2 utf8 / grapheme**

30. 实现 `utf8.rs`：WidthMethod、isAsciiOnly、findWrapBreaks、findTabStops、findLineBreaks、findWrapPosByWidth、findPosByWidth、getWidthAt、getPrevGraphemeStart、calculateTextWidth、findGraphemeInfo 等，与 `utf8.zig` 行为一致（可依赖 `unicode-width`、`uucode` 等 crate）。
31. 实现 `utf8_test.rs`、`utf8_wcwidth_test.rs`、`utf8_no_zwj_test.rs`：逐条对齐 Zig 中对应 `test "..."`。
32. 实现 `grapheme.rs`：GraphemePool、字素 ID、initGlobalPool/deinitGlobalPool，与 `grapheme.zig` 一致。
33. 实现 `grapheme_test.rs`、`memory_leak_regression_test.rs`：与 Zig 对应用例对齐。

**C.3 rope / mem_registry / syntax_style**

34. 实现或适配 `rope.rs`：与 `rope.zig` 接口对齐；若继续使用 ropey，则提供一层适配器，使对外 API 与 Zig Rope 一致。
35. 实现 `rope_test.rs`、`rope_nested_test.rs`、`rope_fuzz_test.rs`。
36. 实现 `mem_registry.rs` 及 `mem_registry_test.rs`。
37. 实现 `syntax_style.rs` 及 `syntax_style_test.rs`（可与 Python 侧 theme 对齐）。

**C.4 text_buffer_segment / text_buffer_iterators / text_buffer / text_buffer_view**

38. 实现 `text_buffer_segment.rs` 及 `text_buffer_segment_test.rs`。
39. 实现 `text_buffer_iterators.rs` 及 `text_buffer_iterators_test.rs`。
40. 扩展 `text_buffer.rs` 为与 Zig UnifiedTextBuffer 对齐（含 segment、iterators、syntax_style、mem_registry），并实现 `text_buffer_test.rs`、`text_buffer_drawing_test.rs`、`text_buffer_highlights_test.rs`、`text_buffer_selection_test.rs` 等。
41. 实现 `text_buffer_view.rs` 及 `text_buffer_view_test.rs`、`text_buffer_selection_viewport_test.rs`、`word_wrap_editing_test.rs`、`wrap_cache_perf_test.rs`、`segment_merge_test.rs`。

**C.5 buffer 完整对齐**

42. 扩展 `buffer.rs`：在现有 Cell/Buffer 基础上，对齐 Zig OptimizedBuffer（grapheme 池、link 池、drawTextBuffer、scissor、opacity、drawFrameBuffer、RGBA 等）；若需保留当前简化版 PyO3 Buffer，可保留为 ThinBuffer，内部委托给 OptimizedBuffer 或与 OptimizedBuffer 共享逻辑。
43. 补全 `buffer_test.rs`：与 `tests/buffer_test.zig` 中全部用例对齐（含 link、高亮、drawTextBuffer 等）。

**C.6 edit_buffer / editor_view**

44. 实现 `edit_buffer.rs` 及 `edit_buffer_test.rs`、`edit_buffer_history_test.rs`。
45. 实现 `editor_view.rs` 及 `editor_view_test.rs`。

**C.7 renderer 完整对齐**

46. 在 `renderer.rs` 中补齐与 Zig 一致的逻辑（如 drawTextBuffer、hyperlink、debug overlay 绘制、dump 等），并确保 `renderer_test.rs` 与 `tests/renderer_test.zig` 逐条对应。

### 阶段 D：收尾与文档

47. 在 `pytui/src/pytui/native/README.md` 中更新模块列表、与 Zig 的对应关系，以及如何运行测试（`cargo test --features test`）。
48. 在 `pytui/docs/opentui-zig-alignment-options.md` 中注明：Rust 模块与测试已按本计划与 OpenTUI Zig 一一对应，并附本计划文档链接。
49. 全量运行 `cargo test --features test` 与 Python 侧测试，确保无回归。

## 六、Rust 源码目录结构（目标）

```
pytui/src/pytui/native/src/
├── lib.rs                 # pymodule、mod 声明、PyO3 注册
├── utils.rs
├── ansi.rs
├── geometry.rs            # ClipRect 等（或并入 buffer.rs）
├── cell.rs
├── buffer.rs
├── link.rs
├── terminal.rs
├── renderer.rs
├── text_buffer.rs
├── grapheme.rs
├── utf8.rs
├── rope.rs
├── mem_registry.rs
├── syntax_style.rs
├── text_buffer_segment.rs
├── text_buffer_iterators.rs
├── text_buffer_view.rs
├── edit_buffer.rs
├── editor_view.rs
├── logger.rs              # 可选
├── event_bus.rs           # 可选
├── event_emitter.rs        # 可选
├── file_logger.rs          # 可选
└── tests.rs               # #[cfg(test)] 统一测试入口
    └── 内部按 Zig 测试文件分块：buffer_test, renderer_test, terminal_test, link_test, utf8_test, ...
```

（若采用 `tests/` 子目录，则可为 `tests/mod.rs` + `tests/buffer_test.rs`、`tests/renderer_test.rs` 等。）

## 七、检查清单（每完成一个模块/测试文件可勾选）

- [ ] 每个 Zig 源文件都有对应 Rust 模块文件且命名对应
- [ ] 每个 Zig 测试文件都有对应 Rust 测试模块且用例名称/行为对齐
- [ ] `lib.rs` 仅负责 mod 与 pymodule，无业务逻辑
- [ ] 所有现有 PyO3 接口（pyclass、pyfunction）仍可正常导入与调用
- [ ] `cargo test --features test` 全绿
- [ ] 文档（README、alignment 文档）已更新并指向本计划

---

## 八、后续补全（可选模块与整体对齐）

在完成阶段 A～D、核心模块与测试与 Zig 对齐后，可按需按下列顺序补全可选模块与 Python 侧对接。

### 8.1 logger.rs 补全

1. **Rust 侧**  
   - 若当前为占位：在 `logger.rs` 中保留 `set_log_callback(callback: Option<...>)` 的 PyO3 导出（或通过 `lib.rs` 注册为 `setLogCallback`），并实现 `log_message(level, format, args)`，在 `global_log_callback.is_some()` 时调用回调，否则 no-op 或 `eprintln!`。  
   - 与 Zig 一致：`LogLevel` 枚举（err/warn/info/debug）、`log_message` 内部格式化后以 `(level, msg_ptr, msg_len)` 调用 C 风格回调。  
   - 在 `renderer.rs`、`text_buffer.rs`、`text_buffer_view.rs` 等中，将现有 `eprintln!`/未实现处改为 `logger::warn(...)` / `logger::err(...)`（与 Zig 调用点一致）。

2. **Python 侧**  
   - 在 `pytui/core/renderer.py` 或初始化入口中，向 `pytui_native` 注册日志回调：例如 `pytui_native.set_log_callback(callback)`，`callback(level: int, msg: bytes)` 中根据 level 转发到 `logging` 或自定义输出。  
   - 参考 OpenTUI 的 zig.ts：在加载 native 后调用 `setLogCallback`，回调内把 `(level, msgPtr, msgLen)` 转成字符串再交给 JS 的 log。

3. **验证**  
   - 触发一次会打日志的路径（如能力查询失败、分配失败），确认 Python 侧能收到并输出。

### 8.2 event_bus.rs 补全

1. **Rust 侧**  
   - 若当前为占位：在 `event_bus.rs` 中实现 `set_event_callback(callback: Option<...>)` 与 `emit(name: &[u8], data: &[u8])`；回调签名与 Zig 一致 `(name_ptr, name_len, data_ptr, data_len)`。  
   - 在实现 **edit_buffer.rs** 时，在 Zig 调用 `event_bus.emit(...)` 的对应位置（例如历史/选区变更通知）调用 `event_bus::emit(name, data)`。

2. **Python 侧**  
   - 提供 `pytui_native.set_event_callback(callback)`，`callback(name: bytes, data: bytes)` 由上层（如 Renderer/App）注册；在回调里根据 `name` 解析 `data` 并更新状态或触发 Python 侧事件（如 `on_capability_response`、`on_edit_event`）。  
   - 参考 zig.ts：在初始化时 `setEventCallback`，在回调里解析 name/data 并 dispatch 到 TypeScript 事件。

3. **验证**  
   - 实现 edit_buffer 后，执行会触发 emit 的操作（如一次编辑），确认 Python 侧能收到对应 name/data。

### 8.3 event_emitter.rs 补全

1. **Rust 侧**  
   - 实现与 Zig 等价的泛型 `EventEmitter<EventType>`：`on(event, listener)`、`off(event, listener)`、`emit(event)`，其中 `EventType` 为枚举，listener 为闭包或函数指针封装。  
   - 在实现 **syntax_style.rs** 时，按 Zig 的 `syntax-style.zig` 使用方式，在销毁等时机调用 `emitter.emit(.Destroy)` 等。  
   - 可单独建 `tests/event_emitter_test.rs`，与 `tests/event-emitter_test.zig` 用例对齐。

2. **Python 侧**  
   - EventEmitter 为 Rust 内部使用，一般不暴露给 Python；若将来需要“样式销毁”等事件通知到 Python，再在 event_bus 或单独 PyO3 接口中暴露。

3. **验证**  
   - `cargo test --features test` 中 event_emitter 与 syntax_style 相关测试通过。

### 8.4 file_logger.rs（若需要）

- Zig 的 `file-logger.zig` 为可选的“写文件日志”。若 PyTUI 需要同等能力，可新增 `file_logger.rs`，实现“按配置写日志到文件”，并由 logger 或独立入口调用；否则可保持不实现或空壳。

### 8.5 整体对齐的收尾顺序建议

1. 先完成 **阶段 A～D**（拆分 + 测试独立 + 按依赖补齐 buffer/utf8/grapheme/rope/text_buffer*/edit_buffer/editor_view 等）。  
2. 再按需补全 **logger**（便于排查问题）→ **event_bus**（与 edit_buffer 一起）→ **event_emitter**（与 syntax_style 一起）。  
3. 每补全一个可选模块，在 README 与 alignment 文档中注明“已实现”，并跑一遍全量测试与 Python 侧用例。

---

本计划为“完全对齐 OpenTUI Zig 的 Rust 重构”的详细执行步骤；实际推进时可按阶段 A → B → C → D 分步执行，每步完成后跑测试与构建以保持可交付状态；可选模块按**八、后续补全**在核心对齐完成后再做。
