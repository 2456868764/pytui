# pytui.lib.terminal_palette - Aligns with OpenTUI lib/terminal-palette.ts
# TerminalPalette, create_terminal_palette, detect_capability, get_palette_color; TerminalColors, GetPaletteOptions

from __future__ import annotations

import os
from typing import Any, Protocol, TypedDict

ColorCapability = str

class TerminalColors(TypedDict, total=False):
    palette: list[str | None]
    defaultForeground: str | None
    defaultBackground: str | None
    cursorColor: str | None
    mouseForeground: str | None
    mouseBackground: str | None
    tekForeground: str | None
    tekBackground: str | None
    highlightBackground: str | None
    highlightForeground: str | None


class GetPaletteOptions(TypedDict, total=False):
    timeout: int
    size: int


class TerminalPaletteDetector(Protocol):
    def detect(self, options: GetPaletteOptions | None = None) -> Any: ...
    def detect_osc_support(self, timeout_ms: int | None = None) -> Any: ...
    def cleanup(self) -> None: ...


def _xterm_256_palette() -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    sixteen = [
        (0, 0, 0, 255),
        (205, 0, 0, 255),
        (0, 205, 0, 255),
        (205, 205, 0, 255),
        (0, 0, 238, 255),
        (205, 0, 205, 255),
        (0, 205, 205, 255),
        (229, 229, 229, 255),
        (76, 76, 76, 255),
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (255, 255, 0, 255),
        (92, 92, 255, 255),
        (255, 0, 255, 255),
        (0, 255, 255, 255),
        (255, 255, 255, 255),
    ]
    out.extend(sixteen)
    for r in range(6):
        for g in range(6):
            for b in range(6):
                out.append(
                    (
                        55 + r * 40 if r else 0,
                        55 + g * 40 if g else 0,
                        55 + b * 40 if b else 0,
                        255,
                    )
                )
    for i in range(24):
        v = min(8 + i * 10, 238)
        out.append((v, v, v, 255))
    return out


_XTERM_256: list[tuple[int, int, int, int]] | None = None


def get_palette_color(index: int) -> tuple[int, int, int, int]:
    """Return (r,g,b,a) for 256 palette index. Aligns OpenTUI static palette."""
    global _XTERM_256
    if _XTERM_256 is None:
        _XTERM_256 = _xterm_256_palette()
    if 0 <= index < len(_XTERM_256):
        return _XTERM_256[index]
    return (0, 0, 0, 255)


def _to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def detect_capability() -> ColorCapability:
    """Detect terminal color capability: truecolor | 256 | 16 | mono. Aligns OpenTUI."""
    color_term = os.environ.get("COLORTERM", "")
    if "truecolor" in color_term or "24bit" in color_term:
        return "truecolor"
    term = os.environ.get("TERM", "")
    if "256" in term or "xterm-256" in term.lower():
        return "256"
    if term and term != "dumb":
        return "16"
    return "mono"


class TerminalPalette:
    """Terminal palette detector. Aligns OpenTUI TerminalPalette. No TTY => static palette."""

    def __init__(
        self,
        stdin: Any = None,
        stdout: Any = None,
        write_fn: Any = None,
        in_legacy_tmux: bool = False,
    ) -> None:
        self._stdin = stdin
        self._stdout = stdout
        self._write_fn = write_fn
        self._in_legacy_tmux = in_legacy_tmux
        self._active_listeners: list[Any] = []
        self._active_timers: list[Any] = []

    def cleanup(self) -> None:
        """Remove listeners and timers. Aligns OpenTUI cleanup()."""
        self._active_listeners.clear()
        for t in self._active_timers:
            if hasattr(t, "cancel"):
                t.cancel()
        self._active_timers.clear()

    def detect_osc_support(self, timeout_ms: int = 300) -> bool:
        """Detect OSC 4 support. No TTY => False. Aligns OpenTUI detectOSCSupport()."""
        out = self._stdout
        inp = self._stdin
        if out is None or inp is None:
            return False
        if getattr(out, "isTTY", None) and getattr(inp, "isTTY", None):
            return False
        return False

    def detect(self, options: GetPaletteOptions | None = None) -> TerminalColors:
        """Return terminal colors. No OSC => static 256 palette first size entries as hex."""
        opts = options or {}
        timeout = opts.get("timeout", 5000)
        size = opts.get("size", 16)
        supported = self.detect_osc_support(timeout_ms=min(500, timeout))
        if not supported:
            global _XTERM_256
            if _XTERM_256 is None:
                _XTERM_256 = _xterm_256_palette()
            palette_list: list[str | None] = []
            for i in range(size):
                if i < len(_XTERM_256):
                    r, g, b, _ = _XTERM_256[i]
                    palette_list.append(_to_hex(r, g, b))
                else:
                    palette_list.append(None)
            return {
                "palette": palette_list,
                "defaultForeground": None,
                "defaultBackground": None,
                "cursorColor": None,
                "mouseForeground": None,
                "mouseBackground": None,
                "tekForeground": None,
                "tekBackground": None,
                "highlightBackground": None,
                "highlightForeground": None,
            }
        return {
            "palette": [None] * size,
            "defaultForeground": None,
            "defaultBackground": None,
            "cursorColor": None,
            "mouseForeground": None,
            "mouseBackground": None,
            "tekForeground": None,
            "tekBackground": None,
            "highlightBackground": None,
            "highlightForeground": None,
        }


def create_terminal_palette(
    stdin: Any = None,
    stdout: Any = None,
    write_fn: Any = None,
    is_legacy_tmux: bool = False,
) -> TerminalPaletteDetector:
    """Factory. Aligns OpenTUI createTerminalPalette()."""
    return TerminalPalette(stdin, stdout, write_fn, is_legacy_tmux)
