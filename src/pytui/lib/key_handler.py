# pytui.lib.key_handler - Aligns with OpenTUI lib/KeyHandler.ts
# KeyHandler, KeyEvent, PasteEvent, InternalKeyHandler; processInput, processPaste, onInternal, offInternal

from __future__ import annotations

import logging
import re
from typing import Any, Callable

from pyee import EventEmitter

from pytui.lib.parse_keypress import parse_keypress

_LOG = logging.getLogger(__name__)


class KeyEvent:
    """Key event with preventDefault/stopPropagation. Aligns OpenTUI KeyEvent (wraps ParsedKey)."""

    def __init__(self, parsed: dict[str, Any]) -> None:
        self._parsed = parsed
        self._default_prevented = False
        self._propagation_stopped = False

    @property
    def default_prevented(self) -> bool:
        return self._default_prevented

    @property
    def propagation_stopped(self) -> bool:
        return self._propagation_stopped

    def prevent_default(self) -> None:
        self._default_prevented = True

    def stop_propagation(self) -> None:
        self._propagation_stopped = True

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get for backward compat (name, char, ctrl, shift, meta, option, sequence)."""
        return self._parsed.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._parsed[key]

    def __contains__(self, key: str) -> bool:
        return key in self._parsed

    @property
    def name(self) -> str:
        return self._parsed.get("name", "")

    @property
    def sequence(self) -> str:
        return self._parsed.get("sequence", "")

    @property
    def raw(self) -> str:
        return self._parsed.get("raw", "")

    @property
    def number(self) -> bool:
        return self._parsed.get("number", False)

    @property
    def event_type(self) -> str:
        return self._parsed.get("eventType", "press")

    @property
    def source(self) -> str:
        return self._parsed.get("source", "raw")

    @property
    def ctrl(self) -> bool:
        return self._parsed.get("ctrl", False)

    @property
    def meta(self) -> bool:
        return self._parsed.get("meta", False)

    @property
    def shift(self) -> bool:
        return self._parsed.get("shift", False)

    @property
    def option(self) -> bool:
        return self._parsed.get("option", False)

    @property
    def char(self) -> str:
        return self._parsed.get("char", "")

    @property
    def code(self) -> str | None:
        return self._parsed.get("code")

    @property
    def super_key(self) -> bool | None:
        return self._parsed.get("super")

    @property
    def hyper(self) -> bool | None:
        return self._parsed.get("hyper")

    @property
    def caps_lock(self) -> bool | None:
        return self._parsed.get("capsLock")

    @property
    def num_lock(self) -> bool | None:
        return self._parsed.get("numLock")

    @property
    def base_code(self) -> int | None:
        return self._parsed.get("baseCode")

    @property
    def repeated(self) -> bool | None:
        return self._parsed.get("repeated")


class PasteEvent:
    """Paste event with preventDefault/stopPropagation. Aligns OpenTUI PasteEvent."""

    def __init__(self, text: str) -> None:
        self.text = text
        self._default_prevented = False
        self._propagation_stopped = False

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get for backward compat (e.g. pasted[0].get('text'))."""
        if key == "text":
            return self.text
        return default

    @property
    def default_prevented(self) -> bool:
        return self._default_prevented

    @property
    def propagation_stopped(self) -> bool:
        return self._propagation_stopped

    def prevent_default(self) -> None:
        self._default_prevented = True

    def stop_propagation(self) -> None:
        self._propagation_stopped = True


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences. Aligns OpenTUI Bun.stripANSI behavior."""
    # Strip CSI sequences (e.g. \x1b[31m, \x1b[0m) and OSC (e.g. \x1b]0;title\x07)
    text = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)
    text = re.sub(r"\x1b\][^\x07]*(?:\x07|\x1b\\)?", "", text)
    return text


class KeyHandler(EventEmitter):
    """Keyboard input handler. processInput(data), processPaste(data). Emits keypress, keyrelease, paste. Aligns OpenTUI KeyHandler."""

    def __init__(self, use_kitty_keyboard: bool = False) -> None:
        super().__init__()
        self.use_kitty_keyboard = use_kitty_keyboard

    def process_input(self, data: str | bytes) -> bool:
        """Parse input and emit keypress/keyrelease. Returns True if key was emitted. Aligns OpenTUI processInput()."""
        parsed = parse_keypress(data, {"use_kitty_keyboard": self.use_kitty_keyboard})
        if parsed is None:
            return False
        try:
            event_type = parsed.get("eventType", "press")
            key_event = KeyEvent(parsed)
            if event_type == "release":
                self.emit("keyrelease", key_event)
            else:
                self.emit("keypress", key_event)
        except Exception as e:
            _LOG.exception("[KeyHandler] Error processing input: %s", e)
            return True
        return True

    def process_paste(self, data: str) -> None:
        """Emit paste event with cleaned text (strip ANSI). Aligns OpenTUI processPaste()."""
        try:
            text = _strip_ansi(data)
            self.emit("paste", PasteEvent(text))
        except Exception as e:
            _LOG.exception("[KeyHandler] Error processing paste: %s", e)


class InternalKeyHandler(KeyHandler):
    """Used by renderer: global handlers run first, then internal (renderable) handlers. preventDefault prevents internal. Aligns OpenTUI InternalKeyHandler."""

    def __init__(self, use_kitty_keyboard: bool = False) -> None:
        super().__init__(use_kitty_keyboard)
        self._internal_handlers: dict[str, set[Callable[..., None]]] = {}

    def emit(self, event: str, *args: Any) -> bool:
        if event not in ("keypress", "keyrelease", "paste"):
            return super().emit(event, *args)
        return self._emit_with_priority(event, *args)

    def _emit_with_priority(self, event: str, *args: Any) -> bool:
        has_global = False
        raw = getattr(self, "_events", {}).get(event)
        if raw is None:
            raw = ()
        listeners = list(raw) if not hasattr(raw, "keys") else list(raw.keys())
        if listeners:
            has_global = True
            for fn in listeners:
                try:
                    fn(*args)
                except Exception as e:
                    _LOG.exception("[KeyHandler] Error in global %s handler: %s", event, e)
                if args and getattr(args[0], "propagation_stopped", False):
                    return has_global
        internal_set = self._internal_handlers.get(event)
        internal_list = list(internal_set) if internal_set else []
        has_internal = bool(internal_list)
        if internal_list and args:
            ev = args[0]
            if getattr(ev, "default_prevented", False) or getattr(ev, "propagation_stopped", False):
                return has_global or has_internal
            for fn in internal_list:
                try:
                    fn(*args)
                except Exception as e:
                    _LOG.exception("[KeyHandler] Error in renderable %s handler: %s", event, e)
                if getattr(args[0], "propagation_stopped", False):
                    return has_global or has_internal
        return has_global or has_internal

    def on_internal(self, event: str, handler: Callable[..., None]) -> None:
        """Register internal (renderable) handler. Aligns OpenTUI onInternal()."""
        if event not in self._internal_handlers:
            self._internal_handlers[event] = set()
        self._internal_handlers[event].add(handler)

    def off_internal(self, event: str, handler: Callable[..., None]) -> None:
        """Unregister internal handler. Aligns OpenTUI offInternal()."""
        s = self._internal_handlers.get(event)
        if s:
            s.discard(handler)
