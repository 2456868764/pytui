# PyTUI Examples 实现计划

目标：在 `pytui/src/pytui/examples` 下实现与 `opentui/packages/core/src/examples` 对应的**所有可在纯 TUI 环境实现**的 example 功能，并明确不可移植项的处置方式。

---

## 一、OpenTUI Examples 清单与分类

### 1.1 纯 TUI 类（在 PyTUI 中完整实现）

| # | OpenTUI 文件 | 名称 | 功能简述 | PyTUI 依赖组件 |
|---|--------------|------|----------|----------------|
| 1 | `simple-layout-example.ts` | Layout System Demo | Flex 布局：水平/垂直/居中/三列，可切换 | Box, Text, layout |
| 2 | `input-demo.ts` | Input Demo | 多输入框、Tab 切换、校验、提交 | Input, Box, Text |
| 3 | `input-select-layout-demo.ts` | Input & Select Layout Demo | 输入+选择组合布局 | Input, Select, Box, Text |
| 4 | `select-demo.ts` | Select Demo | 下拉选择、导航、描述、滚动指示 | Select, Box, Text |
| 5 | `tab-select-demo.ts` | Tab Select | 标签选择、左右切换、下划线/描述 | TabSelect, Box, Text |
| 6 | `slider-demo.ts` | Slider Demo | 水平/垂直滑块、动画滑块、数值显示 | Slider, Box, Text |
| 7 | `styled-text-demo.ts` | Styled Text Demo | 模板字面量、颜色、粗体等样式 | Text (styled), t/fg/bold 等 |
| 8 | `text-node-demo.ts` | TextNode Demo | TextNode API、复杂样式结构 | TextNode, Box, Text |
| 9 | `text-wrap.ts` | Text Wrap Demo | 自动换行、可调大小、文件路径输入 | Text, ScrollBox, Input, Box |
| 10 | `link-demo.ts` | Link Demo | OSC 8 超链接、可点击链接 | Text (link span), 终端 OSC 8 |
| 11 | `extmarks-demo.ts` | Extmarks Demo | 虚拟 extmarks、光标跳过范围 | EditBuffer/Textarea + extmarks |
| 12 | `opacity-example.ts` | Opacity Demo | 盒子透明度、动画过渡 | Box (alpha), 动画/时间线 |
| 13 | `code-demo.ts` | Code Demo | 代码查看、行号、语法高亮、诊断 | Code, LineNumber, ScrollBox, Box, Text |
| 14 | `diff-demo.ts` | Diff Demo | 统一/分屏 diff、语法高亮、多主题 | Diff, Box, Text |
| 15 | `hast-syntax-highlighting-demo.ts` | HAST Syntax Highlighting | HAST 树转高亮文本块 | 高亮 chunk 生成（可简化） |
| 16 | `editor-demo.ts` | Editor Demo | 完整文本编辑（TextareaRenderable） | Textarea, Box, Text |
| 17 | `console-demo.ts` | Console Demo | 交互式日志、可点击按钮 | Box, Text, 事件/焦点 |
| 18 | `mouse-interaction-demo.ts` | Mouse Interaction Demo | 鼠标轨迹、可点击格子 | Box, Text, Mouse 事件 |
| 19 | `text-selection-demo.ts` | Text Selection Demo | 多 Renderable 文本选择、拖拽 | Text/Textarea, selection API |
| 20 | `ascii-font-selection-demo.ts` | ASCII Font Selection Demo | ASCII 字体下的字符级选择 | ASCIIFont, selection |
| 21 | `scroll-example.ts` | ScrollBox Demo | 可滚动容器、Box/ASCIIFont 子项 | ScrollBox, Box, ASCIIFont, Text |
| 22 | `sticky-scroll-example.ts` | Sticky Scroll Demo | 内容变化时保持边界位置 | ScrollBox 行为 |
| 23 | `nested-zindex-demo.ts` | Nested Z-Index Demo | 嵌套 z-index 行为 | Box, Text, zIndex |
| 24 | `relative-positioning-demo.ts` | Relative Positioning Demo | 子相对父的定位 | Box, 布局/定位 |
| 25 | `transparency-demo.ts` | Transparency Demo | 透明与 Alpha 混合 | Box (alpha), RGBA |
| 26 | `vnode-composition-demo.ts` | VNode Composition Demo | Box(Box(Box(children))) 声明式组合 | Box, Text, Generic/VNode（或 React 等价） |
| 27 | `full-unicode-demo.ts` | Full Unicode Demo | 复杂字形、可拖拽盒子 | Box, Text, 鼠标拖拽 |
| 28 | `live-state-demo.ts` | Live State Management Demo | 自动渲染生命周期、动态挂载 | Renderer, 动态 add/remove |
| 29 | `opentui-demo.ts` | OpenTUI Demo | 多 Tab 综合演示 | 多种组件组合 |
| 30 | `fonts.ts` (boxExample) | ASCII Font Demo | 多种 ASCII 字体、颜色 | ASCIIFont, Box |
| 31 | `terminal.ts` | Terminal Palette Demo | 256 色检测与展示 | TerminalPalette, Box/Text |
| 32 | `keypress-debug-demo.ts` | Keypress Debug Tool | 按键事件、原始输入、能力检测 | Keyboard, Text, 调试输出 |
| 33 | `split-mode-demo.ts` | Split Mode Demo (Experimental) | 渲染器仅占底部、上方正常终端输出 | Renderer 区域/alternate buffer |
| 34 | `timeline-example.ts` | Timeline Example | 时间线动画、同步子时间线 | Timeline, Box, Text |

