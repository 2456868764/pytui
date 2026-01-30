# pytui 示例

在项目根目录下运行（需先 `pip install -e .` 或 `conda activate pytui`）：

```bash
cd pytui
python examples/hello.py
python examples/counter.py
python examples/login_form.py
python examples/code_viewer.py
python examples/diff_viewer.py
python examples/textarea_demo.py
python examples/dashboard.py
# 声明式 API 示例（Phase 5）
python examples/hello_react.py
python examples/counter_react.py
python examples/timer_react.py
python examples/tabs_react.py
python examples/todo_react.py
python examples/dashboard_react.py
python examples/form_react.py
# Phase 7 组件与输入体验
python examples/phase7_components_react.py
python examples/scroll_accel_demo.py
# Phase 8：声明式 hooks（useRenderer/useResize/useKeyboard）、onXxx、Console overlay 见 core/console.py 与 react/hooks.py
# 调试：按任意键打印 name/char，确认方向键等解析（q 退出）
python examples/debug_keys.py

# 对应 opentui/packages/react/examples 的 demo（同样功能）
python examples/basic_react.py      # basic.tsx：登录表单 + Styled Text
python examples/counter_auto_react.py  # counter.tsx：自动递增
python examples/text_react.py       # text.tsx：Color Showcase / Span
python examples/box_react.py         # box.tsx：Box 示例
python examples/borders_react.py    # borders.tsx：四种边框
python examples/scroll_react.py     # scroll.tsx：Scrollbox + Lorem
python examples/animation_react.py  # animation.tsx：System Monitor 动画
python examples/ascii_react.py      # ascii.tsx：Select 字体 + ASCIIFont
python examples/opencode_react.py   # OpenCode 风格：Initialize Project 对话框 Yes/No
python examples/diff_react.py       # diff.tsx：Diff 视图 + 主题
python examples/extend_react.py    # extend-example.tsx：自定义组件
python examples/flush_sync_react.py # flush-sync.tsx：批量 vs 逐次更新
python examples/line_number_react.py # line-number.tsx：Code + 行号
python examples/opacity_react.py   # opacity.tsx：透明度/动画
```

| 示例 | 说明 |
|------|------|
| **hello.py** | Box + Text，最简 Hello World |
| **counter.py** | 计数器（命令式）：按空格 +1，按 q 退出 |
| **login_form.py** | 登录表单：Input（用户名/密码）+ Select（角色） |
| **code_viewer.py** | Code 组件展示 Python 代码片段（行号） |
| **diff_viewer.py** | Diff 组件对比两段文本增删改 |
| **textarea_demo.py** | Textarea 长文本，上下键滚动 |
| **dashboard.py** | 单面板仪表盘：Stats + Log 区块 |
| **hello_react.py** | 声明式 Hello：仅 h() + reconcile，无 state |
| **counter_react.py** | 声明式计数器：useState + useEffect + h() |
| **timer_react.py** | 声明式计时器：useState 存秒数，空格 +1 |
| **tabs_react.py** | 声明式标签页：TabSelect 组件 + useState，←/→ 切换 |
| **todo_react.py** | 声明式 Todo：useState 存列表，a=添加 r=删除 |
| **dashboard_react.py** | 声明式仪表盘：与 dashboard 同布局，Component + h() |
| **form_react.py** | 声明式登录表单：useState + h('input')/h('select') |
| **phase7_components_react.py** | Phase 7：TabSelect、Slider、ScrollBar、LineNumber（←/→ tab，j/k 音量，↑/↓ 滚动） |
| **scroll_accel_demo.py** | 滚动加速度：MacOSScrollAccel，连续 ↑/↓ 时步长增大 |
| **debug_keys.py** | 调试按键：按任意键打印 name/char，q 退出（方向键无响应时可先跑此脚本确认解析） |
| **basic_react.py** | 对应 basic.tsx：OpenTUI 风格登录、Tab 焦点、Enter 提交 |
| **counter_auto_react.py** | 对应 counter.tsx：每 50ms 自动 +1 |
| **text_react.py** | 对应 text.tsx：Color Showcase、Span、粗体/斜体/链接 |
| **box_react.py** | 对应 box.tsx：Box 标题/背景/内边距/嵌套 |
| **borders_react.py** | 对应 borders.tsx：single/double/rounded/heavy 边框 |
| **scroll_react.py** | 对应 scroll.tsx：Scrollbox + 多色 Lorem Box |
| **animation_react.py** | 对应 animation.tsx：useTimeline 进度条动画 |
| **ascii_react.py** | 对应 ascii.tsx：Select 选字体 + ASCIIFont |
| **opencode_react.py** | OpenCode 风格：顶部信息 + Initialize Project 对话框（Yes/No）+ 底部状态栏 |
| **diff_react.py** | 对应 diff.tsx：Diff 视图、T 主题、? 帮助 |
| **extend_react.py** | 对应 extend-example.tsx：自定义 ConsoleButton 风格 |
| **flush_sync_react.py** | 对应 flush-sync.tsx：a=批量 s=逐次 渲染 |
| **line_number_react.py** | 对应 line-number.tsx：Code + L/H/D 切换 |
| **opacity_react.py** | 对应 opacity.tsx：1-4 透明度、A 动画 |

退出：`Ctrl+C` 或示例内提示按键（如 q、←/→）。
