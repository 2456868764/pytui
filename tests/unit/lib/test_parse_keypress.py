# Aligns with OpenTUI lib/parse.keypress.test.ts

import pytest

from pytui.lib.parse_keypress import (
    KeyEventType,
    non_alphanumeric_keys,
    parse_keypress,
)


def _norm(d: dict) -> dict:
    """Normalize parsed key for assertion (only fields we care about)."""
    return {k: d.get(k) for k in ("name", "ctrl", "meta", "shift", "option", "number", "sequence", "raw", "eventType", "source") if k in d}


class TestParseKeypressBasicLetters:
    """Aligns: parse.keypress.test.ts - parseKeypress basic letters"""

    def test_basic_letters(self):
        r = parse_keypress("a")
        assert r is not None
        assert _norm(r) == {
            "name": "a",
            "ctrl": False,
            "meta": False,
            "shift": False,
            "option": False,
            "number": False,
            "sequence": "a",
            "raw": "a",
            "eventType": "press",
            "source": "raw",
        }
        r2 = parse_keypress("A")
        assert r2 is not None
        assert r2["name"] == "a"
        assert r2["shift"] is True
        assert r2["sequence"] == "A"
        assert r2["raw"] == "A"


class TestParseKeypressNumbers:
    def test_numbers(self):
        r = parse_keypress("1")
        assert r is not None
        assert r["name"] == "1"
        assert r["number"] is True
        assert r["sequence"] == "1"
        assert r["raw"] == "1"


class TestParseKeypressSpecialKeys:
    """Aligns: parse.keypress.test.ts - parseKeypress special keys"""

    def test_return(self):
        r = parse_keypress("\r")
        assert r is not None
        assert r["name"] == "return"
        assert r["sequence"] == "\r"
        assert r["raw"] == "\r"

    def test_linefeed(self):
        r = parse_keypress("\n")
        assert r is not None
        assert r["name"] == "linefeed"
        assert r["sequence"] == "\n"
        assert r["raw"] == "\n"

    def test_meta_return_and_meta_linefeed(self):
        r = parse_keypress("\x1b\r")
        assert r is not None
        assert r["name"] == "return"
        assert r["meta"] is True
        r2 = parse_keypress("\x1b\n")
        assert r2 is not None
        assert r2["name"] == "linefeed"
        assert r2["meta"] is True

    def test_tab(self):
        r = parse_keypress("\t")
        assert r is not None
        assert r["name"] == "tab"
        assert r["sequence"] == "\t"

    def test_backspace(self):
        r = parse_keypress("\b")
        assert r is not None
        assert r["name"] == "backspace"
        assert r["sequence"] == "\b"

    def test_escape(self):
        r = parse_keypress("\x1b")
        assert r is not None
        assert r["name"] == "escape"
        assert r["sequence"] == "\x1b"

    def test_space(self):
        r = parse_keypress(" ")
        assert r is not None
        assert r["name"] == "space"
        assert r["sequence"] == " "


class TestParseKeypressCtrlLetter:
    def test_ctrl_letter_combinations(self):
        r = parse_keypress("\x01")
        assert r is not None
        assert r["name"] == "a"
        assert r["ctrl"] is True
        assert r["sequence"] == "\x01"
        r2 = parse_keypress("\x1a")
        assert r2 is not None
        assert r2["name"] == "z"
        assert r2["ctrl"] is True


class TestParseKeypressFilterMouseAndResponses:
    """Aligns: parseKeypress returns null for mouse / terminal responses / paste markers"""

    def test_mouse_sgr_returns_none(self):
        assert parse_keypress("\x1b[<0;10;5M") is None
        assert parse_keypress("\x1b[<0;10;5m") is None

    def test_mouse_basic_returns_none(self):
        assert parse_keypress("\x1b[M ab") is None

    def test_window_size_report_returns_none(self):
        assert parse_keypress("\x1b[4;24;80t") is None

    def test_cursor_position_report_returns_none(self):
        assert parse_keypress("\x1b[1;1R") is None

    def test_device_attributes_returns_none(self):
        assert parse_keypress("\x1b[?1;0c") is None

    def test_focus_events_return_none(self):
        assert parse_keypress("\x1b[I") is None
        assert parse_keypress("\x1b[O") is None

    def test_bracketed_paste_markers_return_none(self):
        assert parse_keypress("\x1b[200~") is None
        assert parse_keypress("\x1b[201~") is None


class TestNonAlphanumericKeys:
    """Aligns: parse.keypress.test.ts - nonAlphanumericKeys = [...Object.values(keyName), 'backspace']"""

    def test_non_alphanumeric_keys_contains_key_name_values_and_backspace(self):
        assert "backspace" in non_alphanumeric_keys
        assert "tab" in non_alphanumeric_keys
        assert "up" in non_alphanumeric_keys
        assert "down" in non_alphanumeric_keys
        assert "f1" in non_alphanumeric_keys
        assert "home" in non_alphanumeric_keys
        assert "end" in non_alphanumeric_keys
