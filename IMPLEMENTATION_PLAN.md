# OpenTUI Python 实现计划 (方案 A)

> 基于 [opentui/PYTHON_IMPLEMENTATION_GUIDE.md](../opentui/PYTHON_IMPLEMENTATION_GUIDE.md) 方案 A 的详细实现计划，包含单元测试与集成测试。

**项目根目录**: `pytui/`

---

## 📋 目录

- [1. 方案概述](#1-方案概述)
- [2. 技术栈与依赖](#2-技术栈与依赖)
- [3. 目录结构](#3-目录结构)
- [4. 实现阶段与步骤](#4-实现阶段与步骤)
- [5. 单元测试计划](#5-单元测试计划)
- [6. 集成测试计划](#6-集成测试计划)
- [7. 测试运行与 CI](#7-测试运行与-ci)
- [8. 验收标准与里程碑](#8-验收标准与里程碑)
- [9. 后续阶段：缺失功能实现计划（与 OpenTUI 对齐）](#9-后续阶段缺失功能实现计划与-opentui-对齐)

---

## 1. 方案概述

采用 **方案 A：完整实现**，从零打造高性能 TUI 框架：

| 能力           | 实现方式                          |
|----------------|-----------------------------------|
| 高性能渲染     | Rust + PyO3 原生层 (Buffer/Cell)  |
| 布局系统       | Yoga Flexbox (yoga-layout)        |
| 终端 I/O       | prompt-toolkit / 自实现 ANSI      |
| 语法高亮       | tree-sitter + tree-sitter-languages |
| 事件系统       | pyee (EventEmitter)               |
| 声明式 API     | 自实现 Reconciler + Hooks         |
| 测试           | pytest + pytest-benchmark + pytest-cov |

**目标**：在 `pytui/` 下实现与指南一致的 `src/pytui` 包，并配套完整单元测试与集成测试。

---

## 2. 技术栈与依赖

### 2.1 生产依赖

```toml
dependencies = [
    "pyee>=11.0.0",
    "numpy>=1.24.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
yoga = ["yoga-layout>=1.0.0"]
syntax = ["tree-sitter>=0.20.0", "tree-sitter-languages>=1.10.0"]
full = ["yoga-layout>=1.0.0", "tree-sitter>=0.20.0", "tree-sitter-languages>=1.10.0"]
```

原生层：Rust + PyO3 + maturin 构建，可选依赖（无 Rust 时退化为纯 Python Buffer）。

### 2.2 开发/测试依赖

```toml
dev = [
    "pytest>=8.0.0",
    "pytest-benchmark>=4.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "maturin>=1.4.0",
]
```

---

## 3. 目录结构

```
pytui/
├── pyproject.toml
├── README.md
├── IMPLEMENTATION_PLAN.md          # 本文件
├── .gitignore
│
├── src/
│   └── pytui/
│       ├── __init__.py
│       ├── core/                   # 核心
│       │   ├── __init__.py
│       │   ├── renderer.py
│       │   ├── renderable.py
│       │   ├── buffer.py
│       │   ├── layout.py
│       │   ├── terminal.py
│       │   ├── events.py
│       │   ├── colors.py
│       │   ├── ansi.py
│       │   ├── keyboard.py
│       │   ├── mouse.py
│       │   └── console.py
│       ├── native/                 # Rust 扩展 (maturin)
│       │   ├── Cargo.toml
│       │   └── src/
│       │       └── lib.rs
│       ├── components/
│       │   ├── __init__.py
│       │   ├── text.py
│       │   ├── box.py
│       │   ├── input.py
│       │   ├── textarea.py
│       │   ├── select.py
│       │   ├── scrollbox.py
│       │   ├── code.py
│       │   └── diff.py
│       ├── syntax/
│       │   ├── __init__.py
│       │   ├── highlighter.py
│       │   └── themes.py
│       ├── react/
│       │   ├── __init__.py
│       │   ├── reconciler.py
│       │   ├── component.py
│       │   ├── hooks.py
│       │   └── jsx.py
│       └── utils/
│           ├── __init__.py
│           ├── diff.py
│           └── validation.py
│
├── examples/
│   ├── hello.py
│   ├── counter.py
│   ├── login_form.py
│   ├── code_editor.py
│   └── dashboard.py
│
├── tests/                          # 测试根目录
│   ├── conftest.py                 # 共享 fixtures
│   ├── unit/                       # 单元测试
│   │   ├── core/
│   │   │   ├── test_buffer.py
│   │   │   ├── test_cell.py
│   │   │   ├── test_ansi.py
│   │   │   ├── test_colors.py
│   │   │   ├── test_events.py
│   │   │   ├── test_keyboard.py
│   │   │   ├── test_layout.py
│   │   │   ├── test_renderable.py
│   │   │   └── test_renderer.py
│   │   ├── components/
│   │   │   ├── test_text.py
│   │   │   ├── test_box.py
│   │   │   ├── test_input.py
│   │   │   └── test_select.py
│   │   ├── syntax/
│   │   │   └── test_highlighter.py
│   │   ├── react/
│   │   │   ├── test_reconciler.py
│   │   │   ├── test_component.py
│   │   │   └── test_hooks.py
│   │   └── utils/
│   │       ├── test_diff.py
│   │       └── test_validation.py
│   ├── integration/                # 集成测试
│   │   ├── test_app_hello.py
│   │   ├── test_app_layout.py
│   │   ├── test_app_forms.py
│   │   └── test_react_flow.py
│   └── benchmarks/
│       ├── bench_buffer.py
│       └── bench_layout.py
│
└── docs/
    ├── getting-started.md
    ├── architecture.md
    └── api-reference.md
```

---

## 4. 实现阶段与步骤

### Phase 1: 原生层与基础核心 (1–2 周)

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 1.1 | 初始化 `pytui` 项目：pyproject.toml、src 布局、README | 可安装的包骨架 | - |
| 1.2 | Rust 子项目：`src/pytui/native`，Cargo.toml，PyO3 配置 | 可 `maturin develop` 的 native 包 | Rust, maturin |
| 1.3 | 实现 Rust：Cell、Buffer（set_cell/get_cell/draw_text/clear）、TextBuffer (Rope) | pytui_native 模块 | 1.2 |
| 1.4 | Python core/buffer.py：Cell  dataclass、OptimizedBuffer（native/fallback）、to_ansi | 缓冲区 Python API | 1.3 |
| 1.5 | core/ansi.py：ANSI 常量与 cursor_to/rgb_fg/rgb_bg/reset | ANSI 工具 | - |
| 1.6 | core/colors.py：parse_color（#rrggbb、透明） | 颜色解析 | - |
| 1.7 | 单元测试：test_cell、test_buffer、test_ansi、test_colors | 通过单元测试 | 1.4–1.6 |

**里程碑 1**：无布局、无渲染循环情况下，Buffer 可设置/读取 Cell、draw_text、clear，并输出 ANSI；单元测试全部通过。

---

### Phase 2: 布局与可渲染树 (2–3 周)

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 2.1 | core/layout.py：Yoga 封装，LayoutNode（flex/尺寸/边距/定位/子节点/calculate_layout/get_computed_layout） | 布局 API | yoga-layout |
| 2.2 | core/events.py：EventBus / EventEmitter 封装 | 事件 API | pyee |
| 2.3 | core/renderable.py：Renderable 基类（ctx、id、parent/children、layout_node、add/remove、request_render、calculate_layout、render/render_self） | 可渲染树 | 2.1, 2.2 |
| 2.4 | core/terminal.py：get_size、raw/alternate screen、cursor hide/show、mouse on/off | 终端控制 | - |
| 2.5 | core/keyboard.py：KeyboardHandler、keypress 事件（解析常见键） | 键盘输入 | 2.2 |
| 2.6 | core/renderer.py：RenderContext、RootRenderable、Renderer（双缓冲、start/stop、_render_frame、_diff_and_output、schedule_render） | 渲染器 | 1.4, 2.1–2.5 |
| 2.7 | 单元测试：test_layout、test_events、test_renderable、test_renderer（含 mock 终端/缓冲区） | 通过单元测试 | 2.1–2.6 |

**里程碑 2**：固定尺寸下可挂载 Renderable 树、计算布局、渲染到 Buffer 并输出 ANSI；单元测试通过。

---

### Phase 3: 基础组件与示例 (2–3 周)

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 3.1 | components/text.py：Text（content、fg/bg、样式、render_self） | Text 组件 | 2.3 |
| 3.2 | components/box.py：Box（border、border_style、title、背景、render_self） | Box 组件 | 2.3 |
| 3.3 | examples/hello.py：Box + Text，renderer.start() | Hello World | 2.6, 3.1, 3.2 |
| 3.4 | components/input.py：Input（单行、焦点、光标、render_self） | Input 组件 | 2.3, 2.5 |
| 3.5 | components/select.py：Select（选项列表、选中、render_self） | Select 组件 | 2.3, 2.5 |
| 3.6 | 单元测试：test_text、test_box、test_input、test_select（基于 mock buffer/ctx） | 通过单元测试 | 3.1–3.5 |
| 3.7 | 集成测试：test_app_hello（启动 renderer、挂载 Box+Text、渲染一帧、校验 buffer 内容） | 通过集成测试 | 3.3 |

**里程碑 3**：可运行 hello 与简单表单（Input/Select）；单元与集成测试通过。

---

### Phase 4: 高级组件与语法高亮 (2–3 周)

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 4.1 | components/textarea.py：多行文本、滚动 | Textarea | 2.3 |
| 4.2 | components/scrollbox.py：视口滚动 | Scrollbox | 2.3 |
| 4.3 | syntax/highlighter.py：Tree-sitter 集成、按 token 上色 | 语法高亮 | tree-sitter |
| 4.4 | syntax/themes.py：主题（颜色映射） | 主题 | core/colors |
| 4.5 | components/code.py：Code 组件（语法高亮 + 行号） | Code 组件 | 4.3, 4.4 |
| 4.6 | components/diff.py：Diff 视图（增删改行） | Diff 组件 | utils/diff |
| 4.7 | utils/diff.py：文本 diff 算法 | Diff 工具 | - |
| 4.8 | 单元测试：test_highlighter、test_code、test_diff、test_diff_util | 通过单元测试 | 4.1–4.7 |
| 4.9 | 集成测试：test_app_layout（多组件布局）、test_app_forms（表单交互） | 通过集成测试 | 3.x, 4.x |

**里程碑 4**：支持代码块与 diff 展示；布局与表单集成测试通过。

---

### Phase 5: 声明式 API (2–3 周)

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 5.1 | react/component.py：Component 基类、props、state、update() | 组件基类 | 2.3 |
| 5.2 | react/hooks.py：useState、useEffect（简易实现） | Hooks | 5.1 |
| 5.3 | react/jsx.py：create_element（h）、类型映射到 Renderable | JSX-like API | 5.1 |
| 5.4 | react/reconciler.py：树 diff、挂载/更新/卸载 | Reconciler | 2.3, 5.1–5.3 |
| 5.5 | examples/counter.py：声明式计数器 | 示例 | 5.1–5.4 |
| 5.6 | 单元测试：test_component、test_hooks、test_reconciler、test_jsx | 通过单元测试 | 5.1–5.4 |
| 5.7 | 集成测试：test_react_flow（挂载→更新→卸载） | 通过集成测试 | 5.5 |

**里程碑 5**：声明式组件可挂载、更新、卸载；相关单元与集成测试通过。

---

### Phase 6: 收尾与质量 (1–2 周)

| 步骤 | 内容 | 产出 |
|------|------|------|
| 6.1 | core/mouse.py、console.py（若在范围內） | 鼠标与控制台 |
| 6.2 | 基准测试：bench_buffer、bench_layout | 性能基线 |
| 6.3 | mypy 严格模式、ruff 规则、CI（pytest + cov + lint） | 质量门禁 |
| 6.4 | 文档：getting-started、architecture、api-reference | 可交付文档 |

---

## 5. 单元测试计划

### 5.1 原则

- 每个模块对应 `tests/unit/` 下同名包内的 `test_*.py`。
- 优先测公共 API 与边界条件；Rust 层通过 Python 封装测试。
- 使用 pytest fixtures（conftest.py）提供 mock 的 Terminal、Buffer、RenderContext。
- 不依赖真实终端：尺寸固定、不真正切换 raw/alternate screen。

### 5.2 各模块测试要点

#### core

| 文件 | 测试类/主题 | 用例要点 |
|------|-------------|----------|
| test_cell.py | TestCell | 默认值；to_native（有/无 native）；eq/hash 用于 diff |
| test_buffer.py | TestOptimizedBuffer | new/clear；set_cell/get_cell 越界；draw_text 换行与截断；fill_rect；to_ansi 含 ANSI 码；use_native=False 与 True（若可用） |
| test_ansi.py | TestANSI | cursor_to 格式；rgb_fg/rgb_bg；reset；常量存在 |
| test_colors.py | TestParseColor | #rrggbb、#rgb、transparent；非法输入 |
| test_events.py | TestEventBus | on/emit/once/off；参数传递；多监听器 |
| test_keyboard.py | TestKeyboardHandler | 单字符、转义序列、Ctrl 组合；keypress 事件 payload |
| test_layout.py | TestLayoutNode | flex 方向/对齐；宽高/边距；子节点顺序；calculate_layout 后 get_computed_layout 合理 |
| test_renderable.py | TestRenderable | add/remove/remove_all；request_render 冒泡；calculate_layout 递归；render 调用 render_self 与子节点顺序；find_by_id；focus/blur |
| test_renderer.py | TestRenderer | 构造；root 为 RootRenderable；schedule_render；_render_frame 清空 back_buffer、调用 root.render；_diff_and_output 不崩溃（mock stdout） |

#### components

| 文件 | 测试类/主题 | 用例要点 |
|------|-------------|----------|
| test_text.py | TestText | set_content 触发 request_render；render_self 多行与裁剪；样式应用 |
| test_box.py | TestBox | border on/off；border_style；title 居中；背景填充 |
| test_input.py | TestInput | 光标位置；输入字符/退格；focus 时边框或样式 |
| test_select.py | TestSelect | 选项列表；选中变更；键盘上下选择 |

#### syntax

| 文件 | 测试类/主题 | 用例要点 |
|------|-------------|----------|
| test_highlighter.py | TestHighlighter | 解析简单代码；返回 token 列表或带颜色的片段；未知语言降级 |

#### react

| 文件 | 测试类/主题 | 用例要点 |
|------|-------------|----------|
| test_component.py | TestComponent | props/state；update 触发重渲染 |
| test_hooks.py | TestHooks | useState 初始与更新；useEffect 执行时机（简化） |
| test_jsx.py | TestCreateElement | h('text', props, children)；类型映射正确 |
| test_reconciler.py | TestReconciler | 挂载新树；更新 props；卸载节点 |

#### utils

| 文件 | 测试类/主题 | 用例要点 |
|------|-------------|----------|
| test_diff.py | TestDiff | 相同/单行增删/多行变更；统一接口 |
| test_validation.py | TestValidation | 合法/非法参数；错误信息 |

### 5.3 conftest.py 建议

```python
# tests/conftest.py
import pytest

@pytest.fixture
def buffer_10x5():
    """10x5 缓冲区，用于渲染测试。"""
    from pytui.core.buffer import OptimizedBuffer
    return OptimizedBuffer(10, 5, use_native=False)

@pytest.fixture
def mock_context():
    """带 mock renderer 的 RenderContext。"""
    from pytui.core.renderer import RenderContext
    from unittest.mock import MagicMock
    renderer = MagicMock()
    renderer.width = 40
    renderer.height = 20
    return RenderContext(renderer=renderer)
```

---

## 6. 集成测试计划

### 6.1 原则

- 在 `tests/integration/` 下，不依赖真实 TTY；可替换 stdout 或使用内存 Buffer 校验。
- 单次运行时间可控（如不长时间阻塞主循环）。
- 覆盖：启动→挂载→渲染→输出 或 声明式更新流程。

### 6.2 用例

| 文件 | 场景 | 步骤 | 校验 |
|------|------|------|------|
| test_app_hello.py | Hello World | 创建 Renderer(40, 20)，root.add(Box).add(Text)，执行一帧 _render_frame | back_buffer 中包含预期字符串/ANSI |
| test_app_layout.py | 布局 | 多子节点不同 flex；calculate_layout；render | 各子节点 x/y/width/height 符合预期 |
| test_app_forms.py | 表单 | 挂载 Input + Select；模拟 keypress；再渲染 | 输入内容与选中项一致 |
| test_react_flow.py | 声明式 | 挂载 Counter；调用 update；再渲染 | buffer 中计数递增 |

### 6.3 集成测试示例骨架

```python
# tests/integration/test_app_hello.py
import pytest
from pytui.core import Renderer
from pytui.core.buffer import OptimizedBuffer
from pytui.components import Box, Text

def test_hello_renders_text():
    r = Renderer(width=40, height=10, target_fps=0)
    box = Box(r.context, {"width": 40, "height": 10, "border": True})
    text = Text(r.context, {"content": "Hello"})
    box.add(text)
    r.root.add(box)
    r._render_frame()
    # 校验 back_buffer 中 (2, 2) 附近为 "Hello" 或对应 ANSI
    buf = r.back_buffer
    found = False
    for y in range(10):
        for x in range(40):
            c = buf.get_cell(x, y)
            if c and "H" in (c.char or ""):
                found = True
                break
        if found:
            break
    assert found
```

---

## 7. 测试运行与 CI

### 7.1 本地命令

```bash
# 全部测试
pytest tests/ -v

# 仅单元测试
pytest tests/unit/ -v

# 仅集成测试
pytest tests/integration/ -v

# 覆盖率
pytest tests/ --cov=src/pytui --cov-report=term-missing --cov-report=html

# 基准测试（不参与 CI 失败判定时）
pytest tests/benchmarks/ --benchmark-only
```

### 7.2 建议 CI 步骤

1. 检出代码，安装 Python 3.11+ 与 Rust 工具链。
2. `pip install -e ".[dev,full]"` 或 `maturin develop`（若含 native）。
3. `ruff check src/ && ruff format --check src/`。
4. `mypy src/`（若已配置）。
5. `pytest tests/unit/ tests/integration/ -v --cov=src/pytui --cov-fail-under=70`（阈值可调）。

---

## 8. 验收标准与里程碑

| 里程碑 | 验收标准 |
|--------|----------|
| M1 | Buffer/Cell/ANSI/colors 单元测试通过；可生成 ANSI 字符串 |
| M2 | Layout + Renderable + Renderer 单元测试通过；固定尺寸下可渲染一帧 |
| M3 | Text/Box/Input/Select 单元测试通过；hello 集成测试通过；examples/hello.py 可运行 |
| M4 | Code/Diff/高亮与布局、表单集成测试通过 |
| M5 | React 单元与 test_react_flow 集成测试通过；examples/counter.py 可运行 |
| M6 | 基准测试可运行；mypy/ruff 通过；文档可读 |

本计划与 [opentui/PYTHON_IMPLEMENTATION_GUIDE.md](../opentui/PYTHON_IMPLEMENTATION_GUIDE.md) 方案 A 对齐，实现时以该指南中的代码示例为参考，并在 `pytui` 目录下按上述阶段与测试计划推进。

---

## 9. 后续阶段：缺失功能实现计划（与 OpenTUI 对齐）

> 依据 [docs/opentui-pytui-comparison.md](docs/opentui-pytui-comparison.md) 中“缺失或明显弱化”项整理，按优先级与依赖关系分阶段推进。各阶段可独立排期（建议每阶段 1–3 周）。

### Phase 7: 补充组件与输入体验 (2–3 周) ✅ 已完成（7.1–7.6）

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 7.1 | components/tab_select.py：TabSelect（多 tab 切换、选中事件） | TabSelect 组件 | 2.3, 3.x |
| 7.2 | components/slider.py：Slider（数值滑块、min/max/step、事件） | Slider 组件 | 2.3 |
| 7.3 | components/scrollbar.py：独立 ScrollBar（与 Scrollbox 可组合） | ScrollBar 组件 | 2.3, Scrollbox |
| 7.4 | components/line_number.py：LineNumberRenderable（行号 + 内容区，可配宽） | LineNumber 组件 | 2.3 |
| 7.5 | react/reconciler TYPE_MAP 注册 TabSelect、Slider、ScrollBar、LineNumber | 声明式可用 | 7.1–7.4 |
| 7.6 | 单元测试：test_tab_select、test_slider、test_scrollbar、test_line_number | 通过单元测试 | 7.1–7.4 |
| 7.7 | 可选：core/keyboard Kitty 协议扩展（解析 Kitty 键盘序列） | 更好终端兼容 | 2.5 |
| 7.8 | 可选：utils/scroll_acceleration.py（滚动加速度曲线） | 滚动体验 | Scrollbox |

**7.7 已完成**：keyboard.py 支持 CSI number;modifier u（Kitty）、CSI 1;mod Letter（带修饰键的 legacy）；单元测试 test_kitty_csi_u_*、test_legacy_csi_with_modifier。  
**7.8 已完成**：utils/scroll_acceleration.py 提供 LinearScrollAccel、MacOSScrollAccel；Scrollbox 支持 scroll_acceleration 选项；单元测试 test_scroll_acceleration、test_scrollbox。

**里程碑 7**：TabSelect、Slider、ScrollBar、LineNumber 可用；声明式与命令式示例可运行；Kitty 键盘解析与滚动加速度可用。

---

### Phase 8: 声明式增强与 Console Overlay (2–3 周) ✅ 已完成（8.1–8.6）

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 8.1 | react/hooks.py：useKeyboard(ctx)、useResize(ctx)、useRenderer(ctx) | 常用 hooks | 5.1, 5.2 |
| 8.2 | react/reconciler 或 host 层：支持 props 中 onInput/onChange/onSelect 等，挂载时绑定到对应 Renderable 事件 | 声明式 onXxx | 5.4, Input/Select |
| 8.3 | react/hooks.py：useTimeline 或简易 useAnimation（与 core 动画解耦或占位） | 动画 hook（可选） | 5.2 |
| 8.4 | core/console.py：Console overlay（捕获 sys.stdout/sys.stderr 或 logging，可定位 BOTTOM/TOP、大小比例、滚动、颜色） | Console overlay | 2.4, 6.1 |
| 8.5 | 文档与示例：声明式 onXxx、useKeyboard、Console overlay 用法 | 可交付文档 | 8.1–8.4 |
| 8.6 | 单元测试：test_hooks 扩展（useKeyboard/useResize）；集成测试：Console overlay 输出校验 | 通过测试 | 8.1, 8.4 |

**8.1 已完成**：hooks.py 提供 useRenderer(ctx)、useResize(ctx)、useKeyboard(ctx)；test_hooks 含 test_useResize_returns_size_and_updates_on_resize_event。  
**8.3 已完成**：hooks.py 提供 useTimeline(ctx) -> { elapsed, pause, resume }；每帧由 renderer.events.emit("frame", time) 驱动；与 core 动画解耦；test_hooks 含 test_useTimeline_returns_elapsed_and_updates_on_frame_event。  
**8.2 已完成**：reconciler 中 onInput/onChange/onSelect/onSelectionChanged/onScroll 挂载时绑定到对应 Renderable 事件；Input/Select 发出 input/change、select。  
**8.4 已完成**：core/console.py 提供 ConsoleBuffer、ConsoleOverlay（position top/bottom、滚动）、capture_stdout；Console 便捷类。  
**8.5–8.6 已完成**：test_hooks 扩展 useResize；tests/unit/core/test_console.py（ConsoleBuffer、ConsoleOverlay、capture_stdout）；tests/integration/test_console_overlay.py。

**里程碑 8**：声明式 onXxx 与常用 hooks 可用；Console overlay 可捕获输出并展示。

---

### Phase 9: 编辑器基础、动画与 Buffer 增强 (2–3 周) ✅ 已完成（9.1–9.7）

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 9.1 | core/edit_buffer.py：EditBuffer（基于 TextBuffer/Rope 的编辑缓冲、insert/delete/undo 等） | EditBuffer | 1.3, native |
| 9.2 | core/editor_view.py 或 components/editor_view.py：EditorView（视口与 EditBuffer 绑定、光标、选区） | EditorView | 9.1, 2.3 |
| 9.3 | components/textarea.py：可选接入 EditBuffer/EditorView，支持选区与 undo | Textarea 增强 | 9.1, 9.2 |
| 9.4 | core/animation.py：Timeline（简易时间轴、tick、回调或驱动 state） | 动画基础 | 2.2 |
| 9.5 | core/buffer.py 或 native：alpha 混合（set_cell_with_alpha / blend） | Buffer alpha | 1.4 |
| 9.6 | 可选：FrameBuffer 作为 Renderable（全屏画布节点） | FrameBuffer 节点 | 2.3, 9.5 |
| 9.7 | 可选：post/filters.py（后处理滤镜，如 dim、blur 占位） | 后处理扩展点 | 2.6 |

**9.1 已完成**：core/edit_buffer.py 提供 EditBuffer（纯 Python，与 Rope 解耦）：insert(pos, text)、delete(start, end)、undo()、redo()、get_lines()、pos_to_line_col/line_col_to_pos、set_text；tests/unit/core/test_edit_buffer.py。  
**9.2 已完成**：core/editor_view.py 提供 EditorView（视口、cursor_pos/scroll_y/selection、get_visible_lines、insert/delete_backward/delete_forward、undo/redo）；tests/unit/core/test_editor_view.py。  
**9.3 已完成**：components/textarea.py 支持 buffer / editor_view 选项，渲染时同步 editor_view 视口尺寸，绘制光标与选区，undo/redo 委托；tests/unit/components/test_textarea.py 含 buffer/editor_view 用例。  
**9.4 已完成**：core/animation.py 提供 Timeline（start/stop/pause/resume、elapsed、on_tick/remove_tick、tick）；tests/unit/core/test_animation.py。  
**9.5 已完成**：core/buffer.py 提供 blend_color、set_cell_with_alpha；tests/unit/core/test_buffer.py 含 test_blend_color、test_set_cell_with_alpha_blends。  
**9.6 已完成**：components/frame_buffer.py 提供 FrameBuffer（get_buffer、render_self 时 blit 到父 buffer）；reconciler TYPE_MAP 注册 frame_buffer；tests/unit/components/test_frame_buffer.py。  
**9.7 已完成**：post/filters.py 提供 apply_dim、apply_blur_placeholder；tests/unit/post/test_filters.py。

**里程碑 9**：EditBuffer/EditorView 可用；Timeline 可用；Buffer 支持 alpha；FrameBuffer 节点与 post 滤镜占位已实现。

---

### Phase 10: 富文本、语法与测试增强 (2–3 周) ✅ 已完成（10.1–10.8）

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 10.1 | components/text_node.py：TextNode、Span（内联富文本）、Bold/Italic/Underline/LineBreak、可选 Link | 富文本内联 | 2.3, Text |
| 10.2 | syntax/tree_sitter 或 syntax/languages：预编译语言包集成（如 py-tree-sitter 语言包）、highlighter 多语言 | Tree-sitter 多语言 | 4.3, 可选依赖 |
| 10.3 | syntax/style.py：SyntaxStyle / convertThemeToStyles（更完整主题→样式映射） | 主题体系增强 | 4.4 |
| 10.4 | core/rgba.py：RGBA 类（from_hex/from_ints/from_values），colors 层可选用 | RGBA 统一表示 | 1.6 |
| 10.5 | testing/test_renderer.py：create_test_renderer(width, height, …)，无 TTY、可注入输入 | TestRenderer | 2.6 |
| 10.6 | testing/mock_keys.py、mock_mouse.py：create_mock_keys(renderer)、create_mock_mouse(renderer) | Mock 输入 | 2.5, 2.6 |
| 10.7 | 快照测试：pytest 快照插件或自写 buffer 快照，对关键组件做 layout/render 快照 | Snapshot 能力 | 10.5 |
| 10.8 | 单元/集成测试扩展：TestRenderer + Mock 输入用例 | 通过测试 | 10.5, 10.6 |

**10.1 已完成**：components/text_node.py 提供 TextNode、Span、bold/italic/underline/line_break/link；reconciler TYPE_MAP 注册 text_node；tests/unit/components/test_text_node.py。  
**10.2 已完成**：syntax/languages.py 提供 get_language、get_parser（可选 tree_sitter_languages）。  
**10.3 已完成**：syntax/style.py 提供 SyntaxStyle、convert_theme_to_styles、get_default_styles；tests/unit/syntax/test_style.py。  
**10.4 已完成**：core/rgba.py 提供 RGBA（from_hex/from_ints/from_values、to_tuple）；tests/unit/core/test_rgba.py。  
**10.5 已完成**：pytui/testing/test_renderer.py 提供 MockTerminal、create_test_renderer；Renderer 支持 terminal= 与 render_once()；tests/unit/testing/test_renderer.py。  
**10.6 已完成**：pytui/testing/mock_keys.py、mock_mouse.py 提供 create_mock_keys、create_mock_mouse；tests/unit/testing/test_mock_keys.py。  
**10.7 已完成**：pytui/testing/snapshot.py 提供 buffer_snapshot_lines、assert_buffer_snapshot；tests/unit/testing/test_snapshot.py。  
**10.8 已完成**：tests/integration/test_test_renderer_snapshot.py（TestRenderer + Mock + 快照）。

**里程碑 10**：富文本内联可用；Tree-sitter 多语言占位与主题样式增强；RGBA 与测试设施（TestRenderer、Mock、快照）就绪。

---

### Phase 11: 可选增强（低优先级） ✅ 已完成（11.1–11.5）

| 步骤 | 内容 | 产出 | 依赖 |
|------|------|------|------|
| 11.1 | components/ascii_font.py：ASCIIFont（艺术字、可选多套字体 JSON） | ASCIIFont 组件 | 2.3 |
| 11.2 | utils/extmarks.py：extmarks（行内标记/装饰，用于高亮、诊断等） | extmarks 扩展点 | 2.3 |
| 11.3 | core/terminal_palette.py 或 lib/terminal-palette：终端调色板检测与映射 | 终端调色板 | 2.4 |
| 11.4 | utils/data_paths.py：数据目录/缓存路径（tree-sitter 资源、字体等） | 数据路径 | 4.3, 11.1 |
| 11.5 | 可选：Solid 风格 reconciler（细粒度响应式，单独包或子模块） | 第二套声明式 API | 5.x |

**11.1 已完成**：components/ascii_font.py 提供 ASCIIFont、TINY_FONT、measure_text、render_font_to_buffer、load_font_from_json、register_font；reconciler TYPE_MAP 注册 ascii_font；tests/unit/components/test_ascii_font.py。  
**11.2 已完成**：utils/extmarks.py 提供 Extmark、ExtmarksStore（add/remove/get_in_range/clear）；tests/unit/utils/test_extmarks.py。  
**11.3 已完成**：core/terminal_palette.py 提供 detect_capability、get_palette_color（256 调色板）；tests/unit/core/test_terminal_palette.py。  
**11.4 已完成**：utils/data_paths.py 提供 get_data_dir、get_cache_dir、ensure_data_dir、ensure_cache_dir；tests/unit/utils/test_data_paths.py。  
**11.5 已完成**：react/solid_placeholder.py 占位（Solid 风格 reconciler 为未来扩展点）。

**里程碑 11**：可选组件与工具补齐；与 OpenTUI 能力对齐度更高。

---

### 后续阶段汇总表

| 阶段 | 主题 | 建议周期 | 优先级 |
|------|------|----------|--------|
| Phase 7 | 补充组件（TabSelect、Slider、ScrollBar、LineNumber）、输入体验（Kitty、滚动加速） | 2–3 周 | 高 |
| Phase 8 | 声明式增强（hooks、onXxx）、Console overlay | 2–3 周 | 高 |
| Phase 9 | 编辑器基础（EditBuffer、EditorView）、动画（Timeline）、Buffer alpha、post | 2–3 周 | 中 |
| Phase 10 | 富文本、语法/主题增强、RGBA、TestRenderer/Mock/Snapshot | 2–3 周 | 中 |
| Phase 11 | ASCIIFont、extmarks、terminal-palette、data-paths、Solid reconciler（可选） | 按需 | 低 |

详细缺失项与对照见 [docs/opentui-pytui-comparison.md](docs/opentui-pytui-comparison.md)。  
**缺失能力与实现步骤**（组件细节、Textarea/编辑器、语法、声明式、ASCIIFont 等）见 [opentui-pytui-comparison.md 第 10 节](docs/opentui-pytui-comparison.md#10-缺失能力与实现步骤)，可作为 Phase 12 及以后的候选步骤插入本计划表。

---

## 附录：已创建的测试文件

实现计划落地时，已预先创建以下测试骨架（需在实现对应模块后逐步通过）：

| 路径 | 说明 |
|------|------|
| `tests/conftest.py` | 共享 fixtures：buffer_10x5、buffer_40x20、mock_renderer、mock_context |
| `tests/unit/core/test_cell.py` | Cell 默认值、to_native、相等性 |
| `tests/unit/core/test_buffer.py` | OptimizedBuffer 创建、set/get_cell、draw_text、fill_rect、to_ansi |
| `tests/unit/core/test_ansi.py` | ANSI.cursor_to、rgb_fg/rgb_bg、reset、常量 |
| `tests/integration/test_app_hello.py` | Hello 场景：Box+Text 挂载、一帧渲染、buffer 内容校验 |
| `tests/unit/core/test_console.py` | ConsoleBuffer、ConsoleOverlay、capture_stdout 单元测试 |
| `tests/integration/test_console_overlay.py` | Console Overlay 集成：挂载 overlay+buffer、渲染、校验内容 |

**运行测试**（需先实现并安装包）：

```bash
cd pytui
pip install -e ".[dev]"
pytest tests/ -v
# 仅单元测试
pytest tests/unit/ -v
# 仅集成测试
pytest tests/integration/ -v
# 覆盖率
pytest tests/ --cov=src/pytui --cov-report=term-missing
```

未实现 `pytui` 包时，测试会因 `pytest.importorskip("pytui...")` 而 skip，不会报错。
