# pytui.lib.parse_keypress - Aligns with OpenTUI lib/parse.keypress.ts
# parse_keypress(s, options) -> ParsedKey | None; KeyEventType, ParsedKey

from __future__ import annotations

import re
from typing import Literal, TypedDict

KeyEventType = Literal["press", "repeat", "release"]


class ParsedKey(TypedDict, total=False):
    name: str
    ctrl: bool
    meta: bool
    shift: bool
    option: bool
    sequence: str
    number: bool
    raw: str
    eventType: KeyEventType
    source: Literal["raw", "kitty"]
    code: str
    super: bool
    hyper: bool
    capsLock: bool
    numLock: bool
    baseCode: int
    repeated: bool
    char: str  # pytui compat


# OpenTUI keyName map (subset for common keys)
_KEY_NAME: dict[str, str] = {
    "OP": "f1", "OQ": "f2", "OR": "f3", "OS": "f4",
    "[11~": "f1", "[12~": "f2", "[13~": "f3", "[14~": "f4",
    "[[A": "f1", "[[B": "f2", "[[C": "f3", "[[D": "f4", "[[E": "f5",
    "[15~": "f5", "[17~": "f6", "[18~": "f7", "[19~": "f8", "[20~": "f9", "[21~": "f10", "[23~": "f11", "[24~": "f12",
    "[A": "up", "[B": "down", "[C": "right", "[D": "left", "[E": "clear", "[F": "end", "[H": "home",
    "OA": "up", "OB": "down", "OC": "right", "OD": "left", "OE": "clear", "OF": "end", "OH": "home",
    "[1~": "home", "[2~": "insert", "[3~": "delete", "[4~": "end", "[5~": "pageup", "[6~": "pagedown",
    "[[5~": "pageup", "[[6~": "pagedown", "[7~": "home", "[8~": "end",
    "[a": "up", "[b": "down", "[c": "right", "[d": "left", "[e": "clear",
    "f": "right", "b": "left", "p": "up", "n": "down",
    "[2$": "insert", "[3$": "delete", "[5$": "pageup", "[6$": "pagedown", "[7$": "home", "[8$": "end",
    "Oa": "up", "Ob": "down", "Oc": "right", "Od": "left", "Oe": "clear",
    "[2^": "insert", "[3^": "delete", "[5^": "pageup", "[6^": "pagedown", "[7^": "home", "[8^": "end",
    "[Z": "tab",
}

# Aligns OpenTUI nonAlphanumericKeys: key names that are not alphanumeric
non_alphanumeric_keys: tuple[str, ...] = tuple(_KEY_NAME.values()) + ("backspace",)

_META_KEY_RE = re.compile(r"^\x1b([a-zA-Z0-9])$")
_FN_KEY_RE = re.compile(r"^(?:\x1b+)(O|N|\[|\[\[)(?:(\d+)(?:;(\d+))?([~^$])|(?:1;)?(\d+)?([a-zA-Z]))")
_MODIFY_OTHER_KEYS_RE = re.compile(r"^\x1b\[27;(\d+);(\d+)~$")

_SHIFT_CODES = frozenset(("[a", "[b", "[c", "[d", "[e", "[2$", "[3$", "[5$", "[6$", "[7$", "[8$", "[Z"))
_CTRL_CODES = frozenset(("Oa", "Ob", "Oc", "Od", "Oe", "[2^", "[3^", "[5^", "[6^", "[7^", "[8^"))


def _is_shift_key(code: str) -> bool:
    return code in _SHIFT_CODES


def _is_ctrl_key(code: str) -> bool:
    return code in _CTRL_CODES


