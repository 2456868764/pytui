# tests.benchmarks.bench_layout - Layout 计算性能基线

import pytest

pytest.importorskip("pytui.core.layout")


class TestBenchLayout:
    """LayoutNode calculate_layout / get_computed_layout 基准。"""

    def test_calculate_layout_single_node(self, benchmark):
        from pytui.core.layout import LayoutNode

        n = LayoutNode()
        n.set_width(80)
        n.set_height(24)

        def run():
            n.calculate_layout(80.0, 24.0)
            n.get_computed_layout()

        benchmark(run)

    def test_calculate_layout_tree_10_children(self, benchmark):
        from pytui.core.layout import LayoutNode

        root = LayoutNode()
        root.set_width(80)
        root.set_height(24)
        for _ in range(10):
            c = LayoutNode()
            c.set_width(78)
            c.set_height(2)
            root.add_child(c)

        def run():
            root.calculate_layout(80.0, 24.0)
            root.get_computed_layout()

        benchmark(run)
