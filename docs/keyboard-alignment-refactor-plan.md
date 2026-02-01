# Keyboard 模块对齐 OpenTUI 结构 — 重构计划与执行步骤

## 目标

与 OpenTUI 结构对齐：**移除 `pytui/core/keyboard.py`**，将「StdinBuffer + KeyHandler 组合 + feed」逻辑内联到 `Renderer` 中（与 OpenTUI `renderer.ts` 一致）。

## 现状与对应关系

| 项目 | PyTUI 现状 | OpenTUI |
|------|------------|---------|
| 组合层 | `core/keyboard.py`（KeyboardHandler = StdinBuffer + KeyHandler + feed） | **无单独文件**，逻辑在 `renderer.ts` 内 |
| KeyHandler | `lib/key_handler.py`（KeyHandler, InternalKeyHandler） | `lib/KeyHandler.ts` |
| 缓冲 | `lib/stdin_buffer.py`（StdinBuffer） | `lib/stdin-buffer.ts` |
| 组装位置 | Renderer 创建 KeyboardHandler，在 `_process_input()` 里 `keyboard.feed(decoded)` | Renderer 内创建 `_keyHandler`、`_stdinBuffer`，stdin.on("data") → `_stdinBuffer.process(data)`；`_stdinBuffer.on("data", …)` 里跑 inputHandlers（含 `_keyHandler.processInput`） |

## 重构后结构（对齐 OpenTUI）

- **core**：不再包含 `keyboard.py`。
- **Renderer**：内部持有 `_key_handler`（InternalKeyHandler）、`_stdin_buffer`（StdinBuffer）；在 `_process_input()` 中向 `_stdin_buffer.process(decoded)` 喂数据；`_stdin_buffer` 的 `"data"` / `"paste"` 回调中执行 input_handlers 并调用 `_key_handler.process_input` / `process_paste`。
- **对外 API**：`renderer.keyboard` 与 `renderer.key_input` 均指向 `_key_handler`（兼容现有 `renderer.keyboard.on(...)` 等用法）；测试注入使用 `renderer.feed_input(data)`（对齐 OpenTUI 的 `renderer.stdin.emit("data", …)` 的语义）。

---

## 执行步骤

### Phase 0：准备与依赖确认

- [ ] **0.1** 确认所有引用 `core.keyboard` 或 `KeyboardHandler` 的位置（见下方「涉及文件」）。
- [ ] **0.2** 确认 `lib/stdin_buffer.StdinBuffer` 与 `lib/key_handler.InternalKeyHandler` 的 API（`process`、`on("data")`、`on("paste")`、`process_input`、`process_paste`）满足 Renderer 内联使用。

### Phase 1：Renderer 内联键盘逻辑

- [ ] **1.1** 在 `pytui/core/renderer.py` 中：
  - 删除：`from pytui.core.keyboard import KeyboardHandler`。
  - 新增：`from pytui.lib.key_handler import InternalKeyHandler`、`from pytui.lib.stdin_buffer import StdinBuffer`。
- [ ] **1.2** 在 `Renderer.__init__` 中：
  - 不再创建 `KeyboardHandler`。
  - 创建 `self._key_handler = InternalKeyHandler(use_kitty_keyboard=use_kitty_keyboard)`。
  - 创建 `self._stdin_buffer = StdinBuffer(...)`（与现 KeyboardHandler 行为一致，例如 `StdinBuffer()` 或 `StdinBuffer({"timeout": 5})` 对齐 OpenTUI）。
  - 设置 **向后兼容**：`self.keyboard = self._key_handler`。
  - 绑定：
    - `self._stdin_buffer.on("data", self._on_stdin_sequence)`
    - `self._stdin_buffer.on("paste", self._key_handler.process_paste)`
  - 保留对 keypress/keyrelease/paste 的转发：`self._key_handler.on("keypress", self._on_keypress)` 等（与现有一致）。
- [ ] **1.3** 新增 `_on_stdin_sequence(self, seq: str)`：
  - 先执行 `_input_handlers`（与 OpenTUI 一致：prepended + capability/focus + … + key handler）。
  - 若某 handler 返回 `True` 则 return。
  - 否则调用 `self._key_handler.process_input(seq)`。
- [ ] **1.4** 在 `_process_input()` 中：
  - 将 `self.keyboard.feed(decoded)` / `self.keyboard.feed(data)` 改为 `self._stdin_buffer.process(decoded)` / `self._stdin_buffer.process(data)`。
- [ ] **1.5** `key_input` 属性：
  - 保持 `return self.keyboard`（因已 `self.keyboard = self._key_handler`），或改为 `return self._key_handler`；类型注解改为 `KeyHandler` 或 `InternalKeyHandler`（从 `pytui.lib.key_handler` 导入）。
- [ ] **1.6** 清理与生命周期：
  - 在 `_cleanup()` 中调用 `self._stdin_buffer.clear()`，避免 stop 后仍有 timeout 触发。
  - 若 Renderer 已有 `destroy()`：在其中调用 `self._stdin_buffer.destroy()`（与 OpenTUI `finalizeDestroy` 一致）；若无则本阶段仅 `clear()` 即可。

### Phase 2：测试与注入 API