### 1.2 GPU/WebGL/物理引擎类（不移植，仅占位说明）

以下依赖 WebGL/Three.js/物理引擎或原生二进制，在 PyTUI 中**不实现**，仅在示例菜单或文档中标注「N/A (GPU/Physics)」：

| # | OpenTUI 文件 | 名称 | 原因 |
|---|--------------|------|------|
| 35 | `golden-star-demo.ts` | Golden Star Demo | Three.js 3D + 粒子 |
| 36 | `fractal-shader-demo.ts` | Fractal Shader | GPU Shader |
| 37 | `shader-cube-demo.ts` | Shader Cube | 3D + 自定义 Shader |
| 38 | `lights-phong-demo.ts` | Phong Lighting | 3D 光照 |
| 39 | `physx-planck-2d-demo.ts` | Physics Planck | 2D 物理引擎 Planck |
| 40 | `physx-rapier-2d-demo.ts` | Physics Rapier | 2D 物理引擎 Rapier |
| 41 | `static-sprite-demo.ts` | Static Sprite | 纹理/GPU 渲染 |
| 42 | `sprite-animation-demo.ts` | Sprite Animation | 精灵动画/GPU |
| 43 | `sprite-particle-generator-demo.ts` | Sprite Particles | 粒子系统/GPU |
| 44 | `framebuffer-demo.ts` | Framebuffer Demo | GPU Framebuffer |
| 45 | `texture-loading-demo.ts` | Texture Loading | 纹理加载/GPU |

---

## 二、执行阶段与步骤

### 阶段 0：基础设施（优先完成）

