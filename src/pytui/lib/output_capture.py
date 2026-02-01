# pytui.lib.output_capture - Aligns with OpenTUI lib/output.capture.ts
# Capture (write/claim_output), CapturedWritableStream.

import io
import os
import sys
from typing import Literal

from pyee import EventEmitter

StreamName = Literal["stdout", "stderr"]


class CapturedOutput(dict):
    """Single captured chunk. Aligns with OpenTUI CapturedOutput."""
    stream: StreamName
    output: str


class Capture(EventEmitter):
    """Collects written output; write(stream, data), claim_output(). Aligns with OpenTUI Capture."""

    def __init__(self) -> None:
        super().__init__()
        self._output: list[dict] = []

    @property
    def size(self) -> int:
        """Number of captured chunks. Aligns with OpenTUI get size()."""
        return len(self._output)

    def write(self, stream: StreamName, data: str) -> None:
        """Append a chunk and emit 'write'. Aligns with OpenTUI write()."""
        self._output.append({"stream": stream, "output": data})
        self.emit("write", stream, data)

    def claim_output(self) -> str:
        """Return concatenated output and clear. Aligns with OpenTUI claimOutput()."""
        out = "".join(chunk["output"] for chunk in self._output)
        self._output.clear()
        return out

    def _clear(self) -> None:
        self._output.clear()


class CapturedWritableStream(io.TextIOBase):
    """Writable stream that forwards to Capture. Aligns with OpenTUI CapturedWritableStream."""

    def __init__(self, stream: StreamName, capture: Capture) -> None:
        self._stream = stream
        self._capture = capture
        self.isTTY = True
        try:
            cols, rows = os.get_terminal_size(sys.stdout.fileno())
            self.columns = cols
            self.rows = rows
        except Exception:
            self.columns = 80
            self.rows = 24

    def write(self, data: str) -> int:
        """Forward to capture.write(stream, data). Aligns with OpenTUI _write()."""
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="replace")
        self._capture.write(self._stream, data)
        return len(data)

    def getColorDepth(self) -> int:
        """Return color depth; 8 if unknown. Aligns with OpenTUI getColorDepth()."""
        return 8
