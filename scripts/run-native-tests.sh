#!/usr/bin/env bash
# 运行 pytui native 的 Rust 单元测试。需先安装 Rust：https://rustup.rs/
# 测试需链接 libpython，请带 --features test；若报 Library not loaded，设置 DYLD_LIBRARY_PATH。

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NATIVE_DIR="$(cd "$SCRIPT_DIR/../src/pytui/native" && pwd)"

if command -v cargo &>/dev/null; then
    CARGO=cargo
elif [ -x "$HOME/.cargo/bin/cargo" ]; then
    export PATH="$HOME/.cargo/bin:$PATH"
    CARGO="$HOME/.cargo/bin/cargo"
else
    echo "未找到 cargo。请先安装 Rust："
    echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo "  然后新开终端或执行: source \"\$HOME/.cargo/env\""
    exit 1
fi

# Conda 环境下让测试二进制能找到 libpython
if [ -n "$CONDA_PREFIX" ] && [ -d "$CONDA_PREFIX/lib" ]; then
    export DYLD_LIBRARY_PATH="${DYLD_LIBRARY_PATH:+$DYLD_LIBRARY_PATH:}$CONDA_PREFIX/lib"
fi

cd "$NATIVE_DIR"
echo "Running: $CARGO test --features test (in $NATIVE_DIR)"
exec "$CARGO" test --features test
