# tests/unit/core/test_renderer.py

import pytest
from unittest.mock import MagicMock, patch

pytest.importorskip("pytui.core.renderer")


class TestRenderer:
    def test_construct(self):
        from pytui.core.renderer import Renderer, RootRenderable

        r = Renderer(width=40, height=20, target_fps=0)
        assert r.width == 40
        assert r.height == 20
        assert isinstance(r.root, RootRenderable)
        assert r.root.ctx.renderer is r

    def test_schedule_render(self):
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        assert not r._render_scheduled
        r.schedule_render()
        assert r._render_scheduled

    def test_render_frame_clears_and_renders(self):
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        r._render_frame()
        # After swap, front_buffer has the cleared frame
        r.front_buffer.get_cell(0, 0)
        # Should not crash; root renders nothing
        assert r._frame_count == 1

    def test_diff_and_output_no_crash(self):
        import io
        import sys
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        r._render_frame()
        old = sys.stdout
        try:
            sys.stdout = io.StringIO()
            r._diff_and_output()
        finally:
            sys.stdout = old

    def test_process_input_collects_chunk_and_processes_once(self):
        """_process_input 本帧内 select+read(1) 收集后一次 process(chunk)。"""
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        mock_buffer = MagicMock()
        mock_buffer.read.side_effect = [b"\xe4", b"\xb8", b"\xad"]
        mock_stdin = MagicMock()
        mock_stdin.buffer = mock_buffer
        with patch("pytui.core.renderer.sys.stdin", mock_stdin), patch(
            "pytui.core.renderer.select.select",
            side_effect=[
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([], [], []),
            ],
        ), patch.object(r._stdin_buffer, "process") as process_mock:
            r._process_input()
        process_mock.assert_called_once_with("\u4e2d")

    def test_process_input_collects_multibyte_chunk(self):
        """_process_input 本帧内收集多字节后一次 process。"""
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        mock_buffer = MagicMock()
        mock_buffer.read.side_effect = [
            b"\xe4", b"\xb8", b"\xad", b"\xe6", b"\x96", b"\x87",
        ]
        mock_stdin = MagicMock()
        mock_stdin.buffer = mock_buffer
        with patch("pytui.core.renderer.sys.stdin", mock_stdin), patch(
            "pytui.core.renderer.select.select",
            side_effect=[
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([mock_buffer], [], []),
                ([], [], []),
            ],
        ), patch.object(r._stdin_buffer, "process") as process_mock:
            r._process_input()
        process_mock.assert_called_once_with("\u4e2d\u6587")

    def test_process_input_no_ready_does_nothing(self):
        """_process_input select 无数据时不调用 process。"""
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        mock_buffer = MagicMock()
        mock_stdin = MagicMock()
        mock_stdin.buffer = mock_buffer
        with patch("pytui.core.renderer.sys.stdin", mock_stdin), patch(
            "pytui.core.renderer.select.select",
            side_effect=[([], [], [])],
        ), patch.object(r._stdin_buffer, "process") as process_mock:
            r._process_input()
        process_mock.assert_not_called()


class TestRendererHitTest:
    """hit_test: frontmost renderable at (x, y). Aligns OpenTUI hitTest."""

    def test_hit_test_returns_none_outside_root(self):
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        r.root.calculate_layout()
        assert r.hit_test(0, 0) is r.root
        assert r.hit_test(39, 19) is r.root
        assert r.hit_test(40, 0) is None
        assert r.hit_test(0, 20) is None
        assert r.hit_test(100, 100) is None

    def test_hit_test_returns_root_when_no_children(self):
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        r.root.calculate_layout()
        hit = r.hit_test(10, 10)
        assert hit is r.root

    def test_hit_test_returns_frontmost_child_containing_point(self):
        from pytui.components.box import Box
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        box = Box(r.context, {"id": "box", "width": 10, "height": 5})
        r.root.add(box)
        r.root.calculate_layout()
        # Point inside box (layout-dependent; typically box at 0,0 with 10x5)
        px, py = box.x + 1, box.y + 1
        assert box.x <= px < box.x + box.width and box.y <= py < box.y + box.height
        hit = r.hit_test(px, py)
        assert hit is box

    def test_hit_test_returns_deepest_child_not_parent(self):
        """Frontmost is the deepest node containing the point (e.g. Text inside Box)."""
        from pytui.components.box import Box
        from pytui.components.text import Text
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        box = Box(r.context, {"id": "box", "width": 12, "height": 3})
        text = Text(r.context, {"id": "text", "content": "x", "width": 12, "height": 1})
        box.add(text)
        r.root.add(box)
        r.root.calculate_layout()
        # Point inside text (child of box)
        px, py = text.x + 1, text.y + 0
        assert text.x <= px < text.x + text.width and text.y <= py < text.y + text.height
        hit = r.hit_test(px, py)
        assert hit is text

    def test_hit_test_returns_none_for_invisible(self):
        from pytui.components.box import Box
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0)
        box = Box(r.context, {"id": "box", "width": 10, "height": 5, "visible": False})
        r.root.add(box)
        r.root.calculate_layout()
        # Point would be inside box if visible
        px, py = box.x + 1, box.y + 1
        hit = r.hit_test(px, py)
        # Box is invisible so not hit; point falls through to root
        assert hit is r.root


