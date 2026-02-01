# pytui.lib.parse_keypress_kitty - Aligns with OpenTUI lib/parse.keypress-kitty.ts
# Kitty Keyboard Protocol parser.

from __future__ import annotations

import re
from typing import Any

from pytui.lib.parse_keypress import KeyEventType, ParsedKey

# Kitty key code -> key name. Aligns with OpenTUI kittyKeyMap.
KITTY_KEY_MAP: dict[int, str] = {
    27: "escape",
    9: "tab",
    13: "return",
    127: "backspace",
    57344: "escape",
    57345: "return",
    57346: "tab",
    57347: "backspace",
    57348: "insert",
    57349: "delete",
    57350: "left",
    57351: "right",
    57352: "up",
    57353: "down",
    57354: "pageup",
    57355: "pagedown",
    57356: "home",
    57357: "end",
    57364: "f1", 57365: "f2", 57366: "f3", 57367: "f4", 57368: "f5", 57369: "f6",
    57370: "f7", 57371: "f8", 57372: "f9", 57373: "f10", 57374: "f11", 57375: "f12",
    57376: "f13", 57377: "f14", 57378: "f15", 57379: "f16", 57380: "f17", 57381: "f18",
    57382: "f19", 57383: "f20", 57384: "f21", 57385: "f22", 57386: "f23", 57387: "f24",
    57388: "f25", 57389: "f26", 57390: "f27", 57391: "f28", 57392: "f29", 57393: "f30",
    57394: "f31", 57395: "f32", 57396: "f33", 57397: "f34", 57398: "f35",
    57400: "kp0", 57401: "kp1", 57402: "kp2", 57403: "kp3", 57404: "kp4",
    57405: "kp5", 57406: "kp6", 57407: "kp7", 57408: "kp8", 57409: "kp9",
    57410: "kpdecimal", 57411: "kpdivide", 57412: "kpmultiply", 57413: "kpminus",
    57414: "kpplus", 57415: "kpenter", 57416: "kpequal",
    57428: "mediaplay", 57429: "mediapause", 57430: "mediaplaypause", 57431: "mediareverse",
    57432: "mediastop", 57433: "mediafastforward", 57434: "mediarewind", 57435: "medianext",
    57436: "mediaprev", 57437: "mediarecord",
    57438: "volumedown", 57439: "volumeup", 57440: "mute",
    57441: "leftshift", 57442: "leftctrl", 57443: "leftalt", 57444: "leftsuper",
    57445: "lefthyper", 57446: "leftmeta", 57447: "rightshift", 57448: "rightctrl",
    57449: "rightalt", 57450: "rightsuper", 57451: "righthyper", 57452: "rightmeta",
    57453: "iso_level3_shift", 57454: "iso_level5_shift",
}

FUNCTIONAL_KEY_MAP: dict[str, str] = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end", "P": "f1", "Q": "f2", "R": "f3", "S": "f4"}

TILDE_KEY_MAP: dict[str, str] = {
    "1": "home", "2": "insert", "3": "delete", "4": "end", "5": "pageup", "6": "pagedown",
    "7": "home", "8": "end", "11": "f1", "12": "f2", "13": "f3", "14": "f4", "15": "f5",
    "17": "f6", "18": "f7", "19": "f8", "20": "f9", "21": "f10", "23": "f11", "24": "f12",
}


def _from_kitty_mods(mod: int) -> dict[str, bool]:
    """Align with OpenTUI fromKittyMods."""
    return {
        "shift": bool(mod & 1),
        "alt": bool(mod & 2),
        "ctrl": bool(mod & 4),
        "super": bool(mod & 8),
        "hyper": bool(mod & 16),
        "meta": bool(mod & 32),
        "capsLock": bool(mod & 64),
        "numLock": bool(mod & 128),
    }


_SPECIAL_KEY_RE = re.compile(r"^\x1b\[(\d+);(\d+):(\d+)([A-Z~])$")
_KITTY_CSI_RE = re.compile(r"^\x1b\[([^\x1b]+)u$")