def parse_keypress(
    s: str | bytes = "",
    options: dict | None = None,
) -> ParsedKey | None:
    """Parse key sequence to ParsedKey. Aligns OpenTUI parseKeypress(). Returns None for mouse/terminal responses/paste markers."""
    opts = options or {}
    use_kitty = opts.get("use_kitty_keyboard", opts.get("useKittyKeyboard", False))

    if isinstance(s, bytes):
        if len(s) == 1 and s[0] > 127:
            s = "\x1b" + chr(s[0] - 128)
        else:
            s = s.decode("utf-8", errors="replace")
    else:
        s = str(s) if s is not None else ""

    # Filter mouse
    if re.match(r"^\x1b\[<\d+;\d+;\d+[Mm]$", s):
        return None
    if s.startswith("\x1b[M") and len(s) >= 6:
        return None
    # Filter terminal responses
    if re.match(r"^\x1b\[\d+;\d+;\d+t$", s):
        return None
    if re.match(r"^\x1b\[\d+;\d+R$", s):
        return None
    if re.match(r"^\x1b\[\?[\d;]+c$", s):
        return None
    if re.match(r"^\x1b\[\?[\d;]+\$y$", s):
        return None
    if s in ("\x1b[I", "\x1b[O"):
        return None
    if re.match(r"^\x1b\][\d;].*(\x1b\\|\x07)$", s):
        return None
    if s in ("\x1b[200~", "\x1b[201~"):
        return None

    key: ParsedKey = {
        "name": "",
        "ctrl": False,
        "meta": False,
        "shift": False,
        "option": False,
        "number": False,
        "sequence": s,
        "raw": s,
        "eventType": "press",
        "source": "raw",
    }

    # Kitty CSI u: ESC [ code ; modifier u (always parse when format matches)
    if re.match(r"^\x1b\[\d+;\d+u$", s):
        kitty = _parse_kitty_keyboard(s)
        if kitty is not None:
            return kitty
    if use_kitty:
        kitty = _parse_kitty_keyboard(s)
        if kitty is not None:
            return kitty

    # modifyOtherKeys: CSI 27 ; modifier ; code ~
    m = _MODIFY_OTHER_KEYS_RE.match(s)
    if m:
        mod_val = int(m.group(1)) - 1
        char_code = int(m.group(2))
        key["ctrl"] = bool(mod_val & 4)
        key["meta"] = bool(mod_val & 2)
        key["shift"] = bool(mod_val & 1)
        key["option"] = bool(mod_val & 2)
        key["super"] = bool(mod_val & 8)
        key["hyper"] = bool(mod_val & 16)
        if char_code == 13:
            key["name"] = "return"
        elif char_code == 27:
            key["name"] = "escape"
        elif char_code == 9:
            key["name"] = "tab"
        elif char_code == 32:
            key["name"] = "space"
        elif char_code in (127, 8):
            key["name"] = "backspace"
        else:
            key["name"] = chr(char_code) if 0 <= char_code <= 0x10FFFF else ""
        return key

    # Single chars and common sequences
    if s in ("\r", "\x1b\r"):
        key["name"] = "return"
        key["meta"] = key["option"] = len(s) == 2
    elif s in ("\n", "\x1b\n"):
        key["name"] = "linefeed"
        key["meta"] = key["option"] = len(s) == 2
    elif s == "\t":
        key["name"] = "tab"
        key["char"] = "\t"
    elif s in ("\b", "\x1b\b", "\x7f", "\x1b\x7f"):
        key["name"] = "backspace"
        key["meta"] = key["option"] = s[0] == "\x1b"
    elif s in ("\x1b", "\x1b\x1b"):
        key["name"] = "escape"
        key["meta"] = key["option"] = len(s) == 2
    elif s in (" ", "\x1b "):
        key["name"] = "space"
        key["char"] = " "
        key["meta"] = key["option"] = len(s) == 2
    elif s == "\x00":
        key["name"] = "space"
        key["char"] = " "
        key["ctrl"] = True
    elif len(s) == 1 and s <= "\x1a":
        key["name"] = chr(ord(s) + ord("a") - 1)
        key["ctrl"] = True
    elif len(s) == 1 and "0" <= s <= "9":
        key["name"] = s
        key["char"] = s
        key["number"] = True
    elif len(s) == 1 and "a" <= s <= "z":
        key["name"] = s
        key["char"] = s
    elif len(s) == 1 and "A" <= s <= "Z":
        key["name"] = s.lower()
        key["shift"] = True
    elif len(s) == 1:
        key["name"] = s
        key["char"] = s
    elif s.startswith("\x1bO") and len(s) == 3:
        # SS3: ESC O + letter (e.g. arrow keys)
        ss3: dict[str, str] = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end", "P": "f1", "Q": "f2", "R": "f3", "S": "f4"}
        key["name"] = ss3.get(s[2], "")
        key["sequence"] = s
        key["raw"] = s
        return key
    elif s.startswith("\x1b[O") and len(s) == 4 and s[3] in "ABCDEFHPQRS":
        # CSI application cursor: ESC [ O letter (Mac/some terminals)
        app_cursor: dict[str, str] = {"A": "up", "B": "down", "C": "right", "D": "left", "E": "clear", "F": "end", "H": "home", "P": "f1", "Q": "f2", "R": "f3", "S": "f4"}
        key["name"] = app_cursor.get(s[3], "")
        key["sequence"] = s
        key["raw"] = s
        return key
    else:
        # Meta+char: ESC + single char
        m2 = _META_KEY_RE.match(s)
        if m2:
            key["meta"] = key["option"] = True
            ch = m2.group(1)
            if ch == "F":
                key["name"] = "right"
            elif ch == "B":
                key["name"] = "left"
            elif ch.isupper():
                key["shift"] = True
                key["name"] = ch
            else:
                key["name"] = ch
            return key
        # Meta+ctrl+letter
        if len(s) == 2 and s[0] == "\x1b" and s[1] <= "\x1a":
            key["meta"] = key["option"] = True
            key["ctrl"] = True
            key["name"] = chr(ord(s[1]) + ord("a") - 1)
            return key
        # CSI/SS3 function key
        m3 = _FN_KEY_RE.match(s)
        if m3:
            parts = list(m3.groups())
            code = "".join(p for p in (parts[0], parts[1], parts[3], parts[5]) if p)
            mod_val = int(parts[2] or parts[4] or "1") - 1
            key["ctrl"] = bool(mod_val & 4)
            key["meta"] = bool(mod_val & 2)
            key["shift"] = bool(mod_val & 1)
            key["option"] = bool(mod_val & 2)
            key["super"] = bool(mod_val & 8)
            key["hyper"] = bool(mod_val & 16)
            key["code"] = code
            name = _KEY_NAME.get(code)
            if not name and len(code) >= 2 and code[0] == "[" and code[-1] in "ABCDEFHPQRS":
                name = _KEY_NAME.get("[" + code[-1])
            if name:
                key["name"] = "backtab" if code == "[Z" else name  # Shift+Tab sends ESC [ Z
                key["shift"] = _is_shift_key(code) or key["shift"]
                key["ctrl"] = _is_ctrl_key(code) or key["ctrl"]
            else:
                key["name"] = ""
                del key["code"]
            return key
        if s == "\x1b[3~":
            key["name"] = "delete"
            key["meta"] = False
            key["code"] = "[3~"
            return key

    return key


