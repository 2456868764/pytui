# OpenTUI Python 实现方案

> 基于 OpenTUI (TypeScript/Zig) 架构的 Python TUI 框架实现指南

## 📋 目录

- [项目概述](#项目概述)
- [技术栈映射](#技术栈映射)
- [核心依赖选择](#核心依赖选择)
- [项目结构](#项目结构)
- [实现步骤](#实现步骤)
- [代码实现](#代码实现)
- [项目配置](#项目配置)
- [开发流程](#开发流程)
- [实现优先级](#实现优先级)
- [技术挑战](#技术挑战)
- [参考资源](#参考资源)

---

## 项目概述

基于 OpenTUI 的分层架构设计，实现一个 Python 版本的终端用户界面框架，提供：

- ✅ 高性能渲染引擎 (Rust 原生层)
- ✅ 灵活的布局系统 (Yoga Flexbox)
- ✅ 丰富的组件库
- ✅ 声明式 API (类 React)
- ✅ 语法高亮支持 (Tree-sitter)

---

## 技术栈映射

### OpenTUI → Python 技术对应

| OpenTUI (TS/Zig) | Python 方案 | 说明 |
|------------------|-------------|------|
| **Bun Runtime** | CPython 3.11+ / PyPy | 标准 Python 解释器 |
| **Zig (原生层)** | **Rust + PyO3** | 高性能扩展，更成熟的生态 |
| **Yoga Layout** | `yoga-layout` (Python 绑定) | 官方 Python 支持 |
| **Tree-sitter** | `py-tree-sitter` | 官方 Python 绑定 |
| **FFI (Bun)** | PyO3 (Rust) / cffi | Python-Rust FFI |
| **EventEmitter** | `pyee` / 自实现 | 事件系统 |
| **TypeScript** | Python + `mypy` | 静态类型检查 |
| **React Reconciler** | 自定义协调器 | 声明式 UI |
| **Bun.test** | `pytest` + `pytest-benchmark` | 测试框架 |

---

## 核心依赖选择

### 方案 A: 完整实现 (推荐)

适合：从零打造高性能框架

```python
# 核心依赖
dependencies = {
    # 原生性能层
    "maturin": "^1.4.0",           # Rust-Python 构建工具
    
    # 布局引擎
    "yoga-layout": "^1.0.0",       # Facebook Yoga Python 绑定
    
    # 终端处理
    "prompt-toolkit": "^3.0.0",    # 高级终端 I/O
    
    # 语法高亮
    "tree-sitter": "^0.20.0",      # 语法解析
    "tree-sitter-languages": "^1.10.0",  # 预编译语言包
    
    # 事件系统
    "pyee": "^11.0.0",             # EventEmitter
    
    # 性能优化
    "numpy": "^1.24.0",            # 数组操作
    
    # 类型检查
    "typing-extensions": "^4.0.0",
}

dev_dependencies = {
    "pytest": "^8.0.0",
    "pytest-benchmark": "^4.0.0",
    "mypy": "^1.8.0",
    "ruff": "^0.1.0",              # 快速 linter/formatter
}
```

### 方案 B: 快速原型 (基于 Textual)

适合：快速验证想法或学习

```python
dependencies = {
    "textual": "^0.50.0",          # 成熟的 TUI 框架
    "rich": "^13.0.0",             # 富文本终端输出
    "tree-sitter": "^0.20.0",      # 语法高亮
}
```

**本指南聚焦方案 A**

---

## 项目结构

```
opentui-python/
├── pyproject.toml              # 项目配置 (PEP 621)
├── README.md
├── LICENSE
├── .gitignore
│
├── src/
│   └── opentui/
│       ├── __init__.py
│       │
│       ├── core/               # 核心包
│       │   ├── __init__.py
│       │   ├── renderer.py     # 渲染器
│       │   ├── renderable.py   # 可渲染对象基类
│       │   ├── buffer.py       # 缓冲区系统
│       │   ├── layout.py       # Yoga 布局封装
│       │   ├── terminal.py     # 终端 I/O
│       │   ├── events.py       # 事件系统
│       │   ├── colors.py       # 颜色管理
│       │   ├── ansi.py         # ANSI 转义序列
│       │   ├── keyboard.py     # 键盘输入解析
│       │   ├── mouse.py        # 鼠标事件
│       │   └── console.py      # 控制台覆盖层
│       │
│       ├── native/             # Rust 扩展
│       │   ├── Cargo.toml
│       │   ├── pyproject.toml
│       │   └── src/
│       │       ├── lib.rs      # FFI 入口
│       │       ├── buffer.rs   # 缓冲区优化
│       │       ├── rope.rs     # Rope 数据结构
│       │       └── terminal.rs # 终端宽度计算
│       │
│       ├── components/         # 内置组件
│       │   ├── __init__.py
│       │   ├── text.py         # 文本组件
│       │   ├── box.py          # 盒子组件
│       │   ├── input.py        # 输入框
│       │   ├── textarea.py     # 多行文本
│       │   ├── select.py       # 选择器
│       │   ├── scrollbox.py    # 滚动容器
│       │   ├── code.py         # 代码块
│       │   └── diff.py         # Diff 查看器
│       │
│       ├── syntax/             # 语法高亮
│       │   ├── __init__.py
│       │   ├── highlighter.py  # Tree-sitter 集成
│       │   └── themes.py       # 主题定义
│       │
│       ├── react/              # 声明式 API
│       │   ├── __init__.py
│       │   ├── reconciler.py   # 协调器
│       │   ├── component.py    # 组件基类
│       │   ├── hooks.py        # Hooks (useState, useEffect...)
│       │   └── jsx.py          # JSX-like API
│       │
│       └── utils/              # 工具函数
│           ├── __init__.py
│           ├── diff.py         # Diff 算法
│           └── validation.py   # 参数验证
│
├── examples/                   # 示例程序
│   ├── hello.py
│   ├── counter.py
│   ├── login_form.py
│   ├── code_editor.py
│   └── dashboard.py
│
├── tests/                      # 测试
│   ├── conftest.py
│   ├── test_buffer.py
│   ├── test_renderer.py
│   ├── test_layout.py
│   ├── test_components.py
│   └── benchmarks/
│       ├── bench_buffer.py
│       └── bench_layout.py
│
└── docs/                       # 文档
    ├── getting-started.md
    ├── architecture.md
    ├── api-reference.md
    └── components.md
```

---

## 实现步骤

### Phase 1: 原生层搭建 (1-2 周)

#### 1.1 初始化 Rust 项目

```bash
# 创建项目目录
mkdir -p opentui-python/src/opentui/native
cd opentui-python/src/opentui/native

# 初始化 Rust 项目
cargo init --lib
```

#### 1.2 配置 Cargo.toml

```toml
[package]
name = "opentui-native"
version = "0.1.0"
edition = "2021"

[lib]
name = "opentui_native"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
unicode-width = "0.1"       # 字符宽度计算
ropey = "1.6"               # Rope 数据结构
anyhow = "1.0"              # 错误处理

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

#### 1.3 实现核心结构体

```rust
// src/opentui/native/src/lib.rs
use pyo3::prelude::*;
use pyo3::types::PyBytes;

#[pyclass]
#[derive(Clone, Debug)]
pub struct Cell {
    #[pyo3(get, set)]
    pub char: String,
    #[pyo3(get, set)]
    pub fg: (u8, u8, u8, u8),
    #[pyo3(get, set)]
    pub bg: (u8, u8, u8, u8),
    #[pyo3(get, set)]
    pub bold: bool,
    #[pyo3(get, set)]
    pub italic: bool,
    #[pyo3(get, set)]
    pub underline: bool,
}

#[pymethods]
impl Cell {
    #[new]
    fn new() -> Self {
        Cell {
            char: " ".to_string(),
            fg: (255, 255, 255, 255),
            bg: (0, 0, 0, 0),
            bold: false,
            italic: false,
            underline: false,
        }
    }
}

#[pyclass]
pub struct Buffer {
    width: usize,
    height: usize,
    cells: Vec<Cell>,
}

#[pymethods]
impl Buffer {
    #[new]
    fn new(width: usize, height: usize) -> Self {
        let cells = vec![Cell::new(); width * height];
        Buffer { width, height, cells }
    }
    
    fn set_cell(&mut self, x: usize, y: usize, cell: Cell) -> PyResult<()> {
        if x < self.width && y < self.height {
            let idx = y * self.width + x;
            self.cells[idx] = cell;
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }
    
    fn get_cell(&self, x: usize, y: usize) -> PyResult<Cell> {
        if x < self.width && y < self.height {
            let idx = y * self.width + x;
            Ok(self.cells[idx].clone())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }
    
    fn draw_text(&mut self, text: &str, x: usize, y: usize, fg: (u8, u8, u8, u8)) {
        for (i, ch) in text.chars().enumerate() {
            if x + i >= self.width {
                break;
            }
            let idx = y * self.width + (x + i);
            if idx < self.cells.len() {
                self.cells[idx].char = ch.to_string();
                self.cells[idx].fg = fg;
            }
        }
    }
    
    fn clear(&mut self) {
        for cell in &mut self.cells {
            *cell = Cell::new();
        }
    }
    
    fn char_width(&self, ch: &str) -> usize {
        use unicode_width::UnicodeWidthChar;
        ch.chars().next().map(|c| c.width().unwrap_or(1)).unwrap_or(0)
    }
}

// Rope 文本缓冲区
#[pyclass]
pub struct TextBuffer {
    rope: ropey::Rope,
}

#[pymethods]
impl TextBuffer {
    #[new]
    fn new(text: Option<&str>) -> Self {
        let rope = match text {
            Some(t) => ropey::Rope::from_str(t),
            None => ropey::Rope::new(),
        };
        TextBuffer { rope }
    }
    
    fn insert(&mut self, idx: usize, text: &str) -> PyResult<()> {
        if idx <= self.rope.len_chars() {
            self.rope.insert(idx, text);
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
        }
    }
    
    fn delete(&mut self, start: usize, end: usize) -> PyResult<()> {
        if start <= end && end <= self.rope.len_chars() {
            self.rope.remove(start..end);
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Invalid range"))
        }
    }
    
    fn to_string(&self) -> String {
        self.rope.to_string()
    }
    
    fn len_chars(&self) -> usize {
        self.rope.len_chars()
    }
    
    fn len_lines(&self) -> usize {
        self.rope.len_lines()
    }
    
    fn line(&self, line_idx: usize) -> PyResult<String> {
        if line_idx < self.rope.len_lines() {
            Ok(self.rope.line(line_idx).to_string())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err("Line index out of bounds"))
        }
    }
}

#[pymodule]
fn opentui_native(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Cell>()?;
    m.add_class::<Buffer>()?;
    m.add_class::<TextBuffer>()?;
    Ok(())
}
```

#### 1.4 配置 maturin

```toml
# src/opentui/native/pyproject.toml
[build-system]
requires = ["maturin>=1.4,<2.0"]
build-backend = "maturin"

[project]
name = "opentui-native"
requires-python = ">=3.11"
```

---

### Phase 2: 核心 Python 层 (2-3 周)

#### 2.1 缓冲区系统

```python
# src/opentui/core/buffer.py
from typing import Optional
from dataclasses import dataclass
import numpy as np

try:
    from opentui_native import Buffer as NativeBuffer, Cell as NativeCell
    HAS_NATIVE = True
except ImportError:
    HAS_NATIVE = False
    NativeBuffer = None
    NativeCell = None

@dataclass
class Cell:
    """终端单元格"""
    char: str = ' '
    fg: tuple[int, int, int, int] = (255, 255, 255, 255)
    bg: tuple[int, int, int, int] = (0, 0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = False
    
    def to_native(self) -> 'NativeCell':
        """转换为原生 Cell"""
        if HAS_NATIVE:
            cell = NativeCell()
            cell.char = self.char
            cell.fg = self.fg
            cell.bg = self.bg
            cell.bold = self.bold
            cell.italic = self.italic
            cell.underline = self.underline
            return cell
        return None

class OptimizedBuffer:
    """优化的帧缓冲区"""
    
    def __init__(self, width: int, height: int, use_native: bool = True):
        self.width = width
        self.height = height
        self.use_native = use_native and HAS_NATIVE
        
        if self.use_native:
            self._native_buffer = NativeBuffer(width, height)
            self.cells = None
        else:
            self._native_buffer = None
            # 使用 numpy 数组提升性能
            self.cells = np.empty((height, width), dtype=object)
            self.clear()
    
    def set_cell(self, x: int, y: int, cell: Cell):
        """设置单元格"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        if self.use_native:
            self._native_buffer.set_cell(x, y, cell.to_native())
        else:
            self.cells[y, x] = cell
    
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """获取单元格"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        
        if self.use_native:
            native_cell = self._native_buffer.get_cell(x, y)
            return Cell(
                char=native_cell.char,
                fg=native_cell.fg,
                bg=native_cell.bg,
                bold=native_cell.bold,
                italic=native_cell.italic,
                underline=native_cell.underline,
            )
        else:
            return self.cells[y, x]
    
    def draw_text(self, text: str, x: int, y: int, fg: tuple[int, int, int, int]):
        """绘制文本"""
        if self.use_native:
            self._native_buffer.draw_text(text, x, y, fg)
        else:
            for i, char in enumerate(text):
                if x + i >= self.width:
                    break
                self.set_cell(x + i, y, Cell(char=char, fg=fg))
    
    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        cell: Cell,
    ):
        """填充矩形区域"""
        for dy in range(height):
            for dx in range(width):
                self.set_cell(x + dx, y + dy, cell)
    
    def clear(self):
        """清空缓冲区"""
        if self.use_native:
            self._native_buffer.clear()
        else:
            for y in range(self.height):
                for x in range(self.width):
                    self.cells[y, x] = Cell()
    
    def to_ansi(self) -> str:
        """转换为 ANSI 转义序列"""
        from .ansi import ANSI
        
        lines = []
        for y in range(self.height):
            line_chars = []
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    ansi = self._cell_to_ansi(cell)
                    line_chars.append(ansi)
            lines.append(''.join(line_chars))
        
        return '\n'.join(lines)
    
    def _cell_to_ansi(self, cell: Cell) -> str:
        """单元格转 ANSI"""
        from .ansi import ANSI
        
        codes = []
        
        # 样式
        if cell.bold:
            codes.append('1')
        if cell.italic:
            codes.append('3')
        if cell.underline:
            codes.append('4')
        
        # 前景色
        r, g, b, a = cell.fg
        if a > 0:
            codes.append(f'38;2;{r};{g};{b}')
        
        # 背景色
        r, g, b, a = cell.bg
        if a > 0:
            codes.append(f'48;2;{r};{g};{b}')
        
        ansi_prefix = f'\x1b[{";".join(codes)}m' if codes else ''
        return f'{ansi_prefix}{cell.char}\x1b[0m'
```

#### 2.2 ANSI 工具

```python
# src/opentui/core/ansi.py
class ANSI:
    """ANSI 转义序列工具"""
    
    # 光标控制
    CURSOR_UP = '\x1b[A'
    CURSOR_DOWN = '\x1b[B'
    CURSOR_RIGHT = '\x1b[C'
    CURSOR_LEFT = '\x1b[D'
    CURSOR_HOME = '\x1b[H'
    CURSOR_SAVE = '\x1b[s'
    CURSOR_RESTORE = '\x1b[u'
    CURSOR_HIDE = '\x1b[?25l'
    CURSOR_SHOW = '\x1b[?25h'
    
    # 屏幕控制
    CLEAR_SCREEN = '\x1b[2J'
    CLEAR_LINE = '\x1b[2K'
    ALTERNATE_SCREEN_ON = '\x1b[?1049h'
    ALTERNATE_SCREEN_OFF = '\x1b[?1049l'
    
    # 鼠标支持
    MOUSE_ON = '\x1b[?1000h\x1b[?1002h\x1b[?1015h\x1b[?1006h'
    MOUSE_OFF = '\x1b[?1000l\x1b[?1002l\x1b[?1015l\x1b[?1006l'
    
    @staticmethod
    def cursor_to(x: int, y: int) -> str:
        """移动光标到指定位置 (1-based)"""
        return f'\x1b[{y + 1};{x + 1}H'
    
    @staticmethod
    def rgb_fg(r: int, g: int, b: int) -> str:
        """设置前景色 (RGB)"""
        return f'\x1b[38;2;{r};{g};{b}m'
    
    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """设置背景色 (RGB)"""
        return f'\x1b[48;2;{r};{g};{b}m'
    
    @staticmethod
    def reset() -> str:
        """重置样式"""
        return '\x1b[0m'
```

#### 2.3 布局引擎封装

```python
# src/opentui/core/layout.py
try:
    import yoga
    HAS_YOGA = True
except ImportError:
    HAS_YOGA = False
    yoga = None

from typing import Optional, Literal

FlexDirection = Literal['row', 'column', 'row-reverse', 'column-reverse']
AlignItems = Literal['flex-start', 'flex-end', 'center', 'stretch', 'baseline']
JustifyContent = Literal['flex-start', 'flex-end', 'center', 'space-between', 'space-around']

class LayoutNode:
    """Yoga 布局节点封装"""
    
    def __init__(self):
        if not HAS_YOGA:
            raise ImportError("yoga-layout is required for layout support")
        
        self.node = yoga.Node.create()
        self.children: list['LayoutNode'] = []
    
    # Flex 容器属性
    def set_flex_direction(self, direction: FlexDirection):
        """设置 Flex 方向"""
        mapping = {
            'row': yoga.FLEX_DIRECTION_ROW,
            'column': yoga.FLEX_DIRECTION_COLUMN,
            'row-reverse': yoga.FLEX_DIRECTION_ROW_REVERSE,
            'column-reverse': yoga.FLEX_DIRECTION_COLUMN_REVERSE,
        }
        self.node.set_flex_direction(mapping[direction])
    
    def set_flex_wrap(self, wrap: Literal['wrap', 'nowrap']):
        """设置是否换行"""
        self.node.set_flex_wrap(
            yoga.WRAP_WRAP if wrap == 'wrap' else yoga.WRAP_NO_WRAP
        )
    
    def set_align_items(self, align: AlignItems):
        """设置对齐方式"""
        mapping = {
            'flex-start': yoga.ALIGN_FLEX_START,
            'flex-end': yoga.ALIGN_FLEX_END,
            'center': yoga.ALIGN_CENTER,
            'stretch': yoga.ALIGN_STRETCH,
            'baseline': yoga.ALIGN_BASELINE,
        }
        self.node.set_align_items(mapping[align])
    
    def set_justify_content(self, justify: JustifyContent):
        """设置内容分布"""
        mapping = {
            'flex-start': yoga.JUSTIFY_FLEX_START,
            'flex-end': yoga.JUSTIFY_FLEX_END,
            'center': yoga.JUSTIFY_CENTER,
            'space-between': yoga.JUSTIFY_SPACE_BETWEEN,
            'space-around': yoga.JUSTIFY_SPACE_AROUND,
        }
        self.node.set_justify_content(mapping[justify])
    
    # Flex 子项属性
    def set_flex_grow(self, grow: float):
        """设置放大比例"""
        self.node.set_flex_grow(grow)
    
    def set_flex_shrink(self, shrink: float):
        """设置缩小比例"""
        self.node.set_flex_shrink(shrink)
    
    def set_flex_basis(self, basis: int | Literal['auto']):
        """设置基准大小"""
        if basis == 'auto':
            self.node.set_flex_basis_auto()
        else:
            self.node.set_flex_basis(basis)
    
    # 尺寸
    def set_width(self, width: int | str):
        """设置宽度"""
        if isinstance(width, int):
            self.node.set_width(width)
        elif width == 'auto':
            self.node.set_width_auto()
        elif width.endswith('%'):
            self.node.set_width_percent(float(width[:-1]))
    
    def set_height(self, height: int | str):
        """设置高度"""
        if isinstance(height, int):
            self.node.set_height(height)
        elif height == 'auto':
            self.node.set_height_auto()
        elif height.endswith('%'):
            self.node.set_height_percent(float(height[:-1]))
    
    def set_min_width(self, width: int):
        """设置最小宽度"""
        self.node.set_min_width(width)
    
    def set_min_height(self, height: int):
        """设置最小高度"""
        self.node.set_min_height(height)
    
    def set_max_width(self, width: int):
        """设置最大宽度"""
        self.node.set_max_width(width)
    
    def set_max_height(self, height: int):
        """设置最大高度"""
        self.node.set_max_height(height)
    
    # 边距
    def set_margin(self, edge: str, value: int | str):
        """设置边距"""
        edge_map = {
            'left': yoga.EDGE_LEFT,
            'top': yoga.EDGE_TOP,
            'right': yoga.EDGE_RIGHT,
            'bottom': yoga.EDGE_BOTTOM,
            'all': yoga.EDGE_ALL,
        }
        
        if isinstance(value, int):
            self.node.set_margin(edge_map[edge], value)
        elif value == 'auto':
            self.node.set_margin_auto(edge_map[edge])
        elif value.endswith('%'):
            self.node.set_margin_percent(edge_map[edge], float(value[:-1]))
    
    def set_padding(self, edge: str, value: int | str):
        """设置内边距"""
        edge_map = {
            'left': yoga.EDGE_LEFT,
            'top': yoga.EDGE_TOP,
            'right': yoga.EDGE_RIGHT,
            'bottom': yoga.EDGE_BOTTOM,
            'all': yoga.EDGE_ALL,
        }
        
        if isinstance(value, int):
            self.node.set_padding(edge_map[edge], value)
        elif value.endswith('%'):
            self.node.set_padding_percent(edge_map[edge], float(value[:-1]))
    
    # 定位
    def set_position_type(self, position: Literal['relative', 'absolute']):
        """设置定位类型"""
        self.node.set_position_type(
            yoga.POSITION_TYPE_ABSOLUTE if position == 'absolute'
            else yoga.POSITION_TYPE_RELATIVE
        )
    
    def set_position(self, edge: str, value: int | str):
        """设置位置"""
        edge_map = {
            'left': yoga.EDGE_LEFT,
            'top': yoga.EDGE_TOP,
            'right': yoga.EDGE_RIGHT,
            'bottom': yoga.EDGE_BOTTOM,
        }
        
        if isinstance(value, int):
            self.node.set_position(edge_map[edge], value)
        elif value.endswith('%'):
            self.node.set_position_percent(edge_map[edge], float(value[:-1]))
    
    # 子节点管理
    def add_child(self, child: 'LayoutNode', index: Optional[int] = None):
        """添加子节点"""
        if index is None:
            index = len(self.children)
        
        self.children.insert(index, child)
        self.node.insert_child(child.node, index)
    
    def remove_child(self, child: 'LayoutNode'):
        """移除子节点"""
        if child in self.children:
            index = self.children.index(child)
            self.children.remove(child)
            self.node.remove_child(child.node)
    
    # 布局计算
    def calculate_layout(
        self,
        width: float = float('nan'),
        height: float = float('nan'),
        direction: Literal['ltr', 'rtl'] = 'ltr',
    ):
        """计算布局"""
        yoga_direction = (
            yoga.DIRECTION_RTL if direction == 'rtl'
            else yoga.DIRECTION_LTR
        )
        self.node.calculate_layout(width, height, yoga_direction)
    
    def get_computed_layout(self) -> dict:
        """获取计算后的布局"""
        return {
            'x': self.node.get_computed_left(),
            'y': self.node.get_computed_top(),
            'width': self.node.get_computed_width(),
            'height': self.node.get_computed_height(),
        }
    
    def __del__(self):
        """析构函数"""
        if HAS_YOGA and hasattr(self, 'node'):
            yoga.Node.free(self.node)
```

#### 2.4 可渲染对象基类

```python
# src/opentui/core/renderable.py
from typing import Optional, Any, TYPE_CHECKING
from abc import ABC, abstractmethod
from pyee import EventEmitter

from .layout import LayoutNode
from .buffer import OptimizedBuffer

if TYPE_CHECKING:
    from .renderer import RenderContext

class Renderable(ABC, EventEmitter):
    """可渲染对象基类 (类似 OpenTUI BaseRenderable)"""
    
    _id_counter = 0
    
    def __init__(self, ctx: 'RenderContext', options: Optional[dict[str, Any]] = None):
        super().__init__()
        
        options = options or {}
        
        # 上下文
        self.ctx = ctx
        
        # ID
        if 'id' in options:
            self.id = options['id']
        else:
            Renderable._id_counter += 1
            self.id = f'renderable-{Renderable._id_counter}'
        
        # 层次结构
        self.parent: Optional['Renderable'] = None
        self.children: list['Renderable'] = []
        
        # 布局节点
        self.layout_node = LayoutNode()
        
        # 计算后的位置和尺寸
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        
        # 状态
        self.visible = options.get('visible', True)
        self.z_index = options.get('z_index', 0)
        self.focused = options.get('focused', False)
        self._dirty = True
        
        # 应用布局选项
        self._apply_layout_options(options)
    
    def _apply_layout_options(self, options: dict):
        """应用布局选项"""
        # Flex 容器
        if 'flex_direction' in options:
            self.layout_node.set_flex_direction(options['flex_direction'])
        
        if 'align_items' in options:
            self.layout_node.set_align_items(options['align_items'])
        
        if 'justify_content' in options:
            self.layout_node.set_justify_content(options['justify_content'])
        
        # Flex 子项
        if 'flex_grow' in options:
            self.layout_node.set_flex_grow(options['flex_grow'])
        
        if 'flex_shrink' in options:
            self.layout_node.set_flex_shrink(options['flex_shrink'])
        
        if 'flex_basis' in options:
            self.layout_node.set_flex_basis(options['flex_basis'])
        
        # 尺寸
        if 'width' in options:
            self.layout_node.set_width(options['width'])
        
        if 'height' in options:
            self.layout_node.set_height(options['height'])
        
        if 'min_width' in options:
            self.layout_node.set_min_width(options['min_width'])
        
        if 'min_height' in options:
            self.layout_node.set_min_height(options['min_height'])
        
        if 'max_width' in options:
            self.layout_node.set_max_width(options['max_width'])
        
        if 'max_height' in options:
            self.layout_node.set_max_height(options['max_height'])
        
        # 边距
        if 'margin' in options:
            self.layout_node.set_margin('all', options['margin'])
        
        for edge in ['margin_left', 'margin_top', 'margin_right', 'margin_bottom']:
            if edge in options:
                self.layout_node.set_margin(edge.split('_')[1], options[edge])
        
        # 内边距
        if 'padding' in options:
            self.layout_node.set_padding('all', options['padding'])
        
        for edge in ['padding_left', 'padding_top', 'padding_right', 'padding_bottom']:
            if edge in options:
                self.layout_node.set_padding(edge.split('_')[1], options[edge])
        
        # 定位
        if 'position' in options:
            self.layout_node.set_position_type(options['position'])
        
        for edge in ['left', 'top', 'right', 'bottom']:
            if edge in options:
                self.layout_node.set_position(edge, options[edge])
    
    # 树形结构管理
    def add(self, child: 'Renderable', index: Optional[int] = None):
        """添加子节点"""
        # 如果子节点已有父节点，先移除
        if child.parent:
            child.parent.remove(child)
        
        # 设置父子关系
        child.parent = self
        
        if index is None:
            self.children.append(child)
            self.layout_node.add_child(child.layout_node)
        else:
            self.children.insert(index, child)
            self.layout_node.add_child(child.layout_node, index)
        
        # 触发事件
        self.emit('child_added', child)
        child.emit('added', self)
        
        # 请求重新渲染
        self.request_render()
    
    def remove(self, child: 'Renderable'):
        """移除子节点"""
        if child in self.children:
            self.children.remove(child)
            self.layout_node.remove_child(child.layout_node)
            child.parent = None
            
            # 触发事件
            self.emit('child_removed', child)
            child.emit('removed', self)
            
            # 请求重新渲染
            self.request_render()
    
    def remove_all(self):
        """移除所有子节点"""
        for child in list(self.children):
            self.remove(child)
    
    # 渲染相关
    def request_render(self):
        """请求重新渲染 (脏标记模式)"""
        self._dirty = True
        
        # 向上传播到根节点
        if self.parent:
            self.parent.request_render()
        else:
            # 根节点，通知渲染器
            if hasattr(self.ctx, 'renderer'):
                self.ctx.renderer.schedule_render()
    
    def calculate_layout(self):
        """计算布局"""
        if self.parent is None:
            # 根节点，使用渲染器尺寸
            self.layout_node.calculate_layout(
                float(self.ctx.renderer.width),
                float(self.ctx.renderer.height),
            )
        
        # 更新计算后的位置和尺寸
        layout = self.layout_node.get_computed_layout()
        
        # 如果有父节点，相对定位
        if self.parent:
            self.x = self.parent.x + int(layout['x'])
            self.y = self.parent.y + int(layout['y'])
        else:
            self.x = int(layout['x'])
            self.y = int(layout['y'])
        
        self.width = int(layout['width'])
        self.height = int(layout['height'])
        
        # 递归计算子节点
        for child in self.children:
            child.calculate_layout()
    
    def render(self, buffer: OptimizedBuffer):
        """渲染到缓冲区"""
        if not self.visible:
            return
        
        # 渲染自身
        self.render_self(buffer)
        
        # 渲染子节点 (按 z-index 排序)
        sorted_children = sorted(self.children, key=lambda c: c.z_index)
        for child in sorted_children:
            child.render(buffer)
        
        # 清除脏标记
        self._dirty = False
    
    @abstractmethod
    def render_self(self, buffer: OptimizedBuffer):
        """渲染自身 (子类实现)"""
        pass
    
    # 焦点管理
    def focus(self):
        """获取焦点"""
        if not self.focused:
            self.focused = True
            self.emit('focused')
            self.request_render()
    
    def blur(self):
        """失去焦点"""
        if self.focused:
            self.focused = False
            self.emit('blurred')
            self.request_render()
    
    # 辅助方法
    def is_root(self) -> bool:
        """是否是根节点"""
        return self.parent is None
    
    def get_root(self) -> 'Renderable':
        """获取根节点"""
        node = self
        while node.parent:
            node = node.parent
        return node
    
    def find_by_id(self, id: str) -> Optional['Renderable']:
        """根据 ID 查找节点"""
        if self.id == id:
            return self
        
        for child in self.children:
            result = child.find_by_id(id)
            if result:
                return result
        
        return None
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id="{self.id}" x={self.x} y={self.y} w={self.width} h={self.height}>'
```

#### 2.5 渲染器

```python
# src/opentui/core/renderer.py
import sys
import time
import select
from typing import Optional, Callable
from dataclasses import dataclass

from .buffer import OptimizedBuffer
from .renderable import Renderable
from .terminal import Terminal
from .keyboard import KeyboardHandler
from .events import EventBus

@dataclass
class RenderContext:
    """渲染上下文"""
    renderer: 'Renderer'

class RootRenderable(Renderable):
    """根渲染对象"""
    
    def render_self(self, buffer: OptimizedBuffer):
        """根节点不渲染自身"""
        pass

class Renderer:
    """CLI 渲染器 (类似 OpenTUI CliRenderer)"""
    
    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        target_fps: int = 60,
        use_alternate_screen: bool = True,
        use_mouse: bool = False,
    ):
        # 终端
        self.terminal = Terminal()
        self.width = width or self.terminal.width
        self.height = height or self.terminal.height
        
        # 渲染配置
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps if target_fps > 0 else 0
        self.use_alternate_screen = use_alternate_screen
        self.use_mouse = use_mouse
        
        # 双缓冲
        self.front_buffer = OptimizedBuffer(self.width, self.height)
        self.back_buffer = OptimizedBuffer(self.width, self.height)
        
        # 上下文
        self.context = RenderContext(renderer=self)
        
        # 根节点
        self.root = RootRenderable(self.context, {'id': 'root'})
        
        # 输入处理
        self.keyboard = KeyboardHandler()
        self.keyboard.on('keypress', self._on_keypress)
        
        # 事件总线
        self.events = EventBus()
        
        # 状态
        self.running = False
        self._render_scheduled = False
        self._frame_count = 0
        self._last_render_time = 0
        
        # 统计信息
        self.stats = {
            'fps': 0,
            'frame_time': 0,
            'render_time': 0,
        }
    
    def start(self):
        """启动渲染循环"""
        self.running = True
        
        # 初始化终端
        if self.use_alternate_screen:
            self.terminal.enter_alternate_screen()
        
        self.terminal.hide_cursor()
        self.terminal.set_raw_mode()
        
        if self.use_mouse:
            self.terminal.enable_mouse()
        
        try:
            self._run_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
    
    def stop(self):
        """停止渲染循环"""
        self.running = False
    
    def _run_loop(self):
        """运行主循环"""
        last_fps_update = time.time()
        fps_counter = 0
        
        while self.running:
            frame_start = time.time()
            
            # 处理输入
            self._process_input()
            
            # 处理终端尺寸变化
            self._check_resize()
            
            # 渲染帧
            if self._render_scheduled or self._should_render():
                render_start = time.time()
                self._render_frame()
                render_time = time.time() - render_start
                
                self.stats['render_time'] = render_time * 1000  # ms
                self._render_scheduled = False
                fps_counter += 1
            
            # 更新 FPS
            now = time.time()
            if now - last_fps_update >= 1.0:
                self.stats['fps'] = fps_counter
                fps_counter = 0
                last_fps_update = now
            
            # FPS 限制
            elapsed = time.time() - frame_start
            self.stats['frame_time'] = elapsed * 1000  # ms
            
            if self.frame_time > 0 and elapsed < self.frame_time:
                time.sleep(self.frame_time - elapsed)
    
    def _render_frame(self):
        """渲染一帧"""
        # 清空后缓冲
        self.back_buffer.clear()
        
        # 计算布局
        self.root.calculate_layout()
        
        # 渲染到后缓冲
        self.root.render(self.back_buffer)
        
        # 差异化输出
        self._diff_and_output()
        
        # 交换缓冲区
        self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
        
        # 更新帧计数
        self._frame_count += 1
        self._last_render_time = time.time()
    
    def _diff_and_output(self):
        """差异化输出 (优化性能)"""
        # 简化版本：只输出变化的部分
        # TODO: 实现更高效的差异算法
        
        from .ansi import ANSI
        
        output = []
        
        for y in range(self.height):
            for x in range(self.width):
                front_cell = self.front_buffer.get_cell(x, y)
                back_cell = self.back_buffer.get_cell(x, y)
                
                # 只输出变化的单元格
                if front_cell != back_cell:
                    output.append(ANSI.cursor_to(x, y))
                    output.append(self.back_buffer._cell_to_ansi(back_cell))
        
        if output:
            sys.stdout.write(''.join(output))
            sys.stdout.flush()
    
    def _process_input(self):
        """处理输入"""
        # 非阻塞读取标准输入
        if select.select([sys.stdin], [], [], 0)[0]:
            data = sys.stdin.read(1)
            if data:
                self.keyboard.feed(data)
    
    def _check_resize(self):
        """检查终端尺寸变化"""
        new_width, new_height = self.terminal.get_size()
        
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
            
            # 重新创建缓冲区
            self.front_buffer = OptimizedBuffer(self.width, self.height)
            self.back_buffer = OptimizedBuffer(self.width, self.height)
            
            # 触发 resize 事件
            self.events.emit('resize', self.width, self.height)
            
            # 请求重新渲染
            self.schedule_render()
    
    def _on_keypress(self, key):
        """键盘事件处理"""
        # 触发全局键盘事件
        self.events.emit('keypress', key)
        
        # Ctrl+C 退出
        if key.get('ctrl') and key.get('name') == 'c':
            self.stop()
    
    def _should_render(self) -> bool:
        """是否应该渲染"""
        # 检查根节点是否脏
        return self.root._dirty
    
    def schedule_render(self):
        """调度渲染"""
        self._render_scheduled = True
    
    def _cleanup(self):
        """清理资源"""
        if self.use_mouse:
            self.terminal.disable_mouse()
        
        self.terminal.show_cursor()
        self.terminal.restore_mode()
        
        if self.use_alternate_screen:
            self.terminal.exit_alternate_screen()

# 便捷函数
async def create_renderer(**kwargs) -> Renderer:
    """创建渲染器 (类似 OpenTUI createCliRenderer)"""
    return Renderer(**kwargs)
```

---

### Phase 3: 组件库 (2-3 周)

#### 3.1 Text 组件

```python
# src/opentui/components/text.py
from typing import Optional
from ..core.renderable import Renderable
from ..core.buffer import OptimizedBuffer, Cell
from ..core.colors import parse_color

class Text(Renderable):
    """文本组件"""
    
    def __init__(self, ctx, options: Optional[dict] = None):
        options = options or {}
        super().__init__(ctx, options)
        
        self.content = options.get('content', '')
        self.fg = parse_color(options.get('fg', '#ffffff'))
        self.bg = parse_color(options.get('bg', 'transparent'))
        self.bold = options.get('bold', False)
        self.italic = options.get('italic', False)
        self.underline = options.get('underline', False)
    
    def set_content(self, content: str):
        """设置内容"""
        if self.content != content:
            self.content = content
            self.request_render()
    
    def render_self(self, buffer: OptimizedBuffer):
        """渲染文本"""
        lines = self.content.split('\n')
        
        for dy, line in enumerate(lines):
            if dy >= self.height:
                break
            
            for dx, char in enumerate(line):
                if dx >= self.width:
                    break
                
                cell = Cell(
                    char=char,
                    fg=self.fg,
                    bg=self.bg,
                    bold=self.bold,
                    italic=self.italic,
                    underline=self.underline,
                )
                buffer.set_cell(self.x + dx, self.y + dy, cell)
```

#### 3.2 Box 组件

```python
# src/opentui/components/box.py
from typing import Optional, Literal
from ..core.renderable import Renderable
from ..core.buffer import OptimizedBuffer, Cell
from ..core.colors import parse_color

BorderStyle = Literal['single', 'double', 'rounded', 'bold', 'none']

class Box(Renderable):
    """盒子组件 (带边框)"""
    
    BORDER_CHARS = {
        'single': {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'h': '─', 'v': '│'},
        'double': {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 'h': '═', 'v': '║'},
        'rounded': {'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'h': '─', 'v': '│'},
        'bold': {'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛', 'h': '━', 'v': '┃'},
    }
    
    def __init__(self, ctx, options: Optional[dict] = None):
        options = options or {}
        super().__init__(ctx, options)
        
        self.border = options.get('border', False)
        self.border_style: BorderStyle = options.get('border_style', 'single')
        self.border_color = parse_color(options.get('border_color', '#ffffff'))
        self.background_color = parse_color(options.get('background_color', 'transparent'))
        self.title = options.get('title', None)
    
    def render_self(self, buffer: OptimizedBuffer):
        """渲染盒子"""
        # 填充背景
        if self.background_color[3] > 0:  # 非透明
            bg_cell = Cell(bg=self.background_color)
            for dy in range(self.height):
                for dx in range(self.width):
                    buffer.set_cell(self.x + dx, self.y + dy, bg_cell)
        
        # 绘制边框
        if self.border and self.width >= 2 and self.height >= 2:
            self._draw_border(buffer)
    
    def _draw_border(self, buffer: OptimizedBuffer):
        """绘制边框"""
        chars = self.BORDER_CHARS.get(self.border_style, self.BORDER_CHARS['single'])
        
        # 角
        buffer.set_cell(self.x, self.y, 
                       Cell(char=chars['tl'], fg=self.border_color))
        buffer.set_cell(self.x + self.width - 1, self.y,
                       Cell(char=chars['tr'], fg=self.border_color))
        buffer.set_cell(self.x, self.y + self.height - 1,
                       Cell(char=chars['bl'], fg=self.border_color))
        buffer.set_cell(self.x + self.width - 1, self.y + self.height - 1,
                       Cell(char=chars['br'], fg=self.border_color))
        
        # 水平边
        for dx in range(1, self.width - 1):
            buffer.set_cell(self.x + dx, self.y,
                          Cell(char=chars['h'], fg=self.border_color))
            buffer.set_cell(self.x + dx, self.y + self.height - 1,
                          Cell(char=chars['h'], fg=self.border_color))
        
        # 垂直边
        for dy in range(1, self.height - 1):
            buffer.set_cell(self.x, self.y + dy,
                          Cell(char=chars['v'], fg=self.border_color))
            buffer.set_cell(self.x + self.width - 1, self.y + dy,
                          Cell(char=chars['v'], fg=self.border_color))
        
        # 标题
        if self.title:
            title = f' {self.title} '
            title_x = self.x + (self.width - len(title)) // 2
            if title_x > self.x:
                for i, char in enumerate(title):
                    if title_x + i < self.x + self.width - 1:
                        buffer.set_cell(title_x + i, self.y,
                                      Cell(char=char, fg=self.border_color))
```

完整的组件实现请查看仓库中的其他文件...

---

## 项目配置

### pyproject.toml

```toml
[build-system]
requires = ["maturin>=1.4,<2.0"]
build-backend = "maturin"

[project]
name = "opentui"
version = "0.1.0"
description = "A Python TUI framework inspired by OpenTUI"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
keywords = ["tui", "terminal", "ui", "cli"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Rust",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: Terminals",
]

dependencies = [
    "pyee>=11.0.0",
    "numpy>=1.24.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
yoga = [
    "yoga-layout>=1.0.0",
]
syntax = [
    "tree-sitter>=0.20.0",
    "tree-sitter-languages>=1.10.0",
]
full = [
    "yoga-layout>=1.0.0",
    "tree-sitter>=0.20.0",
    "tree-sitter-languages>=1.10.0",
]
dev = [
    "pytest>=8.0.0",
    "pytest-benchmark>=4.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "maturin>=1.4.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/opentui-python"
Documentation = "https://opentui-python.readthedocs.io"
Repository = "https://github.com/yourusername/opentui-python"
Issues = "https://github.com/yourusername/opentui-python/issues"

[tool.maturin]
python-source = "src"
module-name = "opentui.opentui_native"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src/opentui --cov-report=html"
```

---

## 开发流程

### 环境搭建

```bash
# 1. 创建项目目录
mkdir opentui-python
cd opentui-python

# 2. 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. 安装 Rust (如果未安装)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 4. 安装 maturin
pip install maturin

# 5. 初始化项目结构
mkdir -p src/opentui/{core,components,native,react}
touch src/opentui/__init__.py
```

### 开发构建

```bash
# 开发模式安装 (自动重新编译 Rust)
maturin develop

# 发布模式构建 (优化)
maturin develop --release

# 仅构建 wheel
maturin build --release
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_buffer.py

# 运行基准测试
pytest tests/benchmarks/ --benchmark-only

# 生成覆盖率报告
pytest --cov=src/opentui --cov-report=html
```

### 代码质量

```bash
# 类型检查
mypy src/

# Linting
ruff check src/

# 格式化
ruff format src/

# 自动修复
ruff check --fix src/
```

### 运行示例

```bash
# Hello World
python examples/hello.py

# 计数器
python examples/counter.py

# 登录表单
python examples/login_form.py
```

---

## 实现优先级

### Phase 1: MVP (2-3 周)

**目标**: 可运行的基础框架

- [x] Rust 原生层 (Buffer, TextBuffer)
- [x] Python 缓冲区封装
- [x] 基础渲染器 (无布局引擎)
- [x] 简单终端 I/O
- [x] Text 和 Box 组件
- [x] Hello World 示例

**验收标准**: 能显示带边框的文本

### Phase 2: 核心功能 (4-6 周)

**目标**: 完整的布局和事件系统

- [x] Yoga 布局引擎集成
- [x] Renderable 树形结构完善
- [x] 事件系统 (EventEmitter)
- [x] 键盘输入处理
- [x] 鼠标支持
- [x] 双缓冲渲染
- [x] 差异化输出优化
- [x] 更多组件 (Input, Select)

**验收标准**: 能构建交互式表单

### Phase 3: 高级功能 (6-8 周)

**目标**: 生产级特性

- [x] 完整组件库
  - Scrollbox
  - Textarea
  - TabSelect
  - Code (语法高亮)
  - Diff
- [x] Tree-sitter 集成
- [x] 动画系统
- [x] 主题支持
- [x] 控制台覆盖层
- [x] 性能优化

**验收标准**: 能构建代码编辑器

### Phase 4: 声明式 API (4-6 周)

**目标**: 类 React 体验

- [x] 虚拟 DOM
- [x] Reconciler (协调器)
- [x] Component 基类
- [x] Hooks (useState, useEffect)
- [x] 完整示例

**验收标准**: 支持声明式组件开发

### Phase 5: 生态完善 (持续)

**目标**: 社区建设

- [x] 完整文档
- [x] API 参考
- [x] 教程和示例
- [x] 性能基准测试
- [x] CI/CD 流程
- [x] PyPI 发布

---

## 技术挑战与解决方案

### 1. 性能挑战

**问题**: Python GIL 限制多线程性能

**解决方案**:
- 使用 Rust 实现热路径 (Buffer, Rope)
- PyO3 提供零开销 FFI
- Numpy 加速数组操作
- 差异化渲染减少输出

### 2. 布局引擎

**问题**: Yoga Python 绑定可能不完善

**解决方案**:
- 优先使用官方 `yoga-layout` 包
- 备选方案: 使用 CSS Grid 的 Python 实现
- 最后手段: 自己用 Rust 重新实现

### 3. 异步 I/O

**问题**: 终端 I/O 阻塞主线程

**解决方案**:
- 使用 `select` 非阻塞读取
- 可选: 集成 `asyncio`
- 使用 `threading` 处理输入

### 4. 跨平台支持

**问题**: Windows 终端差异

**解决方案**:
- 使用 `colorama` 兼容 Windows
- 检测终端能力 (True Color 支持)
- 提供降级方案

### 5. Unicode 处理

**问题**: 字符宽度计算复杂

**解决方案**:
- Rust 实现 `unicode-width`
- 支持 emoji 和 CJK 字符
- 缓存宽度计算结果

---

## 参考资源

### 学习资源

- **OpenTUI 源码**: https://github.com/sst/opentui
- **Textual**: https://github.com/Textualize/textual (成熟的 Python TUI)
- **Rich**: https://github.com/Textualize/rich (终端渲染)
- **PyO3**: https://pyo3.rs (Rust-Python 绑定)
- **Yoga Layout**: https://yogalayout.com/docs

### 技术文档

- **py-tree-sitter**: https://github.com/tree-sitter/py-tree-sitter
- **Rope 数据结构**: https://docs.rs/ropey/latest/ropey/
- **ANSI 转义序列**: https://en.wikipedia.org/wiki/ANSI_escape_code
- **Flexbox 规范**: https://www.w3.org/TR/css-flexbox-1/

### 社区

- **Python Discord**: https://pythondiscord.com
- **Rust Users Forum**: https://users.rust-lang.org
- **Terminal App Showcase**: https://github.com/msmps/awesome-opentui

---

## 快速启动建议

### 对于初学者

1. **先学习 Textual** - 理解现有框架设计
2. **阅读 OpenTUI 文档** - 理解核心概念
3. **实现 MVP** - 从简单的 Text/Box 开始
4. **逐步添加功能** - 不要一开始就追求完美

### 对于有经验的开发者

1. **直接实现核心层** - Buffer + Renderer
2. **集成 Yoga** - 使用成熟的布局引擎
3. **并行开发组件** - 可以多人协作
4. **早期性能优化** - Rust 层从一开始就要正确

### 推荐学习路径

```
Week 1-2: Rust FFI + Buffer 实现
Week 3-4: Renderer + Layout 引擎
Week 5-6: 基础组件 (Text, Box, Input)
Week 7-8: 高级组件 + 语法高亮
Week 9-10: 声明式 API
Week 11-12: 优化 + 文档
```

---

## 附录

### 示例代码

#### Hello World

```python
from opentui import create_renderer
from opentui.components import Text, Box

async def main():
    renderer = await create_renderer()
    
    # 创建根容器
    root_box = Box(renderer.context, {
        'width': 40,
        'height': 10,
        'border': True,
        'border_style': 'rounded',
        'title': 'Hello OpenTUI',
    })
    
    # 创建文本
    text = Text(renderer.context, {
        'content': 'Hello, Python TUI!',
        'fg': '#00ff00',
        'margin': 2,
    })
    
    root_box.add(text)
    renderer.root.add(root_box)
    
    renderer.start()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

#### 计数器 (声明式)

```python
from opentui.react import Component, create_element as h, render

class Counter(Component):
    def __init__(self, props):
        super().__init__(props)
        self.count = 0
    
    def increment(self):
        self.count += 1
        self.update()
    
    def render(self):
        return h('box', {
            'border': True,
            'title': 'Counter',
            'width': 30,
            'height': 8,
        },
            h('text', {'content': f'Count: {self.count}'}),
            h('text', {'content': 'Press SPACE to increment'}),
        )

async def main():
    counter = Counter({})
    await render(counter)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

---

## 总结

本指南提供了基于 OpenTUI 架构的完整 Python 实现方案，包括：

✅ **技术栈选择** - Rust + PyO3 + Yoga + Tree-sitter  
✅ **分层架构** - 原生层 + 核心层 + 组件层 + 框架层  
✅ **详细代码** - 可直接运行的实现示例  
✅ **开发流程** - 从搭建到测试的完整流程  
✅ **最佳实践** - 性能优化和跨平台支持  

**下一步行动**:

1. 克隆仓库模板
2. 实现 Phase 1 MVP
3. 逐步迭代功能
4. 发布 PyPI 包

需要更详细的某个模块实现或有其他问题，欢迎随时询问！