| 步骤 | 内容 | 产出 |
|------|------|------|
| 0.1 | 创建 `pytui/src/pytui/examples/` 目录结构 | `examples/__init__.py`、`lib/` |
| 0.2 | 实现 `lib/standalone_keys.py` | 与 OpenTUI `standalone-keys.ts` 等价：` 切换 console、. 调试、Ctrl+G 等 |
| 0.3 | 实现统一入口 `run_example(name: str)` 或按名启动单例 | 供下面各 demo 复用 renderer 与退出逻辑 |
| 0.4 | 实现示例选择器（菜单） | Box + Text + Select/列表，筛选、Enter 运行、Esc 返回、Ctrl+C 退出 |

### 阶段 1：布局与基础控件（1–7）

| 步骤 | 对应 OpenTUI | 内容 | 产出文件 |
|------|--------------|------|----------|
| 1.1 | simple-layout-example | 水平/垂直/居中/三列布局切换 | `simple_layout_example.py` |
| 1.2 | input-demo | 多 Input、Tab、校验、提交、状态显示 | `input_demo.py` |
| 1.3 | input-select-layout-demo | Input + Select 同屏布局 | `input_select_layout_demo.py` |
| 1.4 | select-demo | Select 列表、键盘导航、选项描述 | `select_demo.py` |
| 1.5 | tab-select-demo | TabSelect 标签栏、左右键、选项 | `tab_select_demo.py` |
| 1.6 | slider-demo | 水平/垂直 Slider、数值显示、可选动画滑块 | `slider_demo.py` |
| 1.7 | styled-text-demo | 样式文本（颜色、粗体等） | `styled_text_demo.py` |

### 阶段 2：文本与高亮（8–16）

| 步骤 | 对应 OpenTUI | 内容 | 产出文件 |
|------|--------------|------|----------|
| 2.1 | text-node-demo | TextNode 复杂样式结构 | `text_node_demo.py` |
| 2.2 | text-wrap | 换行、可调大小、文件路径输入（可选读文件） | `text_wrap.py` |
| 2.3 | link-demo | OSC 8 链接（终端支持时）或占位说明 | `link_demo.py` |
| 2.4 | extmarks-demo | 虚拟 extmarks、光标跳过 | `extmarks_demo.py` |
| 2.5 | opacity-example | Box 透明度 + 简单动画 | `opacity_example.py` |
| 2.6 | code-demo | Code + LineNumber + ScrollBox、多语言/主题切换 | `code_demo.py` |
| 2.7 | diff-demo | Diff 统一/分屏、语法高亮 | `diff_demo.py` |
| 2.8 | hast-syntax-highlighting-demo | HAST→高亮块（可简化为 Code 高亮展示） | `hast_syntax_highlighting_demo.py` |
| 2.9 | editor-demo | Textarea 全功能编辑 | `editor_demo.py` |

### 阶段 3：交互与滚动（17–25）

| 步骤 | 对应 OpenTUI | 内容 | 产出文件 |
|------|--------------|------|----------|
| 3.1 | console-demo | 日志级别按钮、输出区 | `console_demo.py` |
| 3.2 | mouse-interaction-demo | 鼠标移动/点击、格子高亮 | `mouse_interaction_demo.py` |
| 3.3 | text-selection-demo | 跨组件文本选择、拖拽 | `text_selection_demo.py` |
| 3.4 | ascii-font-selection-demo | ASCIIFont + 选择 | `ascii_font_selection_demo.py` |
| 3.5 | scroll-example | ScrollBox + 多种子项（Box/ASCIIFont） | `scroll_example.py` |
| 3.6 | sticky-scroll-example | Sticky 滚动行为 | `sticky_scroll_example.py` |
| 3.7 | nested-zindex-demo | 嵌套 z-index | `nested_zindex_demo.py` |
| 3.8 | relative-positioning-demo | 相对定位 | `relative_positioning_demo.py` |
| 3.9 | transparency-demo | 透明与混合 | `transparency_demo.py` |

### 阶段 4：组合与系统（26–34）

| 步骤 | 对应 OpenTUI | 内容 | 产出文件 |
|------|--------------|------|----------|
| 4.1 | vnode-composition-demo | Box 嵌套 + 简单按钮（或 React 等价） | `vnode_composition_demo.py` |
| 4.2 | full-unicode-demo | 复杂 Unicode、可拖拽 Box | `full_unicode_demo.py` |
| 4.3 | live-state-demo | 动态挂载/卸载、生命周期 | `live_state_demo.py` |
| 4.4 | opentui-demo | 多 Tab 综合 | `opentui_demo.py` |
| 4.5 | fonts.ts | ASCII Font 多字体多颜色 | `ascii_font_demo.py`（或 `fonts.py`） |
| 4.6 | terminal.ts | 256 色调色板检测与展示 | `terminal_palette_demo.py` |
| 4.7 | keypress-debug-demo | 按键调试工具 | `keypress_debug_demo.py` |
| 4.8 | split-mode-demo | 仅底部区域渲染（若 renderer 支持） | `split_mode_demo.py` |
| 4.9 | timeline-example | Timeline 动画、多时间线 | `timeline_example.py` |

### 阶段 5：入口与文档

| 步骤 | 内容 | 产出 |
|------|------|------|
| 5.1 | 示例注册表 | `examples/registry.py`：name → (run, destroy, description)，含 GPU 项占位 |
| 5.2 | 主入口脚本 | `examples/__main__.py` 或 `run_examples.py`：启动选择器或 `python -m pytui.examples <name>` |
| 5.3 | README | `examples/README.md`：如何运行、列表、与 OpenTUI 对照表 |
| 5.4 | 本计划文档 | 保持 `docs/examples-implementation-plan.md` 与实现进度同步（可选勾选表） |

---

## 三、技术约定

- **Renderer**：每个 demo 使用统一 `create_renderer()`（或从选择器传入），退出时调用 `destroy()`。
- **按键**：Esc 返回菜单（若在子 demo）、Ctrl+C 退出；与 OpenTUI 一致的调试键在 `standalone_keys` 中集中处理。
- **命名**：文件名 `snake_case`，与 OpenTUI 文件名一一对应（见上表）。
- **不可移植项**：GPU/Physics 的 11 个 example 在注册表中列为「N/A」，运行时显示简短说明或跳转文档。

---

## 四、依赖关系简图

```
standalone_keys.py
       ↓
