# PyTUI lib 与 OpenTUI lib 逐文件对齐计划

## 一、目标

1. **逐文件对齐**：`pytui/src/pytui/lib/` 下每个 Python 模块与 `opentui/packages/core/src/lib/` 中对应 TypeScript 文件一一对应（属性、功能、行为、API、测试）。
2. **命名对应**：TS 文件 `kebab-case.ts` / `PascalCase.ts` 对应 Python 文件 `snake_case.py`（如 `data-paths.ts` → `data_paths.py`，`KeyHandler.ts` → `key_handler.py`）。
3. **测试一一对应**：每个 OpenTUI `*.test.ts` 对应 PyTUI `tests/unit/lib/test_*.py`，用例名称与行为与 TS 一致。

## 二、文件映射表

| OpenTUI 文件 | PyTUI 文件 | 说明 | 状态 |
|--------------|------------|------|------|
| `index.ts` | `__init__.py` | 导出清单、顺序（与 index.ts 1–18 一致，含 get_parsers） | 已对齐 |
| `border.ts` | `border.py` | BorderChars, BorderStyle, isValidBorderStyle, parseBorderStyle, getBorderSides, getBorderFromSides, borderCharsToArray, BorderCharArrays, BorderConfig, BoxDrawOptions | 已对齐 |
| `border.test.ts` | `tests/unit/lib/test_border.py` | isValidBorderStyle, parseBorderStyle 用例 | 已补 |
| `KeyHandler.ts` | `key_handler.py` | KeyHandler, KeyEvent, PasteEvent, InternalKeyHandler, processInput, processPaste, onInternal, offInternal | 已对齐 |
| `KeyHandler.test.ts` | `tests/unit/lib/test_key_handler.py` | 单元测试 | 已补 |
| `KeyHandler.integration.test.ts` | 集成测试 | 可选 |
| `KeyHandler.stopPropagation.test.ts` | 停止冒泡测试 | 已覆盖于 test_key_handler |
| `ascii.font.ts` | `ascii_font.py` | measureText, getCharacterPositions, coordinateToCharacterIndex, fonts, font-not-found (0,0)+warn | 已对齐 |
| `hast-styled-text.ts` | `hast_styled_text.py` | HASTNode, hast_to_styled_text | 已对齐 |
| `RGBA.ts` | `rgba.py` | RGBA, hexToRgb, rgbToHex, parseColor, hsvToRgb, ColorInput, equals, toString(0-1) | 已对齐 |
| `RGBA.test.ts` | `tests/unit/core/test_rgba.py` | RGBA 用例 | 已对齐 |
| `parse.keypress.ts` | `parse_keypress.py` | parseKeypress, nonAlphanumericKeys, ParsedKey, KeyEventType | 已对齐 |
| `parse.keypress.test.ts` | `tests/unit/lib/test_parse_keypress.py` | 已补 |
| `parse.keypress-kitty.ts` | `parse_keypress_kitty.py` | parse_kitty_keyboard, KITTY_KEY_MAP | 已对齐 |
| `parse.keypress-kitty.test.ts` | `tests/unit/lib/test_parse_keypress_kitty.py` | 已补 | 已对齐 |
| `scroll-acceleration.ts` | `scroll_acceleration.py` | LinearScrollAccel, MacOSScrollAccel, tick, reset | 已对齐 |
| `stdin-buffer.ts` | `stdin_buffer.py` | StdinBuffer, process, flush, clear, getBuffer, destroy, timeout flush | 已对齐 |
| `stdin-buffer.test.ts` | `tests/unit/lib/test_stdin_buffer.py` | 已补 |
| `styled-text.ts` | `styled_text.py` | StyledText, stringToStyledText, isStyledText, createTextAttributes (strikethrough/reverse/blink) | 已对齐 |
| `yoga.options.ts` | `yoga_options.py` | parse_align, parse_flex_direction, parse_justify 等（字符串 token） | 已对齐 |
| `yoga.options.test.ts` | 可选（行为简单） | 可选 |
| `parse.mouse.ts` | `parse_mouse.py` | MouseParser, RawMouseEvent, ScrollInfo, parseMouseEvent, reset | 已对齐 |
| `selection.ts` | `selection.py` | Selection, SelectionState, ASCIIFontSelectionHelper, convertGlobalToLocalSelection | 已对齐 |
| `env.ts` | `env.py` | env, registerEnvVar, clearEnvCache, generateEnvColored, generateEnvMarkdown | 已对齐 |
| `env.test.ts` | `tests/unit/lib/test_env.py` | 已对齐 |
| `tree-sitter-styled-text.ts` | `tree_sitter_styled_text.py` | treeSitterToStyledText, treeSitterToTextChunks, ConcealOptions, OTUI_TS_STYLE_WARN | 已对齐 |
| `tree-sitter-styled-text.test.ts` | `tests/unit/lib/test_tree_sitter_styled_text.py` | 已补（dot-delimited/constructor/specificity/conceal/non-overlapping） | 已对齐 |
| `tree-sitter/index.ts` | `tree_sitter/__init__.py` | getTreeSitterClient(paths:changed→setDataPath), getParsers/get_parsers | 已对齐 |
| `tree-sitter/client.ts` | `tree_sitter/client.py` | TreeSitterClient, set_data_path, highlight_once | 已对齐 |
| `tree-sitter/client.test.ts` | `tests/unit/lib/test_tree_sitter.py` | 已补（create_buffer hasParser、remove_buffer、destroy、paths:changed） | 已对齐 |
| `tree-sitter/cache.test.ts` | `tests/unit/lib/test_tree_sitter_cache.py` | 已补（stub：clear_cache、set_data_path） | 已对齐 |
| `tree-sitter/default-parsers.ts` | `tree_sitter/parsers_config.py` | get_default_parsers, add_default_parsers | 已对齐 |
| `tree-sitter/parsers-config.ts` | 同上 | 同上 | 已对齐 |
| `tree-sitter/resolve-ft.ts` | `tree_sitter/resolve_ft.py` | path_to_filetype, ext_to_filetype | 已对齐 |
| `tree-sitter/types.ts` | `tree_sitter/types.py` | SimpleHighlight, FiletypeParserOptions 等 | 已对齐 |
| `tree-sitter/download-utils.ts` | `tree_sitter/download_utils.py` | download_or_load, download_to_path, fetch_highlight_queries, DownloadResult | 已对齐 |
| `tree-sitter/parser.worker.ts` | （无 WASM Worker） | PyTUI 由 client stub + sync_highlight 承担；接口见 types | 已对齐 |
| `data-paths.ts` | `data_paths.py` | getDataDir, getCacheDir, ensureDataDir, ensureCacheDir, getDataPaths, DataPathsManager | 已对齐 |
| `data-paths.test.ts` | `tests/unit/lib/test_data_paths.py` | 已对齐 |
| `extmarks.ts` | `extmarks.py` | ExtmarksStore, Extmark, add, remove, get, getInRange, clear | 已对齐 |
| `extmarks.test.ts` | `tests/unit/lib/test_extmarks.py` | 已对齐 |
| `extmarks-multiwidth.test.ts` | `tests/unit/lib/test_extmarks_multiwidth.py` | 已补（lib 层 display-width 用例） | 已对齐 |
| `terminal-palette.ts` | `terminal_palette.py` | TerminalPalette, createTerminalPalette, getPaletteColor, detectCapability | 已对齐 |
| `terminal-palette.test.ts` | `tests/unit/core/test_terminal_palette.py` | 已对齐 |
| `bunfs.ts` | `bunfs.py` | getBunfsRootPath, isBunfsPath, normalizeBunfsPath | 已对齐 |
| `bunfs.test.ts` | `tests/unit/lib/test_bunfs.py` | 已对齐 |
| `clipboard.ts` | `clipboard.py` | Clipboard, ClipboardTarget, copy_to_clipboard_osc52, clear_clipboard_osc52 | 已对齐 |
| `clipboard.test.ts` | `tests/unit/lib/test_clipboard.py` | 已补 | 已对齐 |
| `debounce.ts` | `debounce.py` | createDebounce, clearDebounceScope, clearAllDebounces, DebounceController | 已对齐 |
| `extmarks-history.ts` | `extmarks_history.py` | ExtmarksHistory, ExtmarksSnapshot, saveSnapshot, undo, redo, canUndo, canRedo | 已对齐 |
| `keymapping.ts` | `keymapping.py` | KeyBinding, mergeKeyBindings, buildKeyBindingsMap, keyBindingToString, defaultKeyAliases | 已对齐 |
| `keymapping.test.ts` | `tests/unit/lib/test_keymapping.py` | 已对齐 |
| `objects-in-viewport.ts` | `objects_in_viewport.py` | getObjectsInViewport, ViewportBounds, ViewportObject | 已对齐 |
| `objects-in-viewport.test.ts` | `tests/unit/lib/test_objects_in_viewport.py` | 已对齐 |
| `output.capture.ts` | `output_capture.py` | Capture, CapturedOutput, CapturedWritableStream, write, claimOutput | 已对齐 |
| `queue.ts` | `queue.py` | ProcessQueue, enqueue, clear, isProcessing, size | 已对齐 |
| `renderable.validations.ts` | `renderable_validations.py` | isDimensionType, isMarginType, validateHexColor 等 | 已对齐 |
| `renderable.validations.test.ts` | `tests/unit/lib/test_renderable_validations.py` | 已对齐 |
| `terminal-capability-detection.ts` | `terminal_capability_detection.py` | isCapabilityResponse, isPixelResolutionResponse, parsePixelResolution | 已对齐 |
| `terminal-capability-detection.test.ts` | `tests/unit/lib/test_terminal_capability_detection.py` | 已补 |
| `validate-dir-name.ts` | `validate_dir_name.py` | isValidDirectoryName | 已对齐 |

