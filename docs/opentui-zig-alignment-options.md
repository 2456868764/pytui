# 完全对齐 OpenTUI Zig 功能的方案

OpenTUI 的 Zig 层（`opentui/packages/core/src/zig/`）通过 **Bun FFI (dlopen)** 加载为动态库，提供渲染、Buffer、终端、Hit Grid 等能力。PyTUI 当前为纯 Python（含可选 Rust 扩展：Cell/Buffer/TextBuffer）。以下方案用于「完全对齐」Zig 功能。

**采用方案：方案 B（用 Rust 重写 Zig 层，PyO3 暴露给 Python）**  
- PyTUI 在 Rust 中实现与 OpenTUI Zig 等价的 renderer、buffer、terminal、hit grid、cursor、link 等逻辑，通过 PyO3 扩展暴露给 Python；不依赖 OpenTUI 的构建产物，可独立构建与发版。  
- Renderer 在「native 扩展可用」时走 Rust 路径，否则回退到当前纯 Python 实现。

---

## 一、OpenTUI Zig 层职责概览

| 模块 | 功能 | 典型符号 / 行为 |
|------|------|------------------|
| **renderer.zig** | 渲染循环、双缓冲、输出、统计 | `createRenderer`, `destroyRenderer`, `render`, `getNextBuffer`, `getCurrentBuffer`, `resizeRenderer`, `setRenderOffset`, `setupTerminal`, `suspendRenderer`, `resumeRenderer`, `updateStats`, `updateMemoryStats` |
| **buffer.zig** | 单元格缓冲、diff、ANSI 编码、绘制 | `createOptimizedBuffer`, `bufferClear`, `bufferSetCell`, `bufferDrawText`, `bufferFillRect`, `bufferResize`, `bufferPushScissorRect`, `bufferPopScissorRect`, `bufferPushOpacity`, `bufferPopOpacity`, `bufferDrawBox`, `bufferDrawPackedBuffer` 等 |
| **terminal.zig** | 终端设置、光标、标题、能力查询 | `setCursorPosition`, `setCursorStyle`, `setCursorColor`, `getCursorState`, `setTerminalTitle`, `clearTerminal`, `queryPixelResolution` |
| **Hit Grid** | 鼠标命中检测（每格存 renderable id） | `addToHitGrid`, `hitGridPushScissorRect`, `hitGridPopScissorRect`, `hitGridClearScissorRects`, `checkHit`, `dumpHitGrid` |
| **能力 / 分辨率** | 终端能力、像素分辨率 | `processCapabilityResponse`, `getTerminalCapabilities` |
| **键盘** | Kitty 键盘协议 | `setKittyKeyboardFlags`, `enableKittyKeyboard`, `disableKittyKeyboard` |
| **鼠标** | 原始鼠标协议 | `enableMouse`, `disableMouse` |
| **调试** | 覆盖层、Buffer 导出 | `setDebugOverlay`, `dumpBuffers`, `dumpStdoutBuffer` |
| **Link** | OSC 8 链接池 | `linkAlloc`, `linkGetUrl`, `attributesWithLink`, `attributesGetLinkId` |
| **其他** | 事件/日志回调、Arena 统计 | `setLogCallback`, `setEventCallback`, `getArenaAllocatedBytes` |

Zig 通过 `lib.zig` 的 `export fn` 暴露 **C ABI**，由 TypeScript 的 `zig.ts` 用 Bun FFI 声明并调用。

---

## 二、对齐方案对比

### 方案 A：复用 OpenTUI 的 Zig 编译产物（ctypes/cffi）

**做法**  
- 使用 OpenTUI 现有构建产出（如 `@opentui/core-darwin-arm64` 等）的 `.so` / `.dylib` / `.dll`。  
- 在 Zig 侧确认/补充 **C ABI** 导出（当前已是 `export fn`，即 C 约定）。  
- 在 PyTUI 中用 **ctypes** 或 **cffi** 加载该动态库，按 `zig.ts` 的符号表声明函数签名并调用。  
- PyTUI 的 `Renderer` 在「native 可用」时：创建 renderer 指针、用 native buffer、每帧调用 `render(ptr, force)`、Hit 用 `checkHit` 等；否则回退到当前纯 Python 实现。