def _parse_kitty_special_key(sequence: str) -> ParsedKey | None:
    """Parse Kitty functional/tilde special keys. Aligns with OpenTUI parseKittySpecialKey."""
    m = _SPECIAL_KEY_RE.match(sequence)
    if not m:
        return None
    key_num_or_one, modifier_str, event_type_str, terminator = m.groups()
    key_name: str | None = TILDE_KEY_MAP.get(key_num_or_one) if terminator == "~" else (FUNCTIONAL_KEY_MAP.get(terminator) if key_num_or_one == "1" else None)
    if not key_name:
        return None
    key: ParsedKey = {
        "name": key_name,
        "ctrl": False,
        "meta": False,
        "shift": False,
        "option": False,
        "number": False,
        "sequence": sequence,
        "raw": sequence,
        "eventType": "press",
        "source": "kitty",
        "super": False,
        "hyper": False,
        "capsLock": False,
        "numLock": False,
    }
    if modifier_str:
        mod_val = int(modifier_str, 10)
        if mod_val > 1:
            mods = _from_kitty_mods(mod_val - 1)
            key["shift"] = mods["shift"]
            key["ctrl"] = mods["ctrl"]
            key["meta"] = mods["alt"] or mods["meta"]
            key["option"] = mods["alt"]
            key["super"] = mods["super"]
            key["hyper"] = mods["hyper"]
            key["capsLock"] = mods["capsLock"]
            key["numLock"] = mods["numLock"]
    if event_type_str == "2":
        key["eventType"] = "press"
        key["repeated"] = True
    elif event_type_str == "3":
        key["eventType"] = "release"
    return key


def parse_kitty_keyboard(sequence: str) -> ParsedKey | None:
    """Parse Kitty keyboard protocol sequence. Aligns with OpenTUI parseKittyKeyboard."""
    special = _parse_kitty_special_key(sequence)
    if special is not None:
        return special
    m = _KITTY_CSI_RE.match(sequence)
    if not m:
        return None
    params = m.group(1)
    fields = params.split(";")
    if not fields:
        return None
    key: ParsedKey = {
        "name": "",
        "ctrl": False,
        "meta": False,
        "shift": False,
        "option": False,
        "number": False,
        "sequence": sequence,
        "raw": sequence,
        "eventType": "press",
        "source": "kitty",
        "super": False,
        "hyper": False,
        "capsLock": False,
        "numLock": False,
    }
    field1 = fields[0].split(":")
    codepoint_str = field1[0] if field1 else ""
    if not codepoint_str:
        return None
    try:
        codepoint = int(codepoint_str, 10)
    except ValueError:
        return None
    shifted_codepoint: int | None = None
    base_codepoint: int | None = None
    if len(field1) > 1 and field1[1]:
        try:
            s = int(field1[1], 10)
            if 0 < s <= 0x10FFFF:
                shifted_codepoint = s
        except ValueError:
            pass
    if len(field1) > 2 and field1[2]:
        try:
            b = int(field1[2], 10)
            if 0 < b <= 0x10FFFF:
                base_codepoint = b
        except ValueError:
            pass
    known = KITTY_KEY_MAP.get(codepoint)
    if known:
        key["name"] = known
        key["code"] = f"[{codepoint}u"
    else:
        if 0 < codepoint <= 0x10FFFF:
            key["name"] = chr(codepoint)
            if base_codepoint is not None:
                key["baseCode"] = base_codepoint
        else:
            return None
    if len(fields) > 1 and fields[1]:
        parts = fields[1].split(":")
        mod_str = parts[0] if parts else ""
        event_str = parts[1] if len(parts) > 1 else ""
        if mod_str:
            try:
                mod_val = int(mod_str, 10)
                if mod_val > 1:
                    mods = _from_kitty_mods(mod_val - 1)
                    key["shift"] = mods["shift"]
                    key["ctrl"] = mods["ctrl"]
                    key["meta"] = mods["alt"] or mods["meta"]
                    key["option"] = mods["alt"]
                    key["super"] = mods["super"]
                    key["hyper"] = mods["hyper"]
                    key["capsLock"] = mods["capsLock"]
                    key["numLock"] = mods["numLock"]
            except ValueError:
                pass
        if event_str == "2":
            key["repeated"] = True
        elif event_str == "3":
            key["eventType"] = "release"
    text = ""
    if len(fields) > 2 and fields[2]:
        for cp_str in fields[2].split(":"):
            try:
                cp = int(cp_str, 10)
                if 0 < cp <= 0x10FFFF:
                    text += chr(cp)
            except ValueError:
                pass
    if not text and key.get("name"):
        is_printable = codepoint not in KITTY_KEY_MAP
        if is_printable:
            if key.get("shift") and shifted_codepoint is not None:
                text = chr(shifted_codepoint)
            elif key.get("shift") and len(key["name"]) == 1:
                text = key["name"].upper()
            else:
                text = key["name"]
    if key.get("name") == " " and key.get("shift") and not key.get("ctrl") and not key.get("meta"):
        text = " "
    if text:
        key["sequence"] = text
    return key
