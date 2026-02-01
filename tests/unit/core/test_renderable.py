# tests/unit/core/test_renderable.py - Aligns with OpenTUI Renderable tests
# add/remove, requestRender, calculateLayout, render/renderSelf, findById, focus/blur, getChildren.

import pytest

pytest.importorskip("pytui.core.renderable")
pytest.importorskip("pytui.core.renderer")


class TestRenderable:
    def test_add_remove(self, mock_context):
        from pytui.core.renderable import Renderable
        from pytui.core.buffer import OptimizedBuffer

        class Dummy(Renderable):
            def render_self(self, buffer):
                pass

        root = Dummy(mock_context, {"id": "r1"})
        root.layout_node.set_width(40)
        root.layout_node.set_height(20)
        child = Dummy(mock_context, {"id": "c1"})
        child.layout_node.set_width(20)
        child.layout_node.set_height(10)
        root.add(child)
        assert len(root.children) == 1
        assert child.parent is root
        root.remove(child)
        assert len(root.children) == 0
        assert child.parent is None

    def test_request_render_bubbles(self, mock_context):
        from pytui.core.renderable import Renderable

        class Dummy(Renderable):
            def render_self(self, buffer):
                pass

        r = Dummy(mock_context)
        mock_context.renderer.schedule_render = lambda: None
        r.request_render()
        assert r._dirty

    def test_calculate_layout_recursive(self, mock_context):
        from pytui.core.renderable import Renderable
        from pytui.core.buffer import OptimizedBuffer

        class Dummy(Renderable):
            def render_self(self, buffer):
                pass

        root = Dummy(mock_context, {"id": "root", "width": 40, "height": 20})
        child = Dummy(mock_context, {"id": "c", "width": 20, "height": 10})
        root.add(child)
        root.calculate_layout()
        assert root.width == 40
        assert root.height == 20
        assert child.width == 20
        assert child.height == 10

    def test_render_calls_render_self(self, mock_context, buffer_10x5):
        from pytui.core.renderable import Renderable
        from pytui.core.buffer import OptimizedBuffer, Cell

        seen = []

        class Dummy(Renderable):
            def render_self(self, buffer):
                seen.append(True)
                buffer.set_cell(0, 0, Cell(char="X"))

        r = Dummy(mock_context, {"width": 10, "height": 5})
        r.calculate_layout()
        r.render(buffer_10x5)
        assert seen == [True]
        assert buffer_10x5.get_cell(0, 0).char == "X"

    def test_find_by_id(self, mock_context):
        from pytui.core.renderable import Renderable

        class Dummy(Renderable):
            def render_self(self, buffer):
                pass

        root = Dummy(mock_context, {"id": "root"})
        a = Dummy(mock_context, {"id": "a"})
        b = Dummy(mock_context, {"id": "b"})
        root.add(a)
        root.add(b)
        assert root.find_by_id("a") is a
        assert root.find_by_id("b") is b
        assert root.find_by_id("missing") is None

    def test_focus_blur(self, mock_context):
        from pytui.core.renderable import Renderable

        class Dummy(Renderable):
            def render_self(self, buffer):
                pass

        r = Dummy(mock_context)
        assert not r.focused
        r.focus()
        assert r.focused
        r.blur()
        assert not r.focused

    def test_get_children_returns_copy(self, mock_context):
        from pytui.core.renderable import Renderable

        class Dummy(Renderable):
            def render_self(self, buffer):
                pass

        root = Dummy(mock_context, {"id": "root"})
        child = Dummy(mock_context, {"id": "c1"})
        root.add(child)
        children = root.get_children()
        assert len(children) == 1
        assert children[0] is child
        assert children is not root.children