**优点**  
- 零重写 Zig，行为与 OpenTUI 完全一致。  
- 性能、内存布局与 OpenTUI 一致。

**缺点**  
- 依赖 OpenTUI 的构建与发布产物（需按平台提供库）。  
- 需维护与 `zig.ts` 一致的 FFI 声明（参数/返回值/类型）。  
- 需约定 ABI 稳定（或随 OpenTUI 版本一起发 PyTUI 兼容版本）。  
- 指针与 Buffer 在 Python 侧需用 ctypes 包装（或通过 native 层封装成简单 API）。

**适用**  
- 希望与 OpenTUI 共享同一套二进制、优先保证行为一致时。

---

### 方案 B：用 Rust 重写 Zig 层，PyO3 暴露给 Python

**做法**  
- 将 OpenTUI 的 Zig 逻辑（renderer、buffer、terminal、hit grid、cursor、link 等）在 **Rust** 中重写一份。  
- 通过 **PyO3** 做成 Python 扩展模块：  
  - 暴露「Renderer 句柄 + Buffer 句柄 + 一帧内 API」（如 create/destroy/render/resize/setBackground/addToHitGrid/checkHit 等）。  
  - 或暴露与 zig.ts 类似的 C ABI（Rust `#[no_mangle] extern "C"`），再由 Python 用 ctypes 调用（与方案 A 的调用方式统一）。  
- PyTUI 的 `Renderer` 检测 native 扩展是否可用：可用则走 Rust 路径，不可用则走当前纯 Python 路径。

**优点**  
- 不依赖 OpenTUI 的构建产物，PyTUI 可独立构建、发版。  
- 可与现有 `pytui/native`（Cell/Buffer/TextBuffer）共用一个 Rust 工程，逐步迁移/替换。  
- 行为可按 OpenTUI 严格对齐（单元测试/快照对比）。

**缺点**  
- 工作量大：需移植 renderer、buffer diff、ANSI 输出、terminal、hit grid、cursor、link 等全部逻辑。  
- 需长期与 OpenTUI Zig 变更做对比与回归。

**适用**  
- 希望 PyTUI 独立于 OpenTUI 构建、且愿意投入移植与维护时。

---

### 方案 C：纯 Python 实现「行为等价」

**做法**  
- 不引入任何 native 库；在 PyTUI 内用 Python 实现与 Zig **行为等价** 的逻辑：  
  - Buffer：保持/扩展当前 `OptimizedBuffer`，实现与 Zig 一致的 diff 策略（按行/按区域）、ANSI 编码与输出。  
  - Hit Grid：用二维数组（或稀疏结构）存每格 renderable id，实现 `addToHitGrid`、scissor 栈、`checkHit`。  
  - Terminal：光标位置/样式/颜色、标题、能力查询（若需）用 ANSI 序列 + 现有 `Terminal` 封装。  
  - 渲染循环：与 OpenTUI 相同的阶段顺序（frame callback → 布局 → 渲染 → postProcess → diff → 输出）。  
- 对外 API 与 OpenTUI 的 renderer/buffer 接口一一对应（方法名、参数、语义）。

**优点**  
- 无额外 native 依赖，跨平台一致，易调试、易 CI。  
- 可逐步分模块对齐（先 buffer diff，再 hit grid，再 terminal 能力等）。

**缺点**  
- 性能不如 C/Rust/Zig，尤其在超大终端或高帧率下；可通过「只 diff 脏区域」、减少 Python 层拷贝等方式缓解。  
- 需通过测试/快照与 OpenTUI 对比，保证行为一致。

**适用**  
- 优先考虑可维护性与跨平台，对极限性能要求不极端时。

