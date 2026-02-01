# pytui-native

Rust 扩展（Cell、Buffer、TextBuffer、CliRenderer、Hit Grid、Terminal、LinkPool、Debug/Dump），与 OpenTUI Zig 层对齐（方案 B）。模块与测试按 [Rust 重构与 OpenTUI Zig 完全对齐执行计划](../../../docs/rust-refactor-opentui-alignment-plan.md) 与 `opentui/packages/core/src/zig/` 一一对应。

## 模块与 Zig 对应关系

| Rust 模块 | 对应 Zig 文件 | 功能概要 |
|-----------|----------------|----------|
| `lib.rs` | `lib.zig` | pymodule 入口、mod 声明、PyO3 注册 |
| `utils.rs` | `utils.zig` | RGBA、f32→RGBA 等工具 |
| `ansi.rs` | `ansi.zig` | ANSI 常量、TextAttributes、setLinkId/getLinkId |
| `geometry.rs` | buffer.zig 内 | ClipRect 等几何类型 |
| `cell.rs` | buffer.zig | Cell、cell_eq、cell_to_ansi_sgr |
| `buffer.rs` | `buffer.zig` | Buffer、diff、drawText、fillRect、resize 等 |
| `link.rs` | `link.zig` | LinkPool、alloc/get/incref/decref |
| `terminal.rs` | `terminal.zig` | Terminal、CursorStyle、能力、光标、标题 |
| `renderer.rs` | `renderer.zig` | CliRenderer、双缓冲、Hit Grid、dump、debug overlay |
| `text_buffer.rs` | `text_buffer.zig` | TextBuffer（ropey 封装） |
| `utf8.rs` | `utf8.zig` | 宽度、折行、字素边界等 |
| `grapheme.rs` | `grapheme.zig` | GraphemePool、字素 ID |
| `rope.rs` | `rope.zig` | Rope 适配（ropey） |
| `mem_registry.rs` | `mem_registry.zig` | MemRegistry |
| `syntax_style.rs` | `syntax_style.zig` | SyntaxStyle、主题 |
| `tests.rs` | `tests/*.zig` | 与 Zig 测试文件一一对应的子模块 |

可选/占位（未在 `lib.rs` 中声明）：`logger.rs`、`event_bus.rs`、`event_emitter.rs`、`file_logger.rs`；待实现：`text_buffer_segment.rs`、`text_buffer_iterators.rs`、`text_buffer_view.rs`、`edit_buffer.rs`、`editor_view.rs`。

## 安装 Rust 环境（可运行 `cargo test`）

在终端中执行（二选一）：

**方式一：官方 rustup（推荐）**

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

按提示选择默认安装。安装完成后**新开一个终端**或执行：

```bash
source "$HOME/.cargo/env"
```

**方式二：Homebrew（macOS）**

```bash
brew install rustup
rustup default stable
```

## 验证安装

```bash
cargo --version
rustc --version
```

## 运行 Rust 单元测试

本扩展为 PyO3 cdylib，测试二进制需链接 libpython。**必须**带 `test` feature 运行：

```bash
cd pytui/src/pytui/native   # 从 pytui 仓库根目录进入
cargo test --features test
```

若运行时报错 `Library not loaded: @rpath/libpython3.x.dylib`，请设置 `DYLD_LIBRARY_PATH` 指向当前 Python 的 lib 目录后再跑测试，例如：

```bash
# Conda 环境
export DYLD_LIBRARY_PATH="$CONDA_PREFIX/lib"
cargo test --features test

# 或指定 Python 路径（Homebrew 等）
export DYLD_LIBRARY_PATH="$(python3 -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')"
cargo test --features test
```

## 构建 Python 扩展（可选）

需要先安装 [maturin](https://github.com/PyO3/maturin)。在 **pytui 仓库根目录**（含 `pyproject.toml` 的目录）执行：

```bash
pip install maturin
maturin develop
```

即可在本地使用 `import pytui_native` 并跑 Python 测试。
