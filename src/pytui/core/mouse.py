# pytui.core.mouse - 鼠标事件解析

import re

from pyee import EventEmitter

# SGR 1006: \x1b[<button;x;yM (press/drag) 或 \x1b[<button;x;ym (release)
_SGR_MOUSE = re.compile(rb"^\x1b\[<(\d+);(\d+);(\d+)([Mm])")


class MouseHandler(EventEmitter):
    """解析 SGR 1006 鼠标序列，发出 mouse 事件：{x, y, button, release}。"""

    def __init__(self) -> None:
        super().__init__()
        self._buffer = bytearray()

    def feed(self, data: bytes | str) -> bytes:
        """喂入原始字节；若为鼠标序列则解析并 emit('mouse', event)，返回未消费的字节（可交给 keyboard）。"""
        if isinstance(data, str):
            data = data.encode("utf-8", errors="replace")
        self._buffer.extend(data)
        unconsumed = bytearray()
        i = 0
        while i < len(self._buffer):
            view = bytes(self._buffer[i:])
            if view.startswith(b"\x1b[<"):
                m = _SGR_MOUSE.match(view)
                if m:
                    btn = int(m.group(1))
                    x = int(m.group(2))
                    y = int(m.group(3))
                    release = m.group(4) == b"m"
                    self.emit(
                        "mouse",
                        {
                            "x": x - 1,
                            "y": y - 1,
                            "button": btn & 3 if btn < 32 else None,
                            "release": release,
                            "motion": btn >= 32,
                        },
                    )
                    i += len(m.group(0))
                    continue
                if len(view) < 12:
                    break
            unconsumed.append(self._buffer[i])
            i += 1
        del self._buffer[:i]
        return bytes(unconsumed)

    def clear(self) -> None:
        """清空未解析缓冲。"""
        self._buffer.clear()