---

### 方案 D：混合——仅热路径用 Rust

**做法**  
- **热路径**（每帧执行）：buffer diff、ANSI 编码、stdout 写入 用 Rust 实现（PyO3 扩展或 C ABI 小库），由 Python 传入前后帧 buffer 或脏区域，native 返回要输出的字节。  
- **冷路径**：Hit grid、cursor、terminal 标题、能力查询、debug overlay 等仍用 Python 实现（或后续再部分迁到 Rust）。  
- Renderer 在「有 native」时：每帧把 back_buffer 交给 Rust 做 diff+编码+写；无 native 时用当前纯 Python 输出。

**优点**  
- 性能收益集中在最耗时的部分，移植量小于方案 B。  
- 与现有 `pytui/native` 的 Buffer/Cell 可逐步统一（如 Rust 端统一握有 buffer 内存）。

**缺点**  
- 仍需维护 Rust 与 Python 的接口约定；Hit grid 等若日后也要对齐 Zig，可能还要在 Rust 里实现一份。

**适用**  
- 希望尽快获得接近 OpenTUI 的渲染性能，又不想一次性移植全部 Zig 时。

---

## 三、采用方案 B 的实施顺序（推荐）

1. **阶段一：Buffer 与渲染输出**  
   - 在 `pytui/native` 中实现与 OpenTUI `buffer.zig` 等价的 **OptimizedBuffer**（单元格缓冲、diff、ANSI 编码、setCell/drawText/fillRect/scissor/opacity 等），通过 PyO3 暴露给 Python。  
   - Renderer 在「native 可用」时：使用 Rust 的 buffer 做前后帧 diff，由 Rust 生成 ANSI 并写入 stdout；否则沿用当前纯 Python 的 `_diff_and_output`。

2. **阶段二：Renderer 与双缓冲**  
   - 在 Rust 中实现 **CliRenderer** 核心（create/destroy、getNextBuffer/getCurrentBuffer、resize、setRenderOffset、render、updateStats、setBackgroundColor 等），与 `renderer.zig` 行为对齐。  
   - Python 的 `Renderer` 持有 Rust renderer 句柄（或通过 PyO3 封装的 Python 对象），每帧调用 native render，并从 native 取 buffer 供布局/绘制写入。

3. **阶段三：Hit Grid 与鼠标**  
   - 在 Rust 中实现 **Hit Grid**（addToHitGrid、scissor 栈、checkHit、clearCurrentHitGrid 等），与 Zig 一致。  
   - Python 的 `add_to_hit_grid`、`hit_test` 等转发到 native；鼠标事件分发使用 native checkHit 结果。

4. **阶段四：Terminal、光标、能力**（已完成）  
   - 在 Rust 中实现 **Terminal** 相关（setCursorPosition、setCursorStyle、setCursorColor、getCursorState、setTerminalTitle、clearTerminal、processCapabilityResponse、getTerminalName/Version、cursor*Ansi 等），与 `terminal.zig` 对齐；**CliRenderer** 内嵌 Terminal 并暴露上述方法。  
   - Rust 单元测试与 `terminal_test.zig` 对齐（xtversion 解析 kitty/ghostty/tmux、前缀数据、完整响应、环境覆盖、仅名称、空响应；光标位置/样式/颜色及 ANSI 输出）。

