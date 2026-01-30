# tests.benchmarks.bench_buffer - OptimizedBuffer 性能基线

import pytest

pytest.importorskip("pytui.core.buffer")


class TestBenchBuffer:
    """Buffer set_cell/get_cell/clear/draw_text 基准。"""

    def test_set_cell_80x24(self, benchmark):
        from pytui.core.buffer import OptimizedBuffer, Cell

        buf = OptimizedBuffer(80, 24, use_native=False)
        cell = Cell(char="x", fg=(255, 255, 255, 255))

        def run():
            for y in range(24):
                for x in range(80):
                    buf.set_cell(x, y, cell)

        benchmark(run)

    def test_get_cell_80x24(self, benchmark):
        from pytui.core.buffer import OptimizedBuffer, Cell

        buf = OptimizedBuffer(80, 24, use_native=False)
        cell = Cell(char="x")
        for y in range(24):
            for x in range(80):
                buf.set_cell(x, y, cell)

        def run():
            for y in range(24):
                for x in range(80):
                    buf.get_cell(x, y)

        benchmark(run)

    def test_clear_80x24(self, benchmark):
        from pytui.core.buffer import OptimizedBuffer

        buf = OptimizedBuffer(80, 24, use_native=False)

        benchmark(buf.clear)

    def test_draw_text_80x1(self, benchmark):
        from pytui.core.buffer import OptimizedBuffer

        buf = OptimizedBuffer(80, 24, use_native=False)
        fg = (255, 255, 255, 255)

        def run():
            buf.draw_text("Hello, World!", 0, 0, fg)

        benchmark(run)
