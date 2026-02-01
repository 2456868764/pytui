# Unit tests for pytui.lib.clipboard - aligned with OpenTUI clipboard.test.ts

from __future__ import annotations

import base64
from typing import Any

import pytest

from pytui.lib.clipboard import Clipboard, ClipboardTarget


def _create_mock_adapter(*, supported: bool = True) -> tuple[Any, Any, Any]:
    last_target: list[int | None] = [None]
    last_payload: list[bytes | None] = [None]

    class Adapter:
        def copy_to_clipboard(self, target: int, payload: bytes) -> bool:
            last_target[0] = target
            last_payload[0] = payload
            return supported

        def is_osc52_supported(self) -> bool:
            return supported

    def get_last_target() -> int | None:
        return last_target[0]

    def get_last_payload() -> bytes | None:
        return last_payload[0]

    return Adapter(), get_last_target, get_last_payload


class TestCopyToClipboardOSC52:
    def test_returns_false_when_osc52_not_supported(self) -> None:
        adapter, _, _ = _create_mock_adapter(supported=False)
        clipboard = Clipboard(adapter)
        assert clipboard.copy_to_clipboard_osc52("test") is False

    def test_returns_true_when_osc52_supported(self) -> None:
        adapter, _, _ = _create_mock_adapter(supported=True)
        clipboard = Clipboard(adapter)
        assert clipboard.copy_to_clipboard_osc52("test") is True

    def test_encodes_base64_and_delegates_to_adapter(self) -> None:
        adapter, get_target, get_payload = _create_mock_adapter()
        clipboard = Clipboard(adapter)
        clipboard.copy_to_clipboard_osc52("hello")
        assert get_target() == ClipboardTarget.Clipboard
        payload = get_payload()
        assert payload is not None
        decoded = base64.b64decode(payload).decode("utf-8")
        assert decoded == "hello"

    def test_supports_different_targets(self) -> None:
        adapter, get_target, _ = _create_mock_adapter()
        clipboard = Clipboard(adapter)
        clipboard.copy_to_clipboard_osc52("test", ClipboardTarget.Primary)
        assert get_target() == ClipboardTarget.Primary
        clipboard.copy_to_clipboard_osc52("test", ClipboardTarget.Secondary)
        assert get_target() == ClipboardTarget.Secondary
        clipboard.copy_to_clipboard_osc52("test", ClipboardTarget.Query)
        assert get_target() == ClipboardTarget.Query


class TestClearClipboardOSC52:
    def test_returns_false_when_osc52_not_supported(self) -> None:
        adapter, _, _ = _create_mock_adapter(supported=False)
        clipboard = Clipboard(adapter)
        assert clipboard.clear_clipboard_osc52() is False

    def test_sends_empty_payload_to_adapter(self) -> None:
        adapter, _, get_payload = _create_mock_adapter()
        clipboard = Clipboard(adapter)
        clipboard.clear_clipboard_osc52()
        payload = get_payload()
        assert payload is not None
        assert len(payload) == 0


class TestIsOsc52Supported:
    def test_returns_false_when_adapter_reports_not_supported(self) -> None:
        adapter, _, _ = _create_mock_adapter(supported=False)
        clipboard = Clipboard(adapter)
        assert clipboard.is_osc52_supported() is False

    def test_returns_true_when_adapter_reports_supported(self) -> None:
        adapter, _, _ = _create_mock_adapter(supported=True)
        clipboard = Clipboard(adapter)
        assert clipboard.is_osc52_supported() is True