- [ ] **2.1** 为测试/注入输入，在 Renderer 上增加 **仅用于测试或显式注入** 的入口（与 OpenTUI 的 stdin.emit 语义对齐）：
  - 新增方法：`feed_input(self, data: str | bytes) -> None`，内部调用 `self._stdin_buffer.process(data)`。
  - 在文档或 docstring 中注明：用于测试或非交互式注入，与 OpenTUI 的 `renderer.stdin.emit("data", …)` 等价。
- [ ] **2.2** 修改 `pytui/testing/mock_keys.py`：
  - `MockKeys.feed(data)` 改为调用 `renderer.feed_input(data)`，不再使用 `renderer.keyboard.feed(data)`。

### Phase 3：core/keyboard 移除与测试调整

- [ ] **3.1** 删除 `pytui/core/keyboard.py`。
- [ ] **3.2** 重写 `tests/unit/core/test_keyboard.py`：
  - 不再依赖 `pytui.core.keyboard` 或 `KeyboardHandler`。
  - 改为测试「与 Renderer 相同的组合」：在测试内创建 `StdinBuffer` + `InternalKeyHandler`，连接 `buffer.on("data", handler.process_input)`、`buffer.on("paste", handler.process_paste)`，然后对 `buffer.process(seq)` 喂入序列，断言 `keypress`/`keyrelease`/`paste` 事件。
  - 原有用例（单字符、Ctrl、Backspace、Tab、Shift+Tab、Kitty CSI u、方向键、粘贴等）保留，仅把「KeyboardHandler + feed」换成「StdinBuffer + InternalKeyHandler + process」。
- [ ] **3.3** 若存在 `pytest.importorskip("pytui.core.keyboard")`，改为跳过条件或删除（因该模块已不存在）。

### Phase 4：其它引用与类型

- [ ] **4.1** 确认并更新类型注解：
  - `renderer.py` 中 `key_input` 的返回类型改为 `InternalKeyHandler` 或 `KeyHandler`（从 `pytui.lib.key_handler` 导入）。
- [ ] **4.2** 确认以下位置无需改代码（仅依赖 `renderer.keyboard` 的 `.on()`/`.remove_listener()`，且 `self.keyboard = self._key_handler` 已满足）：
  - `pytui/core/console.py`
  - `pytui/components/textarea.py`、`select.py`、`scrollbox.py`
  - `pytui/examples/selector_demo.py`
  - `pytui/react/reconciler.py`、`app.py`、`hooks.py`
  - `pytui/examples/lib/standalone_keys.py`
- [ ] **4.3** 确认 `pytui/core/__init__.py` 未导出 `keyboard` 或 `KeyboardHandler`（当前未导出则无需修改）。

### Phase 5：验证与文档

- [ ] **5.1** 运行全量测试：`pytest pytui/tests/ -v`（含 `tests/unit/core/test_keyboard.py`、`tests/unit/core/test_renderer.py`、使用 `mock_keys` 的测试）。
- [ ] **5.2** 运行 examples：如 `input_demo`、`select_demo`、`input_select_layout_demo`，确认 Tab/Shift+Tab、按键、粘贴行为正常。
- [ ] **5.3** 更新 `docs/core-opentui-alignment-plan.md`（若其中有 keyboard 相关条目）：注明 core 不再包含 keyboard 模块，键盘逻辑与 OpenTUI 一致内联在 Renderer 中。

---

## 涉及文件清单

| 文件 | 变更类型 |
|------|----------|
| `pytui/core/renderer.py` | 修改：内联键盘逻辑，移除 KeyboardHandler，增加 feed_input |
| `pytui/core/keyboard.py` | **删除** |
| `pytui/testing/mock_keys.py` | 修改：feed 改为调用 renderer.feed_input |
| `tests/unit/core/test_keyboard.py` | 重写：用 StdinBuffer + InternalKeyHandler 替代 KeyboardHandler |
| `pytui/core/__init__.py` | 检查：未导出 keyboard 则不改 |
| `docs/core-opentui-alignment-plan.md` | 可选：更新对齐说明 |
| `docs/keyboard-alignment-refactor-plan.md` | 本计划文档 |

无需改动的引用（仍使用 `renderer.keyboard` / `renderer.key_input`）：  
`console.py`，`textarea.py`，`select.py`，`scrollbox.py`，`selector_demo.py`，`reconciler.py`，`app.py`，`hooks.py`，`standalone_keys.py`。

---

## 风险与回退

- **风险**：依赖 `renderer.keyboard.feed()` 的第三方或内部代码会失败。  
  **缓解**：仅 Renderer 内部和 mock_keys 曾使用 feed；已改为 `feed_input()`，对外不暴露 `keyboard.feed`。
- **回退**：保留本计划与 git 历史，若有问题可恢复 `core/keyboard.py` 并从 renderer 中移除内联逻辑，恢复对 KeyboardHandler 的依赖。

---

## 完成标准

1. `pytui/core/keyboard.py` 已删除。
2. Renderer 内仅使用 `lib/key_handler.InternalKeyHandler` 与 `lib/stdin_buffer.StdinBuffer`，行为与现有一致。
3. `renderer.keyboard` 与 `renderer.key_input` 行为不变；测试通过 `renderer.feed_input()` 或 MockKeys 注入输入。
4. 全部相关单元测试与示例通过，且 `tests/unit/core/test_keyboard.py` 覆盖原有用例（StdinBuffer + KeyHandler 组合）。
