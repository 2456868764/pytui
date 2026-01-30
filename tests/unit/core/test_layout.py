# tests/unit/core/test_layout.py

import pytest

pytest.importorskip("pytui.core.layout")


class TestLayoutNode:
    def test_set_width_height_get_computed(self):
        from pytui.core.layout import LayoutNode

        n = LayoutNode()
        n.set_width(40)
        n.set_height(20)
        n.calculate_layout(40.0, 20.0)
        layout = n.get_computed_layout()
        assert layout["width"] == 40
        assert layout["height"] == 20
        assert "x" in layout
        assert "y" in layout

    def test_add_remove_child(self):
        from pytui.core.layout import LayoutNode

        root = LayoutNode()
        root.set_width(80)
        root.set_height(24)
        child = LayoutNode()
        child.set_width(20)
        child.set_height(10)
        root.add_child(child)
        assert len(root.children) == 1
        root.remove_child(child)
        assert len(root.children) == 0

    def test_calculate_layout_no_nan(self):
        from pytui.core.layout import LayoutNode

        n = LayoutNode()
        n.set_width(10)
        n.set_height(5)
        n.calculate_layout(10.0, 5.0)
        l = n.get_computed_layout()
        assert l["width"] >= 0
        assert l["height"] >= 0
