# Aligns with OpenTUI lib/KeyHandler.test.ts

import pytest

from pytui.lib.key_handler import (
    InternalKeyHandler,
    KeyEvent,
    KeyHandler,
    PasteEvent,
)


def create_key_handler(use_kitty_keyboard: bool = False) -> InternalKeyHandler:
    return InternalKeyHandler(use_kitty_keyboard)


class TestKeyHandlerProcessInput:
    """Aligns: KeyHandler.test.ts - processInput emits keypress events"""

    def test_process_input_emits_keypress_events(self):
        handler = InternalKeyHandler()
        received: list[KeyEvent] = []
        handler.on("keypress", lambda key: received.append(key))
        handler.process_input("a")
        assert len(received) == 1
        assert received[0].name == "a"
        assert received[0].ctrl is False
        assert received[0].meta is False
        assert received[0].shift is False
        assert received[0].option is False
        assert received[0].number is False
        assert received[0].sequence == "a"
        assert received[0].raw == "a"
        assert received[0].event_type == "press"

    def test_emits_keypress_events(self):
        handler = create_key_handler()
        received: list[KeyEvent] = []
        handler.on("keypress", lambda key: received.append(key))
        handler.process_input("a")
        assert len(received) == 1
        assert received[0].name == "a"
        assert received[0].sequence == "a"
        assert received[0].event_type == "press"

    def test_handles_string_input(self):
        handler = create_key_handler()
        received: list[KeyEvent] = []
        handler.on("keypress", lambda key: received.append(key))
        handler.process_input("c")
        assert len(received) == 1
        assert received[0].name == "c"
        assert received[0].sequence == "c"


class TestKeyHandlerPaste:
    """Aligns: KeyHandler.test.ts - paste"""

    def test_handles_paste_via_process_paste(self):
        handler = create_key_handler()
        received: list[str] = []
        handler.on("paste", lambda event: received.append(event.text))
        handler.process_paste("pasted content")
        assert received == ["pasted content"]

    def test_process_paste_handles_content_directly(self):
        handler = create_key_handler()
        received: list[str] = []
        handler.on("paste", lambda event: received.append(event.text))
        handler.process_paste("chunk1chunk2chunk3")
        assert received == ["chunk1chunk2chunk3"]

    def test_strips_ansi_codes_in_paste(self):
        handler = create_key_handler()
        received: list[str] = []
        handler.on("paste", lambda event: received.append(event.text))
        handler.process_paste("text with \x1b[31mred\x1b[0m color")
        assert "red" in received[0]
        assert "\x1b" not in received[0]

    def test_emits_paste_event_even_with_empty_content(self):
        handler = create_key_handler()
        paste_received = False
        received_paste = "not-empty"

        def on_paste(event: PasteEvent) -> None:
            nonlocal paste_received, received_paste
            paste_received = True
            received_paste = event.text

        handler.on("paste", on_paste)
        handler.process_paste("")
        assert paste_received is True
        assert received_paste == ""


class TestKeyHandlerConstructor:
    def test_constructor_accepts_use_kitty_keyboard_parameter(self):
        handler1 = create_key_handler(False)
        handler2 = create_key_handler(True)
        assert handler1 is not None
        assert handler2 is not None


class TestKeyHandlerEventEmitter:
    def test_event_inheritance_from_event_emitter(self):
        handler = create_key_handler()
        assert callable(handler.on)
        assert callable(handler.emit)
        assert callable(getattr(handler, "remove_listener", None) or getattr(handler, "removeListener", None))


class TestKeyHandlerPreventDefault:
    def test_prevent_default_stops_propagation(self):
        handler = create_key_handler()
        global_called = False
        second_called = False

        def first(key: KeyEvent) -> None:
            nonlocal global_called
            global_called = True
            key.prevent_default()

        def second(key: KeyEvent) -> None:
            nonlocal second_called
            if not key.default_prevented:
                second_called = True

        handler.on("keypress", first)
        handler.on("keypress", second)
        handler.process_input("a")
        assert global_called is True
        assert second_called is False


