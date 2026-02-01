# PyTUI Examples

与 [OpenTUI packages/core/src/examples](https://github.com/opentui/opentui/tree/main/packages/core/src/examples) 对应的示例集合。仅实现可在纯 TUI 环境完成的功能；依赖 WebGL/物理引擎的示例在注册表中标注为 N/A。

## 实现计划与步骤

详见 ** [docs/examples-implementation-plan.md](../../../docs/examples-implementation-plan.md)**，包含：

- OpenTUI 全部 example 清单与分类（TUI 可实现 vs GPU/Physics 不移植）
- 阶段 0～5 的执行步骤（基础设施 → 布局与控件 → 文本与高亮 → 交互与滚动 → 组合与系统 → 入口与文档）
- 技术约定、依赖关系与验收标准

## 目录结构

```
pytui/src/pytui/examples/
├── __init__.py          # 导出 EXAMPLES, run_example, get_example_names
├── registry.py          # 示例注册表 name → (run, destroy, description)
├── lib/
│   ├── __init__.py
│   └── standalone_keys.py   # 与 OpenTUI standalone-keys.ts 等价
├── README.md            # 本文件
└── (各 demo 按计划逐步添加，如 simple_layout_example.py, input_demo.py, ...)
```

## 运行方式

- **无参数**：`python -m pytui.examples` → 启动 TUI 示例选择器（上下键选择，Enter 运行，Esc 退出）。
- **按名称**：`python -m pytui.examples simple-layout` → 直接运行指定示例；Ctrl+C 退出。

## 当前状态

- **阶段 0**：目录结构、`lib/standalone_keys.py`、统一入口 `__main__.py`、示例选择器 `selector_demo.py` 已实现。
- **阶段 1.1**：`simple_layout_example.py` 已实现（水平/垂直/居中/三列布局，Space 切换，R 重置，P 自动播放标签）。
- **阶段 1.2**：`input_demo.py` 已实现（多输入框、Tab 切换、校验、Enter 提交、状态显示）。
- **阶段 1.3**：`input_select_layout_demo.py` 已实现（Input + 双 Select 同屏，Tab 切换焦点）。
- **阶段 1.4**：`select_demo.py` 已实现（Select 列表、F/D/S/W 切换描述/滚动/换行、状态区）。
- **阶段 5**：注册表 `registry.py`、主入口、本 README 已就绪；计划文档见 `docs/examples-implementation-plan.md`。
- 其余 demo（1.5–1.7、阶段 2–4）的 `run`/`destroy` 按计划逐步实现。
