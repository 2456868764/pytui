# pytui.core.keyboard - keyboard input

import os
import sys

from pyee import EventEmitter

# Simple key parser: single char or escape sequence -> {name, char, ctrl, alt, shift}
# Supports Kitty keyboard protocol (CSI number;modifier u) for disambiguated keys.


def _kitty_mod_to_flags(mod_val: int) -> tuple[bool, bool, bool]:
    """Kitty modifier encoding: 1 + bitfield (shift=1, alt=2, ctrl=4, super=8)."""
    m = max(0, mod_val - 1)
    return bool(m & 1), bool(m & 2), bool(m & 4)  # shift, alt, ctrl


_KITTY_KEYCODE_NAME: dict[int, str] = {
    9: "tab",
    13: "enter",
    27: "escape",
    127: "backspace",
    57376: "f13",
    57377: "f14",
    57417: "left",
    57418: "right",
    57419: "up",
    57420: "down",
}


class KeyboardHandler(EventEmitter):
    """键盘输入解析，发出 keypress 事件。"""

    def __init__(self) -> None:
        super().__init__()
        self._buffer = []

    def feed(self, data: str | bytes) -> None:
        """喂入输入字节/字符，解析后 emit('keypress', key_dict)。"""
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="replace")
        for ch in data:
            self._buffer.append(ch)
        self._drain()

    def _drain(self) -> None:
        while self._buffer:
            if self._buffer[0] == "\x1b":
                # Escape sequence
                if len(self._buffer) == 1:
                    return  # wait for more
                # SS3: ESC O letter (arrow keys in keypad mode); wait for 3rd byte
                if self._buffer[1] == "O":
                    if len(self._buffer) < 3:
                        return
                    letter = self._buffer[2]
                    del self._buffer[:3]
                    ss3_map = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end", "P": "f1", "Q": "f2", "R": "f3", "S": "f4"}
                    name = ss3_map.get(letter, "unknown")
                    key = {"name": name, "char": "", "ctrl": False, "alt": False, "shift": False}
                    if os.environ.get("PYTUI_DEBUG"):
                        print(f"[pytui:keyboard] emit keypress (SS3): {key}", file=sys.stderr, flush=True)
                    self.emit("keypress", key)
                    continue
                if self._buffer[1] == "[":
                    # CSI: consume until terminator (letter, ~, or u)
                    # Mac/部分终端发 ESC [ O A 等（application cursor），需多读一字节
                    i = 2
                    while i < len(self._buffer):
                        c = self._buffer[i]
                        if c in "u~" or c.isalpha():
                            if c == "O" and i + 1 < len(self._buffer) and self._buffer[i + 1] in "ABCD":
                                i += 1  # 吞掉 O 后的 A/B/C/D，整段当作方向键
                            break
                        i += 1
                    if i >= len(self._buffer):
                        return
                    seq = "".join(self._buffer[2 : i + 1])
                    del self._buffer[: i + 1]
                    if seq.endswith("u"):
                        try:
                            body = seq[:-1].split(":")[0]
                            parts = body.split(";")
                            keycode = int(parts[0])
                            mod_val = int(parts[1]) if len(parts) > 1 else 1
                            self._emit_kitty(keycode, mod_val)
                        except (ValueError, IndexError):
                            self._emit_escape("[" + seq)
                    else:
                        if os.environ.get("PYTUI_DEBUG"):
                            print(f"[pytui:keyboard] CSI seq: [{seq!r}] -> _emit_escape", file=sys.stderr, flush=True)
                        self._emit_escape("[" + seq)
                    continue
                # Alt+char (ESC + single char, but not ESC O which is SS3)
                if len(self._buffer) >= 2:
                    ch = self._buffer[1]
                    del self._buffer[:2]
                    self.emit("keypress", {"name": ch, "char": ch, "ctrl": False, "alt": True, "shift": False})
                    continue
                return
            ch = self._buffer.pop(0)
            ctrl = False
            name = ch
            if ch == "\t":
                name = "tab"
            elif ch == "\r" or ch == "\n":
                name = "enter"
            elif ch == "\x08" or ch == "\x7f":
                # \x08 = BS, \x7f = DEL；部分终端（如 Mac）用 \x7f 表示 Backspace
                name = "backspace"
            elif ord(ch) < 32:
                ctrl = True
                name = chr(ord(ch) + 96) if 1 <= ord(ch) <= 26 else ch
            key = {"name": name, "char": ch, "ctrl": ctrl, "alt": False, "shift": False}
            if os.environ.get("PYTUI_DEBUG"):
                print(f"[pytui:keyboard] emit keypress (char): {key}", file=sys.stderr, flush=True)
            self.emit("keypress", key)

    def _emit_kitty(self, keycode: int, mod_val: int) -> None:
        shift, alt, ctrl = _kitty_mod_to_flags(mod_val)
        name = _KITTY_KEYCODE_NAME.get(keycode)
        if name is not None:
            char = "" if name in ("tab", "enter", "escape", "backspace", "up", "down", "left", "right", "home", "end", "delete", "insert", "f13", "f14") else (chr(keycode) if 32 <= keycode <= 126 else "")
            self.emit("keypress", {"name": name, "char": char, "ctrl": ctrl, "alt": alt, "shift": shift})
            return
        if 32 <= keycode <= 126:
            self.emit("keypress", {"name": chr(keycode), "char": chr(keycode), "ctrl": ctrl, "alt": alt, "shift": shift})
            return
        if 1 <= keycode <= 26:
            self.emit("keypress", {"name": chr(keycode + 96), "char": "", "ctrl": True, "alt": alt, "shift": shift})
            return
        if keycode == 0:
            self.emit("keypress", {"name": "space", "char": " ", "ctrl": ctrl, "alt": alt, "shift": shift})
            return
        self.emit("keypress", {"name": "unknown", "char": "", "ctrl": ctrl, "alt": alt, "shift": shift})

    def _emit_escape(self, seq: str) -> None:
        name_map = {
            "[A": "up",
            "[B": "down",
            "[C": "right",
            "[D": "left",
            "[H": "home",
            "[F": "end",
            "[3~": "delete",
            "[2~": "insert",
            "[5~": "page_up",
            "[6~": "page_down",
            # Mac/部分终端发 CSI O + 字母（application cursor）
            "[OA": "up",
            "[OB": "down",
            "[OC": "right",
            "[OD": "left",
        }
        # Legacy with modifier: [1;5C = ctrl+right
        if len(seq) >= 5 and seq[1:2].isdigit() and seq[2:3] == ";" and seq[3:-1].isdigit():
            try:
                mod_val = int(seq[3:-1])
                shift, alt, ctrl = _kitty_mod_to_flags(mod_val)
                legacy = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end", "P": "f1", "Q": "f2", "R": "f3", "S": "f4"}
                name = legacy.get(seq[-1], "unknown")
                self.emit("keypress", {"name": name, "char": "", "ctrl": ctrl, "alt": alt, "shift": shift})
                return
            except ValueError:
                pass
        # Shift+Tab: CSI Z (backward tab)
        if seq[1:] == "Z":
            self.emit("keypress", {"name": "tab", "char": "\t", "ctrl": False, "alt": False, "shift": True})
            return
        # Mac/某些终端发 [0A / [1A 等：数字+单字母，用最后一个字母查表
        body = seq[1:]
        if len(body) >= 1 and body[-1] in "ABCDEFHPQRS":
            name = name_map.get("[" + body[-1], "unknown")
            key = {"name": name, "char": "", "ctrl": False, "alt": False, "shift": False}
            if os.environ.get("PYTUI_DEBUG"):
                print(f"[pytui:keyboard] emit keypress (escape): {key}", file=sys.stderr, flush=True)
            self.emit("keypress", key)
            return
        name = name_map.get(seq[1:], "unknown")
        key = {"name": name, "char": "", "ctrl": False, "alt": False, "shift": False}
        if os.environ.get("PYTUI_DEBUG"):
            print(f"[pytui:keyboard] emit keypress (escape): {key}", file=sys.stderr, flush=True)
        self.emit("keypress", key)
