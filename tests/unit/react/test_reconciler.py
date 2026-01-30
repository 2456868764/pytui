# tests.unit.react.test_reconciler

import pytest
from unittest.mock import MagicMock, patch

pytest.importorskip("pytui.react.reconciler")


class TestReconciler:
    def test_mount_host_tree(self, mock_context):
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(
            h("box", {"width": 40, "height": 20, "border": True}, h("text", {"content": "Hello", "width": 38, "height": 1})),
            r.root,
        )
        assert len(r.root.children) == 1
        box = r.root.children[0]
        assert box.__class__.__name__ == "Box"
        assert len(box.children) == 1
        text = box.children[0]
        assert text.__class__.__name__ == "Text"
        assert text.content == "Hello"

    def test_mount_component_tree(self, mock_context):
        from pytui.core.renderer import Renderer
        from pytui.react import Component, useState, h, reconcile

        class C(Component):
            def render(self):
                x, _ = useState(7)
                return h("text", {"content": str(x), "width": 10, "height": 1})

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h(C, {}), r.root)
        assert len(r.root.children) == 1
        text = r.root.children[0]
        assert text.content == "7"

    def test_reconcile_replaces_children(self, mock_context):
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h("text", {"content": "A", "width": 10, "height": 1}), r.root)
        assert len(r.root.children) == 1
        assert r.root.children[0].content == "A"
        reconcile(h("text", {"content": "B", "width": 10, "height": 1}), r.root)
        assert len(r.root.children) == 1
        assert r.root.children[0].content == "B"

    def test_unmount_removes_from_container(self, mock_context):
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h("text", {"content": "X", "width": 10, "height": 1}), r.root)
        assert len(r.root.children) == 1
        reconcile([], r.root)
        assert len(r.root.children) == 0

    def test_mount_ascii_font_via_h(self, mock_context):
        """Phase 11: ascii_font 可通过 h() 挂载。"""
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h("ascii_font", {"text": "Hi", "font": "tiny"}), r.root)
        assert len(r.root.children) == 1
        af = r.root.children[0]
        assert af.__class__.__name__ == "ASCIIFont"
        assert af._text == "Hi"

    def test_mount_text_node_via_h(self, mock_context):
        """Phase 10: text_node 可通过 h() 挂载。"""
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h("text_node", {"content": "Hi", "width": 10, "height": 1}), r.root)
        assert len(r.root.children) == 1
        node = r.root.children[0]
        assert node.__class__.__name__ == "TextNode"
        assert len(node._spans) == 1
        assert node._spans[0].text == "Hi"

    def test_mount_phase7_components_via_h(self, mock_context):
        """Phase 7: tab_select, slider, scrollbar, line_number 可通过 h() 挂载。"""
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        tree = h(
            "box",
            {"width": 40, "height": 20},
            h("tab_select", {"tabs": ["A", "B"], "width": 20, "height": 1}),
            h("slider", {"min": 0, "max": 100, "value": 50, "width": 20, "height": 1}),
            h("scrollbar", {"scroll_max": 10, "scroll_value": 0, "width": 1, "height": 5}),
            h("line_number", {"line_count": 10, "scroll_offset": 0, "width": 4, "height": 5}),
        )
        reconcile(tree, r.root)
        box = r.root.children[0]
        assert box.__class__.__name__ == "Box"
        assert len(box.children) == 4
        assert box.children[0].__class__.__name__ == "TabSelect"
        assert box.children[0].selected == "A"
        assert box.children[1].__class__.__name__ == "Slider"
        assert box.children[1].value == 50
        assert box.children[2].__class__.__name__ == "ScrollBar"
        assert box.children[2].scroll_value == 0
        assert box.children[3].__class__.__name__ == "LineNumber"
        assert box.children[3].line_count == 10

    def test_on_select_binding(self, mock_context):
        """Phase 8.2: onSelect 挂载时绑定到 Select 的 select 事件。"""
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile

        r = Renderer(width=40, height=20, target_fps=0)
        calls = []

        def on_select(index: int, name: str, value: str) -> None:
            calls.append((index, name, value))

        reconcile(
            h("select", {"options": ["a", "b", "c"], "selected": 0, "width": 10, "height": 3, "onSelect": on_select}),
            r.root,
        )
        assert len(r.root.children) == 1
        sel = r.root.children[0]
        assert sel.__class__.__name__ == "Select"
        sel.select_next()
        assert calls == [(1, "b", "b")]
        sel.select_next()
        assert len(calls) == 2
        assert calls[1] == (2, "c", "c")

    def test_unmount_calls_blur_on_focused_host(self, mock_context):
        """组件更新时卸载旧 host 会调用 blur()，避免 keypress 监听器累积。"""
        from pytui.core.renderer import Renderer
        from pytui.react import h, reconcile
        from pytui.react.reconciler import _unmount

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h("input", {"width": 10, "height": 1, "focused": True}), r.root)
        parent = r.root
        host = parent.children[0]
        assert host.focused
        inst = ({"type": "input", "props": {}}, host)
        with patch.object(host, "blur", wraps=host.blur) as blur_spy:
            _unmount(inst, parent)
        blur_spy.assert_called_once()
        assert host not in parent.children

    def test_update_component_output_unmounts_old_children_on_state_update(self, mock_context):
        """组件 setState 重渲染时 _update_component_output 会先卸载旧子节点（调用 _unmount）。"""
        from pytui.core.renderer import Renderer
        from pytui.react import Component, useState, h, reconcile

        class C(Component):
            def render(self):
                s, set_s = useState(0)
                if not hasattr(self, "_setter"):
                    self._setter = set_s
                return h("box", {"width": 40, "height": 20}, h("input", {"width": 10, "height": 1}))

        r = Renderer(width=40, height=20, target_fps=0)
        reconcile(h(C, {}), r.root)
        comp = r.root._react_children[0][1][1]
        old_child_insts = list(comp._react_child_insts)

        with patch("pytui.react.reconciler._unmount", wraps=lambda *a: None) as mock_unmount:
            comp._setter(1)

        mock_unmount.assert_called()
        # 应使用旧的 old_child_insts 调用 _unmount(inst, parent)
        calls = [c for c in mock_unmount.call_args_list if len(c[0]) >= 2]
        assert len(calls) >= 1
        # 第一次调用应为 (old_inst, parent)
        first_inst = calls[0][0][0]
        assert first_inst is old_child_insts[0][1]
