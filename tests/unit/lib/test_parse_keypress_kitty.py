# Unit tests for pytui.lib.parse_keypress_kitty - aligned with OpenTUI parse.keypress-kitty.test.ts

from __future__ import annotations

import pytest

from pytui.lib.parse_keypress_kitty import parse_kitty_keyboard


class TestParseKittyKeyboard:
    def test_kitty_basic_key_a(self) -> None:
        result = parse_kitty_keyboard("\x1b[97u")
        assert result is not None
        assert result["name"] == "a"
        assert result["sequence"] == "a"
        assert result.get("ctrl") is False
        assert result.get("meta") is False
        assert result.get("shift") is False

    def test_kitty_shift_a(self) -> None:
        result = parse_kitty_keyboard("\x1b[97:65;2u")
        assert result is not None
        assert result["name"] == "a"
        assert result["sequence"] == "A"
        assert result.get("shift") is True
        assert result.get("ctrl") is False
        assert result.get("meta") is False

    def test_kitty_ctrl_a(self) -> None:
        result = parse_kitty_keyboard("\x1b[97;5u")
        assert result is not None
        assert result["name"] == "a"
        assert result.get("ctrl") is True
        assert result.get("shift") is False
        assert result.get("meta") is False

    def test_kitty_alt_a(self) -> None:
        result = parse_kitty_keyboard("\x1b[97;3u")
        assert result is not None
        assert result["name"] == "a"
        assert result.get("meta") is True
        assert result.get("option") is True
        assert result.get("ctrl") is False
        assert result.get("shift") is False

    def test_kitty_function_key_f1(self) -> None:
        result = parse_kitty_keyboard("\x1b[57364u")
        assert result is not None
        assert result["name"] == "f1"
        assert result.get("code") == "[57364u"

    def test_kitty_arrow_up(self) -> None:
        result = parse_kitty_keyboard("\x1b[57352u")
        assert result is not None
        assert result["name"] == "up"
        assert result.get("code") == "[57352u"

    def test_kitty_shift_space(self) -> None:
        result = parse_kitty_keyboard("\x1b[32;2u")
        assert result is not None
        assert result["name"] == " "
        assert result["sequence"] == " "
        assert result.get("shift") is True

    def test_kitty_event_types(self) -> None:
        press_explicit = parse_kitty_keyboard("\x1b[97;1:1u")
        assert press_explicit is not None
        assert press_explicit["name"] == "a"
        assert press_explicit["eventType"] == "press"

        repeat = parse_kitty_keyboard("\x1b[97;1:2u")
        assert repeat is not None
        assert repeat["name"] == "a"
        assert repeat["eventType"] == "press"
        assert repeat.get("repeated") is True

        release = parse_kitty_keyboard("\x1b[97;1:3u")
        assert release is not None
        assert release["name"] == "a"
        assert release["eventType"] == "release"

    def test_kitty_special_functional_up(self) -> None:
        # CSI 1;1:1A = up arrow press
        result = parse_kitty_keyboard("\x1b[1;1:1A")
        assert result is not None
        assert result["name"] == "up"
        assert result.get("source") == "kitty"

    def test_kitty_special_tilde_pageup(self) -> None:
        # CSI 5;1:1~ = pageup
        result = parse_kitty_keyboard("\x1b[5;1:1~")
        assert result is not None
        assert result["name"] == "pageup"

    def test_kitty_invalid_returns_none(self) -> None:
        assert parse_kitty_keyboard("") is None
        assert parse_kitty_keyboard("x") is None
        # Codepoint > 0x10FFFF is invalid Unicode; parser should return None
        assert parse_kitty_keyboard("\x1b[1114112u") is None