class TestRendererDispatchMouse:
    """_dispatch_mouse: hit_test + process_mouse_event (bubble). Aligns OpenTUI handleMouseData + dispatchMouseEvent."""

    def test_dispatch_mouse_does_nothing_when_use_mouse_false(self):
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0, use_mouse=False)
        r.root.calculate_layout()
        with patch.object(r, "hit_test", return_value=r.root) as hit_mock:
            r._dispatch_mouse({"type": "down", "x": 5, "y": 5})
        hit_mock.assert_not_called()

    def test_dispatch_mouse_calls_process_mouse_event_on_hit_target(self):
        from pytui.components.box import Box
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0, use_mouse=True)
        box = Box(r.context, {"id": "box", "width": 10, "height": 5})
        r.root.add(box)
        r.root.calculate_layout()
        ev = {"type": "down", "x": box.x + 1, "y": box.y + 1}
        with patch.object(box, "process_mouse_event") as proc_mock:
            r._dispatch_mouse(ev)
        proc_mock.assert_called_once_with(ev)

    def test_dispatch_mouse_uses_captured_on_drag_and_up(self):
        from pytui.components.box import Box
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0, use_mouse=True)
        box = Box(r.context, {"id": "box", "width": 10, "height": 5})
        r.root.add(box)
        r.root.calculate_layout()
        ex, ey = box.x + 1, box.y + 1
        r._dispatch_mouse({"type": "down", "x": ex, "y": ey})
        assert r._mouse_captured is box
        with patch.object(box, "process_mouse_event") as proc_mock:
            r._dispatch_mouse({"type": "drag", "x": ex + 2, "y": ey})
            r._dispatch_mouse({"type": "up", "x": ex + 2, "y": ey})
        assert proc_mock.call_count == 2
        assert r._mouse_captured is None

    def test_dispatch_mouse_emits_mouse_event(self):
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0, use_mouse=True)
        r.root.calculate_layout()
        ev = {"type": "down", "x": 1, "y": 1}
        with patch.object(r.events, "emit") as emit_mock:
            r._dispatch_mouse(ev)
        emit_mock.assert_any_call("mouse", ev)

    def test_dispatch_mouse_bubbles_to_parent_via_process_mouse_event(self):
        """Hit target is child (Text); process_mouse_event bubbles so parent Box.on_mouse is called. Aligns OpenTUI processMouseEvent."""
        from pytui.components.box import Box
        from pytui.components.text import Text
        from pytui.core.renderer import Renderer

        r = Renderer(width=40, height=20, target_fps=0, use_mouse=True)
        box = Box(r.context, {"id": "box", "width": 12, "height": 3})
        text = Text(r.context, {"id": "text", "content": "x", "width": 12, "height": 1})
        box.add(text)
        r.root.add(box)
        r.root.calculate_layout()
        received = []
        box.on_mouse = lambda ev: received.append(("box", ev.get("type")))
        ev = {"type": "down", "x": text.x + 1, "y": text.y}
        r._dispatch_mouse(ev)
        assert len(received) == 1 and received[0] == ("box", "down")
