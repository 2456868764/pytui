#!/usr/bin/env python3
# pytui.benchmark.renderer_benchmark - Aligns with opentui/packages/core/src/benchmark/renderer-benchmark.ts
# TUI-only scenarios (no 3D): same CLI, flow, stats, results UI and JSON output.

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Ensure pytui is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pytui.core.renderer import Renderer
from pytui.core.buffer import OptimizedBuffer
from pytui.components.box import Box
from pytui.components.text import Text
from pytui.components.frame_buffer import FrameBuffer

# --- Types (align OpenTUI ScenarioResult, MemorySnapshot) ---
ScenarioResult = dict  # name, frameCount, fps, averageFrameTime, minFrameTime, maxFrameTime, stdDev, memorySnapshots?
MemorySnapshot = dict  # heapUsed, heapTotal, arrayBuffers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="renderer-benchmark",
        description="TUI renderer benchmark (aligns OpenTUI renderer-benchmark; no 3D).",
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=10000,
        metavar="ms",
        help="Duration of each scenario in milliseconds (default: 10000)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        metavar="path",
        help="Path to save benchmark results as JSON",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (show culling/stats line)",
    )
    return parser.parse_args()


# Scenario enum (align OpenTUI BenchmarkScenario)
class BenchmarkScenario:
    SingleCube = 0
    MultipleCubes = 1
    TexturedCubes = 2
    Complete = 3


TEST_CUBE_COUNT = 300
MULTIPLE_CUBES_COUNT = 8
RADIUS = 1