## 三、每文件对齐检查项（通用）

对每一对 TS ↔ Python 文件：

1. **属性/类型**：TS interface/type 对应 Python TypedDict/dataclass/Protocol；字段名 snake_case 与 camelCase 映射一致。
2. **API**：每个 export 函数/类在 Python 中有等价实现，签名与语义一致（参数、返回值、副作用）。
3. **行为**：边界条件、默认值、无效输入处理（如 parseBorderStyle 的 fallback、warn）与 OpenTUI 一致。
4. **测试**：每个 `test("...")` / `describe("...")` 对应 pytest 中同名或等价用例，断言行为一致。

## 四、执行顺序（按依赖）

1. **无依赖**：singleton, validate-dir-name, RGBA, border, debounce, queue, selection（基础类型）
2. **env, data-paths**：依赖 singleton / validate-dir_name
3. **parse.keypress, parse.mouse, scroll-acceleration, stdin-buffer, styled-text**
4. **keymapping, KeyHandler**
5. **extmarks, extmarks-history, terminal-palette, terminal-capability-detection**
6. **bunfs, output.capture, renderable.validations, objects-in-viewport**
7. **tree-sitter/**（client, parsers-config, resolve-ft, types）
8. **tree-sitter-styled-text**
9. **index/__init__**：最后统一导出顺序与清单

## 五、当前进度

- [x] 计划文档创建
- [x] border.ts ↔ border.py：已补全 `is_valid_border_style`、`parse_border_style`、`VALID_BORDER_STYLES`，已补 tests/unit/lib/test_border.py
- [x] KeyHandler.ts ↔ key_handler.py：InternalKeyHandler、KeyEvent 属性、_strip_ansi、process 异常处理，已补 test_key_handler.py
- [x] RGBA.ts ↔ rgba.py：toString(0-1)、equals，已对齐 test_rgba
- [x] ascii.font.ts ↔ ascii_font.py：fonts 代理、measureText 未找到字体 (0,0)+warn、getCharacterPositions 未找到 [0]
- [x] scroll-acceleration.ts ↔ scroll_acceleration.py：已对齐（LinearScrollAccel、MacOSScrollAccel）
- [x] stdin-buffer.ts ↔ stdin_buffer.py：timeout flush、_schedule_flush、clear/flush 取消 timer，已补 test_stdin_buffer.py
- [x] styled-text.ts ↔ styled_text.py：string_to_styled_text、is_styled_text、create_text_attributes(strikethrough/reverse/blink)
- [x] parse.mouse.ts ↔ parse_mouse.py：已对齐（MouseParser, RawMouseEvent, ScrollInfo）
- [x] selection.ts ↔ selection.py：已对齐
- [x] env.ts / env.test.ts ↔ env.py / test_env.py：已对齐
- [x] data-paths.ts / data-paths.test.ts ↔ data_paths.py / test_data_paths.py：已对齐
- [x] tree-sitter-styled-text.ts ↔ tree_sitter_styled_text.py：OTUI_TS_STYLE_WARN、ConcealOptions、treeSitterToTextChunks/treeSitterToStyledText，已补 test_tree_sitter_styled_text.py（dot-delimited/constructor/specificity/conceal/non-overlapping）
- [x] tree-sitter/：get_tree_sitter_client 订阅 paths:changed→set_data_path；get_parsers 别名；client、parsers_config、resolve_ft、types 已对齐
- [x] tree-sitter/client.test.ts ↔ test_tree_sitter.py：create_buffer 返回 hasParser、unsupported filetype、remove_buffer、destroy、set_data_path、paths:changed 订阅
- [x] index.ts ↔ __init__.py：__all__ 顺序与 OpenTUI index.ts 1–18 一致，tree_sitter 增加 get_parsers 导出
- [x] tree-sitter/cache.test.ts ↔ test_tree_sitter_cache.py：stub 友好用例（clear_cache、set_data_path）
- [x] extmarks-multiwidth.test.ts ↔ test_extmarks_multiwidth.py：lib 层 display-width 用例
- [x] clipboard.ts ↔ clipboard.py + test_clipboard.py：OSC 52 Clipboard、ClipboardTarget
- [x] parse.keypress-kitty.ts ↔ parse_keypress_kitty.py + test_parse_keypress_kitty.py：parse_kitty_keyboard、KITTY_KEY_MAP
- [x] yoga.options.ts ↔ yoga_options.py：parse_align、parse_flex_direction 等（字符串 token 可选实现）
- [x] hast-styled-text.ts ↔ hast_styled_text.py：HASTNode、hast_to_styled_text
- [x] tree-sitter/download-utils.ts ↔ tree_sitter/download_utils.py：download_or_load、download_to_path、fetch_highlight_queries
- [x] tree-sitter/parser.worker.ts：PyTUI 无 WASM Worker，由 client stub + sync_highlight 承担
- [ ] 其余文件按上表逐项打勾

---

执行时：每完成一对文件，在本文档「状态」列更新，并在对应 PyTUI 文件头注释中标明对齐的 OpenTUI 文件与版本/commit（可选）。
