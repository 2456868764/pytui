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

    def test_process_input_decodes_multibyte_utf8(self):
        """_process_input 逐字节读并用增量 UTF-8 解码，单字多字节（如 中）能正确喂给 keyboard。"""
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        mock_buffer = MagicMock()
        # 中 = UTF-8 E4 B8 AD，逐字节读入（read(1)）
        mock_buffer.read.side_effect = [b"\xe4", b"\xb8", b"\xad", b""]
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
        ), patch.object(r.keyboard, "feed") as feed_mock:
            r._process_input()

        feed_mock.assert_called_once_with("\u4e2d")

    def test_process_input_decodes_multiple_chinese_chars(self):
        """_process_input 逐字节读时，多个中文字符能依次正确解码并喂给 keyboard。"""
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        mock_buffer = MagicMock()
        # 中文 = E4 B8 AD + E6 96 87，逐字节 read(1)
        mock_buffer.read.side_effect = [
            b"\xe4", b"\xb8", b"\xad", b"\xe6", b"\x96", b"\x87", b""
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
        ), patch.object(r.keyboard, "feed") as feed_mock:
            r._process_input()

        assert feed_mock.call_count == 2
        feed_mock.assert_any_call("\u4e2d")
        feed_mock.assert_any_call("\u6587")

    def test_process_input_decodes_ascii(self):
        """_process_input 逐字节读时，英文等 ASCII 能正确解码并喂给 keyboard。"""
        from pytui.core.renderer import Renderer

        r = Renderer(width=4, height=4, target_fps=0)
        mock_buffer = MagicMock()
        mock_buffer.read.side_effect = [b"a", b"b", b""]
        mock_stdin = MagicMock()
        mock_stdin.buffer = mock_buffer

        with patch("pytui.core.renderer.sys.stdin", mock_stdin), patch(
            "pytui.core.renderer.select.select",
            side_effect=[([mock_buffer], [], []), ([mock_buffer], [], []), ([], [], [])],
        ), patch.object(r.keyboard, "feed") as feed_mock:
            r._process_input()

        assert feed_mock.call_count == 2
        feed_mock.assert_any_call("a")
        feed_mock.assert_any_call("b")
