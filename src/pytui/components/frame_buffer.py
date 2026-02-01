# pytui.components.frame_buffer - FrameBuffer renderable; aligns with OpenTUI FrameBufferRenderable (FrameBuffer.ts).

from __future__ import annotations

from pytui.core.buffer import OptimizedBuffer
from pytui.core.renderable import Renderable


class FrameBuffer(Renderable):
    """FrameBuffer renderable: holds OptimizedBuffer of (width, height); render copies to parent buffer.
    Aligns with OpenTUI FrameBufferRenderable: frameBuffer, respectAlpha, onResize, destroy.
    """

    def __init__(self, ctx, options: dict | None = None):
        options = options or {}
        super().__init__(ctx, options)
        self._buffer: OptimizedBuffer | None = None
        self._buf_w = 0
        self._buf_h = 0
        self.respect_alpha = options.get("respect_alpha", options.get("respectAlpha", False))

    @property
    def frame_buffer(self) -> OptimizedBuffer | None:
        """Align with OpenTUI frameBuffer. Same as get_buffer()."""
        return self._buffer

    def get_buffer(self) -> OptimizedBuffer | None:
        """Return internal buffer; created on first render when layout has set width/height."""
        return self._buffer

    def on_resize(self, width: int, height: int) -> None:
        """Align with OpenTUI onResize(width, height). Recreate internal buffer when size changes; no-op if <= 0."""
        if width <= 0 or height <= 0:
            return
        if self._buffer is None or self._buf_w != width or self._buf_h != height:
            self._buf_w, self._buf_h = width, height
            self._buffer = OptimizedBuffer(width, height, use_native=False)
            self._buffer.clear()
        self.request_render()

    def destroy(self) -> None:
        """Align with OpenTUI destroySelf(): release internal frame buffer."""
        self._buffer = None
        self._buf_w = self._buf_h = 0

    def _ensure_buffer(self) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        if self._buffer is None or self._buf_w != self.width or self._buf_h != self.height:
            self._buffer = OptimizedBuffer(self.width, self.height, use_native=False)
            self._buf_w = self.width
            self._buf_h = self.height
            self._buffer.clear()

    def render_self(self, buffer: OptimizedBuffer) -> None:
        if not self.visible:
            return
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
