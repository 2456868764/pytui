# PyTUI Benchmark

与 [OpenTUI packages/core/src/benchmark](https://github.com/opentui/opentui/tree/main/packages/core/src/benchmark) 对应：同一套 CLI、流程、统计与结果展示（含 JSON 输出），场景为 TUI 渲染（无 3D/WebGPU）。

## 运行

在项目根目录或 `pytui` 包可被导入的环境下：

```bash
python -m pytui.benchmark.renderer_benchmark -d 5000 -o results.json
```

或在 `pytui/src/pytui` 下：

```bash
python benchmark/renderer_benchmark.py -d 5000 -o results.json
```

## 选项（与 OpenTUI 对齐）

- **-d, --duration \<ms\>**：每个场景运行时长（毫秒），默认 10000
- **-o, --output \<path\>**：将结果写入 JSON 文件
- **--debug**：显示调试行（如 Culling 状态，TUI 下为 N/A）

## 场景（TUI 对应）

1. **Single Fast Cube**：单个 Box，模拟单物体压力
2. **Multiple Moving Cubes**：8 个 Box 环形排布
3. **Textured Cubes / Heavy Layout**：8 个带边框 Box（无纹理，用“重布局”等效）

每轮会额外添加 300 个“视口外” Box 以增加布局/树压力（对应 OpenTUI 的 addOutOfViewCubes）。

## Renderer 扩展（为 benchmark 增加）

- `gather_stats`, `max_stat_samples`, `memory_snapshot_interval` 构造参数
- `set_frame_callback(cb)`：每帧调用 `cb(delta_ms)`
- `get_stats()`：返回 fps, frameCount, frameTimes, averageFrameTime, minFrameTime, maxFrameTime
- `reset_stats()`：清空帧时间与统计帧数
- `pause()`：等同 `stop()`
- `events.emit("memory:snapshot", { heapUsed, heapTotal, arrayBuffers })`：当 `memory_snapshot_interval > 0` 时按间隔发出
