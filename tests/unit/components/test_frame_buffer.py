# tests/unit/components/test_frame_buffer.py

import pytest

pytest.importorskip("pytui.components.frame_buffer")


class TestFrameBuffer:
    def test_get_buffer_after_render(self, mock_context, buffer_40x20):
        from pytui.components.frame_buffer import FrameBuffer
        from pytui.core.buffer import Cell

        fb = FrameBuffer(mock_context, {"width": 5, "height": 3})
        fb.x, fb.y, fb.width, fb.height = 0, 0, 5, 3
        assert fb.get_buffer() is None
        fb.render_self(buffer_40x20)
        buf = fb.get_buffer()
        assert buf is not None
        assert buf.width == 5
        assert buf.height == 3
        buf.set_cell(0, 0, Cell(char="X", fg=(255, 255, 255, 255)))
        fb.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(0, 0).char == "X"

    def test_blits_to_parent_buffer(self, mock_context, buffer_40x20):
        from pytui.components.frame_buffer import FrameBuffer
        from pytui.core.buffer import Cell

        fb = FrameBuffer(mock_context, {"width": 4, "height": 2})
        fb.x, fb.y, fb.width, fb.height = 2, 1, 4, 2
        fb.render_self(buffer_40x20)
        inner = fb.get_buffer()
        assert inner is not None
        inner.set_cell(1, 0, Cell(char="Z"))
        fb.render_self(buffer_40x20)
        assert buffer_40x20.get_cell(2 + 1, 1 + 0).char == "Z"

    def test_frame_buffer_property_and_respect_alpha(self, mock_context):
        from pytui.components.frame_buffer import FrameBuffer

        fb = FrameBuffer(mock_context, {"width": 3, "height": 2, "respect_alpha": True})
        assert fb.respect_alpha is True
        fb.x, fb.y, fb.width, fb.height = 0, 0, 3, 2
        assert fb.frame_buffer is None
        fb.render_self(__import__("pytui.core.buffer", fromlist=["OptimizedBuffer"]).OptimizedBuffer(40, 20))
        assert fb.frame_buffer is not None
        assert fb.frame_buffer is fb.get_buffer()

    def test_on_resize_and_destroy(self, mock_context):
        from pytui.components.frame_buffer import FrameBuffer

        fb = FrameBuffer(mock_context, {"width": 5, "height": 3})
        fb.x, fb.y, fb.width, fb.height = 0, 0, 5, 3
        fb.on_resize(5, 3)
        assert fb.get_buffer() is not None
        assert fb._buf_w == 5 and fb._buf_h == 3
        fb.on_resize(6, 4)
        assert fb._buf_w == 6 and fb._buf_h == 4
        fb.destroy()
        assert fb.get_buffer() is None
        assert fb._buf_w == 0 and fb._buf_h == 0