def _parse_kitty_keyboard(s: str) -> ParsedKey | None:
    """Kitty CSI u: ESC [ code ; modifier u. Aligns OpenTUI parseKittyKeyboard."""
    if not s.startswith("\x1b[") or not s.endswith("u"):
        return None
    inner = s[2:-1]
    if ":" in inner:
        inner = inner.split(":")[0]
    part = inner.split(";")
    if len(part) < 1:
        return None
    try:
        keycode = int(part[0])
        mod_val = int(part[1]) if len(part) > 1 else 1
    except (ValueError, IndexError):
        return None
    m = max(0, mod_val - 1)
    key: ParsedKey = {
        "name": "",
        "ctrl": bool(m & 4),
        "meta": bool(m & 2),
        "shift": bool(m & 1),
        "option": bool(m & 2),
        "number": False,
        "sequence": s,
        "raw": s,
        "eventType": "press",
        "source": "kitty",
    }
    _KITTY_NAMES: dict[int, str] = {
        9: "tab", 13: "return", 27: "escape", 127: "backspace",
        57376: "f13", 57377: "f14",
        57417: "left", 57418: "right", 57419: "up", 57420: "down",
    }
    name = _KITTY_NAMES.get(keycode)
    if name is not None:
        key["name"] = name
        key["char"] = "" if name in ("tab", "return", "escape", "backspace", "up", "down", "left", "right", "f13", "f14") else (chr(keycode) if 32 <= keycode <= 126 else "")
    elif 32 <= keycode <= 126:
        key["name"] = chr(keycode)
        key["char"] = chr(keycode)
    elif 1 <= keycode <= 26:
        key["name"] = chr(keycode + 96)
        key["char"] = ""
        key["ctrl"] = True
    elif keycode == 0:
        key["name"] = "space"
        key["char"] = " "
    else:
        key["name"] = "unknown"
        key["char"] = ""
    return key
