# tests.unit.react.test_hooks

import pytest

pytest.importorskip("pytui.react.hooks")


class TestHooks:
    def test_useState_requires_component_context(self):
        from pytui.react.hooks import useState

        with pytest.raises(RuntimeError, match="during component render"):
            useState(0)

    def test_useState_initial_and_update(self, mock_context):
        from pytui.react import Component, useState, h
        from pytui.react.reconciler import reconcile
        from pytui.core.renderer import Renderer

        class C(Component):
            def render(self):
                val, set_val = useState(10)
                return {"type": "text", "props": {"content": str(val), "width": 5, "height": 1}, "children": []}

        r = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), r.root)
        # 组件已挂载，state 应在 _hook_state_list
        for _, inst in getattr(r.root, "_react_children", []):
            if isinstance(inst, tuple) and len(inst) == 3 and inst[0] == "component":
                comp = inst[1]
                assert getattr(comp, "_hook_state_list", [])[0] == 10
                comp._hook_state_list[0] = 20
                assert comp._hook_state_list[0] == 20
                break
        else:
            pytest.fail("Counter component not found")

    def test_useState_set_value_accepts_callable(self, mock_context):
        from pytui.react import Component, useState, h
        from pytui.react.reconciler import reconcile
        from pytui.core.renderer import Renderer

        class C(Component):
            def render(self):
                val, set_val = useState(0)
                self._set_val = set_val
                return {"type": "text", "props": {"content": str(val), "width": 5, "height": 1}, "children": []}

        r = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), r.root)
        comp = None
        for _, inst in getattr(r.root, "_react_children", []):
            if isinstance(inst, tuple) and len(inst) == 3 and inst[0] == "component":
                comp = inst[1]
                break
        assert comp is not None
        assert comp._hook_state_list[0] == 0
        comp._set_val(lambda prev: (prev + 1) % 3)
        assert comp._hook_state_list[0] == 1
        comp._set_val(lambda prev: (prev + 1) % 3)
        assert comp._hook_state_list[0] == 2
        comp._set_val(lambda prev: (prev + 1) % 3)
        assert comp._hook_state_list[0] == 0

    def test_useRenderer_returns_renderer(self, mock_context):
        from pytui.react import Component, useRenderer, h
        from pytui.react.reconciler import reconcile
        from pytui.react import hooks as hooks_module
        from pytui.core.renderer import Renderer

        class C(Component):
            def render(self):
                r = useRenderer(self.ctx)
                return {"type": "text", "props": {"content": str(r is self.ctx.renderer), "width": 5, "height": 1}, "children": []}

        renderer = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), renderer.root)
        comp = None
        for _, inst in getattr(renderer.root, "_react_children", []):
            if isinstance(inst, tuple) and len(inst) >= 2 and inst[0] == "component":
                comp = inst[1]
                break
        assert comp is not None
        comp._hook_index = 0
        hooks_module._current_component = comp
        try:
            out = comp.render()
        finally:
            hooks_module._current_component = None
        assert "True" in out.get("props", {}).get("content", "")

    def test_useKeyboard_returns_events(self, mock_context):
        from pytui.react import Component, useKeyboard, h
        from pytui.react.reconciler import reconcile
        from pytui.react import hooks as hooks_module
        from pytui.core.renderer import Renderer

        class C(Component):
            def render(self):
                ev = useKeyboard(self.ctx)
                return {"type": "text", "props": {"content": str(ev is self.ctx.renderer.events), "width": 5, "height": 1}, "children": []}

        renderer = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), renderer.root)
        comp = None
        for _, inst in getattr(renderer.root, "_react_children", []):
            if isinstance(inst, tuple) and len(inst) >= 2 and inst[0] == "component":
                comp = inst[1]
                break
        assert comp is not None
        comp._hook_index = 0
        hooks_module._current_component = comp
        try:
            out = comp.render()
        finally:
            hooks_module._current_component = None
        assert "True" in out.get("props", {}).get("content", "")

    def test_useResize_returns_size_and_updates_on_resize_event(self):
        from pytui.react import Component, useResize, h
        from pytui.react.reconciler import reconcile
        from pytui.core.renderer import Renderer

        class C(Component):
            def render(self):
                size = useResize(self.ctx)
                return {
                    "type": "text",
                    "props": {"content": f"{size[0]}x{size[1]}", "width": 10, "height": 1},
                    "children": [],
                }

        renderer = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), renderer.root)
        comp = None
        for _, inst in getattr(renderer.root, "_react_children", []):
            if isinstance(inst, tuple) and len(inst) >= 2 and inst[0] == "component":
                comp = inst[1]
                break
        assert comp is not None
        assert comp._hook_state_list[0] == (20, 5)
        renderer.events.emit("resize", 30, 8)
        assert comp._hook_state_list[0] == (30, 8)

    def test_useEffect_stores_effect(self, mock_context):
        from pytui.react import Component, useState, useEffect, h
        from pytui.react.reconciler import reconcile
        from pytui.core.renderer import Renderer

        ran = []

        class C(Component):
            def render(self):
                useState(0)
                useEffect(lambda: ran.append(1), [])
                return {"type": "text", "props": {"content": "x", "width": 1, "height": 1}, "children": []}

        r = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), r.root)
        assert ran == [1]

    def test_useTimeline_returns_elapsed_and_updates_on_frame_event(self):
        import time

        from pytui.react import Component, useTimeline, h
        from pytui.react.reconciler import reconcile
        from pytui.core.renderer import Renderer

        class C(Component):
            def render(self):
                tl = useTimeline(self.ctx)
                return {
                    "type": "text",
                    "props": {"content": f"{tl['elapsed']:.1f}", "width": 10, "height": 1},
                    "children": [],
                }

        renderer = Renderer(width=20, height=5, target_fps=0)
        reconcile(h(C, {}), renderer.root)
        comp = None
        for _, inst in getattr(renderer.root, "_react_children", []):
            if isinstance(inst, tuple) and len(inst) >= 2 and inst[0] == "component":
                comp = inst[1]
                break
        assert comp is not None
        assert comp._hook_state_list[0] == 0.0
        t_future = time.time() + 1.0
        renderer.events.emit("frame", t_future)
        assert 0.9 <= comp._hook_state_list[0] <= 1.1