def main() -> None:
    options = parse_args()
    duration_ms = options.duration
    output_path = options.output
    debug = options.debug

    if output_path:
        output_path = os.path.abspath(output_path)
        if os.path.exists(output_path):
            print(f"Error: Output file already exists: {output_path}", file=sys.stderr)
            sys.exit(1)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Create renderer (align createCliRenderer with gatherStats, memorySnapshotInterval)
    renderer = Renderer(
        target_fps=60,
        exit_on_ctrl_c=True,
        gather_stats=True,
        max_stat_samples=300,
        memory_snapshot_interval=1000,
    )
    WIDTH = renderer.width
    HEIGHT = renderer.height

    # Main framebuffer (align OpenTUI fbRenderable for 3D; we use it as main draw area)
    fb_renderable = FrameBuffer(renderer.context, {"id": "main", "width": WIDTH, "height": HEIGHT, "zIndex": 10})
    renderer.root.add(fb_renderable)
    framebuffer = fb_renderable.get_buffer()

    # UI container (align OpenTUI uiContainer)
    ui_container = Box(renderer.context, {"id": "ui-container", "zIndex": 15})
    renderer.root.add(ui_container)

    benchmark_status = Text(renderer.context, {"id": "benchmark", "content": "Initializing benchmark...", "zIndex": 20})
    ui_container.add(benchmark_status)

    cube_count_status = Text(
        renderer.context,
        {"id": "cube-count", "content": f"Test cubes outside view: {TEST_CUBE_COUNT}", "position": "absolute", "left": 0, "top": 1, "zIndex": 20},
    )
    ui_container.add(cube_count_status)

    if debug:
        debug_status = Text(
            renderer.context,
            {"id": "debug", "content": "Culling: N/A (TUI)", "position": "absolute", "left": 0, "top": HEIGHT - 1, "zIndex": 20},
        )
        ui_container.add(debug_status)

    # Benchmark state (align OpenTUI)
    results: list[ScenarioResult] = []
    current_memory_snapshots: list[MemorySnapshot] = []
    benchmark_start_time: float = 0.0
    benchmark_active = True
    current_scenario = BenchmarkScenario.SingleCube
    time_acc = 0.0
    cube_boxes: list[Box] = []
    out_of_view_boxes: list[Box] = []

    def clear_previous_cubes() -> None:
        for node in cube_boxes:
            try:
                renderer.root.remove(node.id)
            except Exception:
                pass
        cube_boxes.clear()
        for node in out_of_view_boxes:
            try:
                renderer.root.remove(node.id)
            except Exception:
                pass
        out_of_view_boxes.clear()

    def update_text(text_id: str, content: str) -> None:
        child = renderer.root.find_by_id(text_id)
        if child is not None and hasattr(child, "content"):
            child.content = content

    def create_single_cube_scenario() -> None:
        update_text("benchmark", f"Running Scenario 1/3: Single Fast Cube ({duration_ms / 1000:.0f}s)")
        box = Box(renderer.context, {"id": "cube_1", "width": 20, "height": 5, "position": "absolute", "left": max(0, WIDTH // 2 - 10), "top": max(0, HEIGHT // 2 - 2), "zIndex": 12})
        renderer.root.add(box)
        cube_boxes.append(box)

    def create_multiple_cubes_scenario() -> None:
        update_text("benchmark", f"Running Scenario 2/3: Multiple Moving Cubes ({duration_ms / 1000:.0f}s)")
        import math
        for i in range(MULTIPLE_CUBES_COUNT):
            angle = (i / MULTIPLE_CUBES_COUNT) * 2 * math.pi
            x = int(WIDTH / 2 + math.cos(angle) * RADIUS * 15 - 4)
            y = int(HEIGHT / 2 + math.sin(angle) * RADIUS * 6 - 1)
            box = Box(renderer.context, {"id": f"cube_{i+1}", "width": 8, "height": 3, "position": "absolute", "left": max(0, x), "top": max(0, y), "zIndex": 12})
            renderer.root.add(box)
            cube_boxes.append(box)

    def create_textured_cubes_scenario() -> None:
        update_text("benchmark", f"Running Scenario 3/3: Heavy Layout (TUI) ({duration_ms / 1000:.0f}s)")
        import math
        for i in range(MULTIPLE_CUBES_COUNT):
            angle = (i / MULTIPLE_CUBES_COUNT) * 2 * math.pi
            x = int(WIDTH / 2 + math.cos(angle) * RADIUS * 12 - 5)
            y = int(HEIGHT / 2 + math.sin(angle) * RADIUS * 5 - 2)
            box = Box(renderer.context, {"id": f"cube_{i+1}", "width": 10, "height": 4, "position": "absolute", "left": max(0, x), "top": max(0, y), "zIndex": 12, "border": True})
            renderer.root.add(box)
            cube_boxes.append(box)

    def add_out_of_view_cubes() -> None:
        for i in range(TEST_CUBE_COUNT):
            # Place far off-screen to stress layout tree (align OpenTUI addOutOfViewCubes)
            box = Box(renderer.context, {"id": f"culling_test_cube_{i}", "width": 2, "height": 1, "position": "absolute", "left": -100 - i * 2, "top": -50, "zIndex": 1})
            renderer.root.add(box)
            out_of_view_boxes.append(box)

    def setup_scenario(scenario: int) -> None:
        clear_previous_cubes()
        current_memory_snapshots.clear()
        renderer.reset_stats()
        if scenario == BenchmarkScenario.SingleCube:
            create_single_cube_scenario()
        elif scenario == BenchmarkScenario.MultipleCubes:
            create_multiple_cubes_scenario()
        elif scenario == BenchmarkScenario.TexturedCubes:
            create_textured_cubes_scenario()
        add_out_of_view_cubes()

    def get_scenario_name(scenario: int) -> str:
        if scenario == BenchmarkScenario.SingleCube:
            return "Single Fast Cube"
        if scenario == BenchmarkScenario.MultipleCubes:
            return "Multiple Moving Cubes"
        if scenario == BenchmarkScenario.TexturedCubes:
            return "Textured Cubes with Emissive Maps"
        return "Unknown"

    def display_benchmark_results() -> None:
        results_box = Box(
            renderer.context,
            {
                "id": "results-box",
                "position": "absolute",
                "left": WIDTH // 6,
                "top": HEIGHT // 6,
                "width": (WIDTH * 2) // 3,
                "height": (HEIGHT * 2) // 3,
                "backgroundColor": (10, 10, 40, 255),
                "zIndex": 30,
            },
        )
        ui_container.add(results_box)
        left = WIDTH // 6 + 2
        y = HEIGHT // 6 + 1
        title = Text(renderer.context, {"id": "results-title", "position": "absolute", "left": left, "top": y, "content": "BENCHMARK RESULTS", "zIndex": 31})
        ui_container.add(title)
        y += 2
        for i, result in enumerate(results):
            header = Text(renderer.context, {"id": f"result-header-{i}", "position": "absolute", "left": left, "top": y, "content": f"Scenario {i+1}: {result['name']}", "zIndex": 31})
            ui_container.add(header)
            y += 1
            for line in [
                f"  Frames: {result['frameCount']} | FPS: {result['fps']}",
                f"  Frame Time: {result['averageFrameTime']:.2f}ms (min: {result['minFrameTime']:.2f}ms, max: {result['maxFrameTime']:.2f}ms)",
                f"  Standard Deviation: {result['stdDev']:.2f}ms",
            ]:
                stat = Text(renderer.context, {"id": f"result-stat-{i}", "position": "absolute", "left": left, "top": y, "content": line, "zIndex": 31})
                ui_container.add(stat)
                y += 1
            if result.get("memorySnapshots") and len(result["memorySnapshots"]) > 0:
                snap = result["memorySnapshots"]
                heap_vals = sorted(s["heapUsed"] for s in snap)
                n = len(heap_vals)
                avg_m = sum(heap_vals) / n
                min_m, max_m = heap_vals[0], heap_vals[-1]
                mid = n // 2
                median_m = (heap_vals[mid - 1] + heap_vals[mid]) / 2 if n % 2 == 0 else heap_vals[mid]
                for line in [
                    f"  Heap Used: {avg_m / 1024 / 1024:.2f}MB avg",
                    f"    (min: {min_m / 1024 / 1024:.2f}MB, max: {max_m / 1024 / 1024:.2f}MB, median: {median_m / 1024 / 1024:.2f}MB)",
                ]:
                    mem_stat = Text(renderer.context, {"id": f"result-mem-{i}", "position": "absolute", "left": left, "top": y, "content": line, "zIndex": 31})
                    ui_container.add(mem_stat)
                    y += 1
            y += 1
        if len(results) > 1:
            comp_title = Text(renderer.context, {"id": "results-comparison", "position": "absolute", "left": left, "top": y, "content": "Performance Comparison:", "zIndex": 31})
            ui_container.add(comp_title)
            y += 1
            for i in range(1, len(results)):
                base_perf = results[0]["averageFrameTime"]
                cur_perf = results[i]["averageFrameTime"]
                ratio = cur_perf / base_perf if base_perf else 0
                pct = (ratio - 1) * 100
                sign = "+" if ratio > 1 else ""
                comp = Text(renderer.context, {"id": f"result-compare-{i}", "position": "absolute", "left": left, "top": y, "content": f"  {results[i]['name']}: {sign}{pct:.1f}% frame time vs. baseline", "zIndex": 31})
                ui_container.add(comp)
                y += 1
        footer = Text(renderer.context, {"id": "results-footer", "position": "absolute", "left": left, "top": (HEIGHT * 5) // 6 - 2, "content": "Press Ctrl+C to exit", "zIndex": 31})
        ui_container.add(footer)

        if output_path:
            try:
                json_results = {
                    "date": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                    "scenarios": results,
                    "comparison": [
                        {"name": results[i]["name"], "ratio": results[i]["averageFrameTime"] / results[0]["averageFrameTime"] if results[0]["averageFrameTime"] else 0, "percentDifference": (results[i]["averageFrameTime"] / results[0]["averageFrameTime"] - 1) * 100 if results[0]["averageFrameTime"] else 0}
                        for i in range(1, len(results))
                    ],
                }
                # Strip memorySnapshots for JSON (large); add memoryStats if present
                for r in json_results["scenarios"]:
                    if "memorySnapshots" in r and r["memorySnapshots"]:
                        snap = r["memorySnapshots"]
                        heap_vals = sorted(s["heapUsed"] for s in snap)
                        n = len(heap_vals)
                        r["memoryStats"] = {
                            "averageHeapUsedMB": sum(heap_vals) / n / 1024 / 1024,
                            "minHeapUsedMB": heap_vals[0] / 1024 / 1024,
                            "maxHeapUsedMB": heap_vals[-1] / 1024 / 1024,
                        }
                    if "memorySnapshots" in r:
                        del r["memorySnapshots"]
                with open(output_path, "w") as f:
                    json.dump(json_results, f, indent=2)
            except Exception as e:
                print(f"Error saving results to {output_path}: {e}", file=sys.stderr)

    # Frame callback (align OpenTUI setFrameCallback)
    def on_frame(delta_ms: float) -> None:
        nonlocal time_acc, benchmark_start_time, current_scenario, benchmark_active
        delta_sec = delta_ms / 1000.0
        if benchmark_start_time == 0:
            benchmark_start_time = time.time()
            renderer.reset_stats()
        time_acc += delta_sec
        elapsed_ms = (time.time() - benchmark_start_time) * 1000

        # Update scenario animation (TUI: request render)
        renderer.request_render()

        if benchmark_active and elapsed_ms >= duration_ms:
            stats = renderer.get_stats()
            frame_times = stats.get("frameTimes", [])
            std_dev = 0.0
            if frame_times:
                avg = stats["averageFrameTime"]
                variance = sum((t - avg) ** 2 for t in frame_times) / len(frame_times)
                std_dev = variance ** 0.5
            results.append({
                "name": get_scenario_name(current_scenario),
                "frameCount": stats.get("frameCount", 0),
                "fps": stats.get("fps", 0),
                "averageFrameTime": stats.get("averageFrameTime", 0),
                "minFrameTime": stats.get("minFrameTime", 0),
                "maxFrameTime": stats.get("maxFrameTime", 0),
                "stdDev": std_dev,
                "memorySnapshots": list(current_memory_snapshots),
            })
            current_scenario += 1
            if current_scenario < BenchmarkScenario.Complete:
                setup_scenario(current_scenario)
                benchmark_start_time = time.time()
            else:
                benchmark_active = False
                display_benchmark_results()
                renderer.pause()

    renderer.set_frame_callback(on_frame)
    renderer.events.on("memory:snapshot", lambda snap: current_memory_snapshots.append(snap) if benchmark_active else None)
    def on_resize(w: int, h: int) -> None:
        fb_renderable.on_resize(w, h)

    renderer.events.on("resize", on_resize)

    setup_scenario(current_scenario)
    renderer.start()


if __name__ == "__main__":
    main()
