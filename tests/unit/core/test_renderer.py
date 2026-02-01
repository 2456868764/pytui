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
