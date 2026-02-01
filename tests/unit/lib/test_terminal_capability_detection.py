# Aligns with OpenTUI lib/terminal-capability-detection.test.ts

import pytest

from pytui.lib.terminal_capability_detection import (
    is_capability_response,
    is_pixel_resolution_response,
    parse_pixel_resolution,
)


class TestIsCapabilityResponse:
    """Aligns: terminal-capability-detection.test.ts - isCapabilityResponse"""

    def test_detects_decrpm_responses(self):
        assert is_capability_response("\x1b[?1016;2$y") is True
        assert is_capability_response("\x1b[?2027;0$y") is True
        assert is_capability_response("\x1b[?1004;1$y") is True

    def test_detects_cpr_responses_for_width_detection(self):
        assert is_capability_response("\x1b[1;2R") is True
        assert is_capability_response("\x1b[1;3R") is True

    def test_does_not_detect_regular_cpr_as_capabilities(self):
        assert is_capability_response("\x1b[10;5R") is False
        assert is_capability_response("\x1b[20;30R") is False

    def test_detects_xtversion_responses(self):
        assert is_capability_response("\x1bP>|kitty(0.40.1)\x1b\\") is True
        assert is_capability_response("\x1bP>|ghostty 1.1.3\x1b\\") is True

    def test_detects_da1_responses(self):
        assert is_capability_response("\x1b[?62;c") is True
        assert is_capability_response("\x1b[?1;2;4c") is True
        assert is_capability_response("\x1b[?6c") is True

    def test_detects_kitty_keyboard_query_responses(self):
        assert is_capability_response("\x1b[?0u") is True
        assert is_capability_response("\x1b[?1u") is True
        assert is_capability_response("\x1b[?31u") is True

    def test_does_not_detect_regular_keypresses(self):
        assert is_capability_response("a") is False
        assert is_capability_response("\x1b[A") is False

    def test_does_not_detect_mouse_sequences(self):
        assert is_capability_response("\x1b[<0;10;10M") is False


class TestIsPixelResolutionResponse:
    """Aligns: terminal-capability-detection.test.ts - isPixelResolutionResponse"""

    def test_detects_pixel_resolution_format(self):
        assert is_pixel_resolution_response("\x1b[4;768;1024t") is True
        assert is_pixel_resolution_response("\x1b[4;600;800t") is True

    def test_rejects_non_resolution_sequences(self):
        assert is_pixel_resolution_response("\x1b[10;5R") is False
        assert is_pixel_resolution_response("a") is False


class TestParsePixelResolution:
    """Aligns: terminal-capability-detection.test.ts - parsePixelResolution"""

    def test_parses_width_height(self):
        out = parse_pixel_resolution("\x1b[4;768;1024t")
        assert out is not None
        width, height = out
        assert width == 1024
        assert height == 768

    def test_returns_none_for_invalid(self):
        assert parse_pixel_resolution("\x1b[10;5R") is None
        assert parse_pixel_resolution("") is None
