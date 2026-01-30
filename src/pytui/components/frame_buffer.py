# pytui.components.frame_buffer - 全屏画布节点，持有 OptimizedBuffer


from __future__ import annotations

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable


class FrameBuffer(Renderable):
    """作为 Renderable 的全屏画布节点：持有与自身宽高一致的 OptimizedBuffer，渲染时整块复制到父 buffer。"""

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self._buffer: OptimizedBuffer | None = None
        self._buf_w = 0
        self._buf_h = 0

    def get_buffer(self) -> OptimizedBuffer | None:
        """返回内部 buffer；在 layout 确定宽高后首次 render 时创建，尺寸为 (width, height)。"""
        return self._buffer

    def _ensure_buffer(self) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        if self._buffer is None or self._buf_w != self.width or self._buf_h != self.height:
            self._buffer = OptimizedBuffer(self.width, self.height, use_native=False)
            self._buf_w = self.width
            self._buf_h = self.height
            self._buffer.clear()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        self._ensure_buffer()
        if self._buffer is None:
            return
        for dy in range(self._buffer.height):
            for dx in range(self._buffer.width):
                cell = self._buffer.get_cell(dx, dy)
                if cell is not None:
                    buffer.set_cell(self.x + dx, self.y + dy, cell)
