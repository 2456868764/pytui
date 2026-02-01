# pytui.lib.stdin_buffer - Aligns with OpenTUI lib/stdin-buffer.ts
# StdinBuffer: process(data), flush(), clear(), getBuffer(), destroy(); emit 'data', 'paste'; timeout flush.

from __future__ import annotations

import re
import threading
from typing import Literal

from pyee import EventEmitter

ESC = "\x1b"
BRACKETED_PASTE_START = "\x1b[200~"
BRACKETED_PASTE_END = "\x1b[201~"


def _is_complete_sequence(data: str) -> Literal["complete", "incomplete", "not-escape"]:
    """Check if string is a complete escape sequence. Aligns OpenTUI isCompleteSequence."""
    if not data.startswith(ESC):
        return "not-escape"
    if len(data) == 1:
        return "incomplete"
    after = data[1:]
    if after.startswith("["):
        if after.startswith("[M"):
            return "complete" if len(data) >= 6 else "incomplete"
        return _is_complete_csi(data)
    if after.startswith("]"):
        return "complete" if (ESC + "\\" in data or "\x07" in data) else "incomplete"
    if after.startswith("P"):
        return "complete" if (ESC + "\\" in data) else "incomplete"
    if after.startswith("_"):
        return "complete" if (ESC + "\\" in data) else "incomplete"
    if after.startswith("O"):
        return "complete" if len(after) >= 2 else "incomplete"
    if len(after) == 1:
        return "complete"
    return "complete"


def _is_complete_csi(data: str) -> Literal["complete", "incomplete"]:
    """CSI: ESC [ ... ends with 0x40-0x7E."""
    if not data.startswith(ESC + "["):
        return "complete"
    if len(data) < 3:
        return "incomplete"
    payload = data[2:]
    last_code = ord(payload[-1])
    if 0x40 <= last_code <= 0x7E:
        if payload.startswith("O"):
            # SS3: ESC O + single letter (need 2 chars after ESC)
            return "complete" if len(payload) >= 2 else "incomplete"
        if payload.startswith("<") and (payload.endswith("M") or payload.endswith("m")):
            if re.match(r"^<\d+;\d+;\d+[Mm]$", payload):
                return "complete"
            parts = payload[1:-1].split(";")
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                return "complete"
            return "incomplete"
        return "complete"
    return "incomplete"


def _extract_complete_sequences(buffer: str) -> tuple[list[str], str]:
    """Split buffer into complete sequences and remainder. Aligns OpenTUI extractCompleteSequences."""
    sequences: list[str] = []
    pos = 0
    while pos < len(buffer):
        remaining = buffer[pos:]
        if remaining.startswith(ESC):
            seq_end = 1
            while seq_end <= len(remaining):
                candidate = remaining[:seq_end]
                status = _is_complete_sequence(candidate)
                if status == "complete":
                    sequences.append(candidate)
                    pos += seq_end
                    break
                if status == "incomplete":
                    seq_end += 1
                else:
                    sequences.append(candidate)
                    pos += seq_end
                    break
            else:
                return sequences, remaining
        else:
            sequences.append(remaining[0])
            pos += 1
    return sequences, ""


class StdinBuffer(EventEmitter):
    """Buffer stdin and emit complete sequences via 'data'; bracketed paste via 'paste'. Aligns OpenTUI StdinBuffer."""

    def __init__(self, options: dict | None = None) -> None:
        super().__init__()
        opts = options or {}
        self._timeout_ms = opts.get("timeout", 10)
        self._timeout_incomplete_ms = opts.get("timeout_incomplete", 2000)
        self._buffer = ""
        self._paste_mode = False
        self._paste_buffer = ""
        self._timeout_handle: threading.Timer | None = None

    def process(self, data: str | bytes) -> None:
        """Feed input; emit 'data' for each complete sequence, 'paste' for bracketed paste. Aligns OpenTUI process()."""
        # Clear any pending timeout first (align OpenTUI) so timer cannot fire and flush partial buffer while we append.
        if self._timeout_handle:
            self._timeout_handle.cancel()
            self._timeout_handle = None
        if isinstance(data, bytes):
            if len(data) == 1 and data[0] > 127:
                s = ESC + chr(data[0] - 128)
            else:
                s = data.decode("utf-8", errors="replace")
        else:
            s = data
        if not s and not self._buffer:
            self.emit("data", "")  # type: ignore[arg-type]
            return
        self._buffer += s
        if self._paste_mode:
            self._paste_buffer += self._buffer
            self._buffer = ""
            idx = self._paste_buffer.find(BRACKETED_PASTE_END)
            if idx != -1:
                content = self._paste_buffer[:idx]
                rest = self._paste_buffer[idx + len(BRACKETED_PASTE_END) :]
                self._paste_mode = False
                self._paste_buffer = ""
                self.emit("paste", content)  # type: ignore[arg-type]
                if rest:
                    self.process(rest)
            return
        start_idx = self._buffer.find(BRACKETED_PASTE_START)
        if start_idx != -1:
            before = self._buffer[:start_idx]
            seqs, _ = _extract_complete_sequences(before)
            for seq in seqs:
                self.emit("data", seq)  # type: ignore[arg-type]
            self._buffer = self._buffer[start_idx + len(BRACKETED_PASTE_START) :]
            self._paste_mode = True
            self._paste_buffer = self._buffer
            self._buffer = ""
            idx = self._paste_buffer.find(BRACKETED_PASTE_END)
            if idx != -1:
                content = self._paste_buffer[:idx]
                rest = self._paste_buffer[idx + len(BRACKETED_PASTE_END) :]
                self._paste_mode = False
                self._paste_buffer = ""
                self.emit("paste", content)  # type: ignore[arg-type]
                if rest:
                    self.process(rest)
            return
        seqs, remainder = _extract_complete_sequences(self._buffer)
        self._buffer = remainder
        for seq in seqs:
            self.emit("data", seq)  # type: ignore[arg-type]
        if self._buffer:
            self._schedule_flush()

    def _schedule_flush(self) -> None:
        """Schedule flush after timeout. Single ESC: short timeout; incomplete CSI (\x1b[, \x1b[1;...): long timeout."""
        if self._timeout_handle:
            self._timeout_handle.cancel()
        ms = self._timeout_ms if self._buffer == ESC else self._timeout_incomplete_ms
        def _run() -> None:
            self._timeout_handle = None
            flushed = self.flush()
            for seq in flushed:
                self.emit("data", seq)  # type: ignore[arg-type]
        self._timeout_handle = threading.Timer(ms / 1000.0, _run)
        self._timeout_handle.daemon = True
        self._timeout_handle.start()

    def flush(self) -> list[str]:
        """Flush buffer and return pending as list. Aligns OpenTUI flush()."""
        if self._timeout_handle:
            self._timeout_handle.cancel()
            self._timeout_handle = None
        if not self._buffer:
            return []
        out = [self._buffer]
        self._buffer = ""
        return out

    def clear(self) -> None:
        """Clear buffer and paste state. Aligns OpenTUI clear()."""
        if self._timeout_handle:
            self._timeout_handle.cancel()
            self._timeout_handle = None
        self._buffer = ""
        self._paste_mode = False
        self._paste_buffer = ""

    def get_buffer(self) -> str:
        """Return current buffer. Aligns OpenTUI getBuffer()."""
        return self._buffer

    def destroy(self) -> None:
        """Aligns OpenTUI destroy()."""
        self.clear()
