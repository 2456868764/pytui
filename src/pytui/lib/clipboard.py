# pytui.lib.clipboard - Aligns with OpenTUI lib/clipboard.ts
# OSC 52 clipboard support; adapter-based for native ANSI generation.

from __future__ import annotations

import base64
from enum import IntEnum
from typing import Protocol


class ClipboardTarget(IntEnum):
    """Align with OpenTUI ClipboardTarget."""

    Clipboard = 0
    Primary = 1
    Secondary = 2
    Query = 3


class ClipboardAdapter(Protocol):
    """Adapter for copy/isOsc52Supported. Aligns with OpenTUI ClipboardAdapter."""

    def copy_to_clipboard(self, target: int, payload: bytes) -> bool:
        ...

    def is_osc52_supported(self) -> bool:
        ...


class Clipboard:
    """OSC 52 clipboard. Aligns with OpenTUI Clipboard."""

    def __init__(self, adapter: ClipboardAdapter) -> None:
        self._adapter = adapter

    def copy_to_clipboard_osc52(
        self,
        text: str,
        target: ClipboardTarget | int = ClipboardTarget.Clipboard,
    ) -> bool:
        """Copy text via OSC 52 (base64). Aligns with OpenTUI copyToClipboardOSC52."""
        if not self._adapter.is_osc52_supported():
            return False
        payload = base64.b64encode(text.encode("utf-8"))
        return self._adapter.copy_to_clipboard(int(target), payload)

    def clear_clipboard_osc52(
        self,
        target: ClipboardTarget | int = ClipboardTarget.Clipboard,
    ) -> bool:
        """Clear clipboard via OSC 52 (empty payload). Aligns with OpenTUI clearClipboardOSC52."""
        if not self._adapter.is_osc52_supported():
            return False
        return self._adapter.copy_to_clipboard(int(target), b"")

    def is_osc52_supported(self) -> bool:
        """Align with OpenTUI isOsc52Supported."""
        return self._adapter.is_osc52_supported()