class TestInternalKeyHandler:
    """Aligns: KeyHandler.test.ts - InternalKeyHandler"""

    def test_on_internal_handlers_run_after_regular_handlers(self):
        handler = create_key_handler()
        call_order: list[str] = []

        handler.on_internal("keypress", lambda key: call_order.append("internal"))
        handler.on("keypress", lambda key: call_order.append("regular"))
        handler.process_input("a")
        assert call_order == ["regular", "internal"]

    def test_prevent_default_prevents_internal_handlers_from_running(self):
        handler = create_key_handler()
        regular_called = False
        internal_called = False

        def set_regular(key: KeyEvent) -> None:
            nonlocal regular_called
            regular_called = True
            key.prevent_default()

        def set_internal(key: KeyEvent) -> None:
            nonlocal internal_called
            internal_called = True

        handler.on("keypress", set_regular)
        handler.on_internal("keypress", lambda key: set_internal())
        handler.process_input("a")
        assert regular_called is True
        assert internal_called is False

    def test_multiple_internal_handlers_can_be_registered(self):
        handler = create_key_handler()
        h1, h2, h3 = [False], [False], [False]

        handler.on_internal("keypress", lambda k: h1.__setitem__(0, True))
        handler.on_internal("keypress", lambda k: h2.__setitem__(0, True))
        handler.on_internal("keypress", lambda k: h3.__setitem__(0, True))
        handler.process_input("a")
        assert h1[0] and h2[0] and h3[0]

    def test_off_internal_removes_specific_handlers(self):
        handler = create_key_handler()
        h1_called, h2_called = False, False

        def internal1(key: KeyEvent) -> None:
            nonlocal h1_called
            h1_called = True

        def internal2(key: KeyEvent) -> None:
            nonlocal h2_called
            h2_called = True

        handler.on_internal("keypress", internal1)
        handler.on_internal("keypress", internal2)
        handler.off_internal("keypress", internal1)
        handler.process_input("a")
        assert h1_called is False
        assert h2_called is True

    def test_emit_returns_true_when_there_are_listeners(self):
        handler = create_key_handler()
        ev = KeyEvent({
            "name": "a", "ctrl": False, "meta": False, "shift": False, "option": False,
            "sequence": "a", "number": False, "raw": "a", "eventType": "press", "source": "raw",
        })
        has_listeners = handler.emit("keypress", ev)
        assert has_listeners is False
        handler.on("keypress", lambda k: None)
        has_listeners = handler.emit(
            "keypress",
            KeyEvent({"name": "b", "ctrl": False, "meta": False, "shift": False, "option": False, "sequence": "b", "number": False, "raw": "b", "eventType": "press", "source": "raw"}),
        )
        assert has_listeners is True

    def test_paste_events_work_with_priority_system(self):
        handler = create_key_handler()
        call_order: list[str] = []
        handler.on("paste", lambda event: call_order.append(f"regular:{event.text}"))
        handler.on_internal("paste", lambda event: call_order.append(f"internal:{event.text}"))
        handler.process_paste("hello")
        assert call_order == ["regular:hello", "internal:hello"]

    def test_paste_prevent_default_prevents_internal_handlers(self):
        handler = create_key_handler()
        regular_called = False
        internal_called = False
        received_text = ""

        def on_paste(event: PasteEvent) -> None:
            nonlocal regular_called, received_text
            regular_called = True
            received_text = event.text
            event.prevent_default()

        handler.on("paste", on_paste)
        def set_internal(event: PasteEvent) -> None:
            nonlocal internal_called
            internal_called = True

        handler.on_internal("paste", set_internal)
        handler.process_paste("test paste")
        assert regular_called is True
        assert received_text == "test paste"
        assert internal_called is False


class TestKeyHandlerFilters:
    def test_filters_out_mouse_events(self):
        handler = create_key_handler()
        keypress_count = 0
        def inc(k: KeyEvent) -> None:
            nonlocal keypress_count
            keypress_count += 1

        handler.on("keypress", inc)
        handler.process_input("\x1b[<0;10;5M")
        assert keypress_count == 0
        handler.process_input("\x1b[<0;10;5m")
        assert keypress_count == 0
        handler.process_input("\x1b[M ab")
        assert keypress_count == 0
        handler.process_input("c")
        assert keypress_count == 1
        handler.process_input("a")
        assert keypress_count == 2


class TestKeyEventSource:
    def test_key_event_has_source_field_raw_by_default(self):
        handler = create_key_handler()
        received: list[KeyEvent] = []
        handler.on("keypress", lambda key: received.append(key))
        handler.process_input("a")
        assert len(received) == 1
        assert received[0].source == "raw"
        assert received[0].name == "a"

    def test_key_event_source_is_kitty_when_using_kitty_keyboard_protocol(self):
        handler = create_key_handler(use_kitty_keyboard=True)
        received: list[KeyEvent] = []
        handler.on("keypress", lambda key: received.append(key))
        handler.process_input("\x1b[97u")
        assert len(received) == 1
        assert received[0].source == "kitty"
        assert received[0].name == "a"


class TestKeyHandlerErrors:
    def test_global_handler_error_is_caught_and_logged(self):
        handler = create_key_handler()
        handler_called = False

        def bad(key: KeyEvent) -> None:
            nonlocal handler_called
            handler_called = True
            raise ValueError("Test error in global handler")

        handler.on("keypress", bad)
        handler.process_input("a")
        assert handler_called is True

    def test_process_input_returns_true_even_when_handler_throws(self):
        handler = create_key_handler()

        def raise_error(k: KeyEvent) -> None:
            raise ValueError("Handler error")

        handler.on("keypress", raise_error)
        result = handler.process_input("a")
        assert result is True

    def test_paste_handler_error_is_caught_and_logged(self):
        handler = create_key_handler()
        handler_called = False

        def bad_paste(event: PasteEvent) -> None:
            nonlocal handler_called
            handler_called = True
            raise ValueError("Test error in paste handler")

        handler.on("paste", bad_paste)
        handler.process_paste("test")
        assert handler_called is True