registry.py → 各 demo 的 run()/destroy()
       ↓
index/选择器 (Box + Select + Textarea filter)
       ↓
┌──────┴──────┐
│ 各 demo     │ 依赖：Box, Text, Input, Select, TabSelect, Slider,
│ 单文件      │       Code, Diff, Textarea, ScrollBox, ASCIIFont,
│ run/destroy │       LineNumber, TextNode, Timeline, TerminalPalette, …
└─────────────┘
```

---

## 五、验收标准

- 所有「纯 TUI 类」34 个 example 在 `pytui/src/pytui/examples` 下有对应实现或明确占位（如 link/HAST 简化）。
- 通过统一入口可列出并运行任意已实现 demo，Esc 返回菜单，Ctrl+C 退出。
- GPU/Physics 的 11 项在列表中可见且标注为不可用，不报错。
- 本计划文档中的步骤与阶段可作为任务拆分与进度跟踪依据。

---

## 六、当前进度

- [x] **阶段 0**：目录结构（0.1）、`lib/standalone_keys.py`（0.2）、统一入口 `__main__.py`（0.3）、示例选择器 `selector_demo.py`（0.4）
- [x] **阶段 1.1**：`simple_layout_example.py`（水平/垂直/居中/三列，Space 切换，R 重置，P 自动播放标签）
- [x] **阶段 1.2**：`input_demo.py`（多 Input、Tab 切换、校验、Enter 提交、状态显示）
- [x] **阶段 1.3**：`input_select_layout_demo.py`（Input + 双 Select 同屏，Tab 切换焦点）
- [x] **阶段 1.4**：`select_demo.py`（Select 列表、F/D/S/W 切换描述/滚动/换行、状态区）
- [x] **阶段 5**：注册表（5.1）、主入口（5.2）、README（5.3）；本计划文档（5.4）
- [ ] 阶段 1.5–1.7、2、3、4：其余 demo 待按步骤实现

**运行**：`python -m pytui.examples`（选择器）或 `python -m pytui.examples <name>`（如 `simple-layout`、`input-demo`、`input-select-layout`、`select-demo`）。

---

## 七、步骤摘要（快速查阅）

| 阶段 | 步骤数 | 内容 |
|------|--------|------|
| 0 | 4 | 建目录、standalone_keys、统一入口、示例选择器 |
| 1 | 7 | simple-layout, input, input-select-layout, select, tab-select, slider, styled-text |
| 2 | 9 | text-node, text-wrap, link, extmarks, opacity, code, diff, hast, editor |
| 3 | 9 | console, mouse, text-selection, ascii-font-selection, scroll, sticky-scroll, nested-zindex, relative-positioning, transparency |
| 4 | 9 | vnode-composition, full-unicode, live-state, opentui-demo, ascii-font-demo, terminal-palette, keypress-debug, split-mode, timeline |
| 5 | 4 | 注册表完善、主入口、README、计划文档同步 |

**合计**：约 34 个 TUI 可实现 example + 11 个 GPU/Physics 占位 + 5 个阶段 42 个步骤。

（当前进度见「六、当前进度」。）
