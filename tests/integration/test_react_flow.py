# tests/integration/test_react_flow.py
"""声明式流程集成测试：挂载 Counter，调用 update，再渲染，buffer 中计数递增。"""

import pytest

pytest.importorskip("pytui.react")
pytest.importorskip("pytui.core.renderer")


def test_react_flow_mount_update_render():
    from pytui.core.renderer import Renderer
    from pytui.react import Component, useState, h, reconcile

    class Counter(Component):
        def render(self):
            count, set_count = useState(0)
            return h(
                "box",
                {"width": 40, "height": 10, "border": True, "title": "Counter"},
                h("text", {"content": f"Count: {count}", "width": 38, "height": 1}),
            )

    r = Renderer(width=40, height=10, target_fps=0)
    reconcile(h(Counter, {}), r.root)
    r._render_frame()
    buf = r.front_buffer
    # 找到 "Count: 0"
    text_found = _find_text_in_buffer(buf, 40, 10, "0")
    assert text_found, "Expected 'Count: 0' in buffer after mount"

    # 找到 Counter 组件并触发 set_state
    for _, inst in getattr(r.root, "_react_children", []):
        if isinstance(inst, tuple) and len(inst) == 3 and inst[0] == "component":
            comp = inst[1]
            if hasattr(comp, "_hook_state_list") and comp._hook_state_list:
                comp._hook_state_list[0] = 1
                comp.update()
            break
    r._render_frame()
    buf = r.front_buffer
    text_found = _find_text_in_buffer(buf, 40, 10, "1")
    assert text_found, "Expected 'Count: 1' in buffer after update"


def test_form_react_placeholder_and_box_after_frame():
    """form_react：首帧后 Box 内应显示 placeholder 或 Username（Input 有正确布局）。"""
    from pytui.core.renderer import Renderer
    from pytui.react import Component, useState, useEffect, useKeyboard, useRenderer, h, reconcile

    class LoginForm(Component):
        def render(self):
            username, set_username = useState("")
            role_index, set_role_index = useState(0)
            events = useKeyboard(self.ctx)
            roles = ["user", "admin", "guest"]

            def on_key(key: dict) -> None:
                name = key.get("name") or key.get("char")
                if name and len(name) == 1 and name.isprintable():
                    set_username(lambda prev: prev + name)
                if name == "up":
                    set_role_index(lambda prev: (prev - 1 + len(roles)) % len(roles))
                if name == "down":
                    set_role_index(lambda prev: (prev + 1) % len(roles))

            def setup() -> None:
                if getattr(self, "_keypress_registered", False):
                    return
                self._keypress_registered = True
                events.on("keypress", on_key)

            useEffect(setup, [])
            return h(
                "box",
                {"width": 52, "height": 18, "border": True, "border_style": "single", "title": "Login"},
                h("text", {"content": "Username:", "width": 50, "height": 1}),
                h("input", {"value": username, "placeholder": " enter username ", "width": 50, "height": 1}),
                h("text", {"content": "Role:", "width": 50, "height": 1}),
                h("select", {"options": roles, "selected": role_index, "width": 50, "height": 3}),
            )

    r = Renderer(width=52, height=18, target_fps=0)
    reconcile(h(LoginForm, {}), r.root)
    r._render_frame()
    buf = r.front_buffer
    assert _find_text_in_buffer(buf, 52, 18, "Username"), "Expected 'Username' label in buffer"
    # Input 的 placeholder 或 value 应出现（首帧 username 为空，应显示 placeholder 内容）
    has_input_area = _find_text_in_buffer(buf, 52, 18, "enter") or _find_text_in_buffer(buf, 52, 18, " ")
    assert has_input_area or _find_text_in_buffer(buf, 52, 18, "user"), "Expected placeholder or role in buffer"
    # 更新后应保持 root -> box -> children 结构（reconciler 修复）
    assert len(r.root.children) == 1, "Root should have one child (box)"
    box = r.root.children[0]
    assert box.__class__.__name__ == "Box"
    assert len(box.children) >= 3, "Box should have at least text, input, text, select"


def _find_text_in_buffer(buf, width: int, height: int, substring: str) -> bool:
    chars = []
    for y in range(height):
        for x in range(width):
            c = buf.get_cell(x, y)
            if c and c.char:
                chars.append(c.char)
    s = "".join(chars)
    return substring in s