5. **阶段五：Link、调试、其余**（已完成）  
   - **Link 池**：Rust `LinkPool` pyclass（alloc、get、incref、decref、get_refcount），与 `link.zig` 对齐；ID 布局 GEN_BITS=8、SLOT_BITS=16、MAX_URL_LENGTH=512；模块级函数 `attributes_with_link(base_attributes, link_id)`、`get_link_id_from_attributes(attr)` 与 ansi.zig TextAttributes 对齐。  
   - **Debug Overlay**：CliRenderer 增加 `debug_overlay_enabled`、`debug_overlay_corner`（0=topLeft～3=bottomRight），`set_debug_overlay(enabled, corner)`、`get_debug_overlay()`。  
   - **Dump**：`last_rendered_output` 在每帧 `render()` 后保存；`dump_buffers(py, timestamp)` 写出 current/next buffer 字符网格及 stdout 到 `buffer_dump/`；`dump_stdout_buffer(timestamp)` 写出上次渲染的 ANSI 到 `buffer_dump/stdout_buffer_{timestamp}.txt`。  
   - Rust 单元测试覆盖 LinkPool（alloc/get、incref/decref/refcount、复用、URL 过长）、attributes_with_link/get_link_id、debug_overlay、dump_stdout_buffer、dump_buffers。

---

## 四、方案 A（复用 Zig 库）的技术要点（未采用，供参考）

1. **ABI 稳定**  
   - OpenTUI Zig 已用 `export fn`（C 约定）；需保证结构体布局、指针语义与 zig.ts 一致，避免 ABI 破坏。

2. **Python 侧**  
   - 使用 `ctypes.CDLL(lib_path)` 或 `cffi.FFI().dlopen(lib_path)` 加载。  
   - 为每个 `export fn` 声明 `argtypes` / `restype`（与 zig.ts 的 args/returns 对应）。  
   - Renderer/Buffer 等以指针（c_void_p 或具体结构）在 Python 中持有，所有调用都传指针。

3. **Buffer 数据**  
   - Zig 的 `getNextBuffer` 返回指针；Python 可通过 `bufferGetCharPtr`、`bufferGetFgPtr` 等拿到裸指针，用 ctypes 的 `from_buffer` 或 numpy 等封装成可读写的数组，再在 Python 层做「从 Renderable 树写入 buffer」的逻辑；或由 Zig 层提供「从某内存块填充 buffer」的接口，减少 Python 与 native 之间的拷贝。

4. **平台库路径**  
   - 与 OpenTUI 一样，按 `platform-arch` 选择库（如 `core-darwin-arm64.dylib`）；可通过 `pip` 包内带预编译库，或单独下载/构建脚本安装。

---

## 五、小结

| 方案 | 行为一致 | 性能 | 工作量 | 依赖 |
|------|----------|------|--------|------|
| A：复用 Zig 库 | 完全一致 | 与 OpenTUI 同 | 中（FFI + 集成） | OpenTUI 构建产物 |
| **B：Rust 重写（采用）** | **可完全一致** | **高** | **大** | **无** |
| C：纯 Python | 可完全一致 | 中 | 中 | 无 |
| D：混合热路径 | 可完全一致 | 较高 | 中～大 | 无（仅 PyTUI Rust） |

**当前采用：方案 B**。在 Rust 中重写与 OpenTUI Zig 等价的逻辑，通过 PyO3 暴露给 Python；PyTUI 不依赖 OpenTUI 构建产物，可独立构建与发版，行为与性能均可与 OpenTUI 对齐。

---

## 六、Rust 与 Zig 一一对齐状态

Rust 原生层（`pytui/src/pytui/native/`）已按 **[Rust 重构与 OpenTUI Zig 完全对齐执行计划](rust-refactor-opentui-alignment-plan.md)** 进行拆分与对齐：

- **模块**：每个 Zig 源文件（`opentui/packages/core/src/zig/*.zig`）对应一个 Rust 模块（`native/src/*.rs`），命名与职责一一对应。
- **测试**：测试集中在 `native/src/tests.rs`，子模块与 `opentui/.../zig/tests/*_test.zig` 一一对应，用例名称与行为与 Zig 保持一致。

执行计划文档中给出完整「Zig 源文件 ↔ Rust 模块」映射表、测试映射表、依赖顺序与阶段 A～D 步骤；收尾与文档（阶段 D）完成后，README 与本文档会注明对齐状态。运行 Rust 单元测试请使用：`cargo test --features test`（详见 `pytui/src/pytui/native/README.md`）。
