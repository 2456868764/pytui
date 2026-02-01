# tests/unit/components/test_input.py - Aligns with OpenTUI Input.test.ts

import pytest

pytest.importorskip("pytui.components.input")


def _key_event(name: str = "", char: str = "", ctrl: bool = False, shift: bool = False, meta: bool = False):
    """Build key dict for keypress (compatible with KeyEvent getattr/get)."""
    d = {"name": name, "char": char or (name if len(name) == 1 else ""), "ctrl": ctrl, "shift": shift, "meta": meta}
    return d


def _key_event_preventable():
    """Mutable key-like object that supports preventDefault."""
    class MutableKey:
        def __init__(self, name="", char="", ctrl=False, shift=False, meta=False):
            self.name = name
            self.char = char or (name if len(name) == 1 else "")
            self.ctrl = ctrl
            self.shift = shift
            self.meta = meta
            self.default_prevented = False
        def get(self, k, default=None):
            return getattr(self, k, default)
        def prevent_default(self):
            self.default_prevented = True
    return MutableKey


def _emit_key(renderer, name: str = "", char: str = "", **mods):
    k = _key_event(name=name, char=char or (name if len(name) == 1 else ""), **mods)
    renderer.events.emit("keypress", k)


class TestInput:
    def test_set_value(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "", "width": 20, "height": 1})
        i.set_value("hello")
        assert i.value == "hello"
        assert i.cursor_pos == 5

    def test_insert_char_backspace(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "ab", "width": 20, "height": 1})
        i.cursor_pos = 1
        i.insert_char("x")
        assert i.value == "axb"
        assert i.cursor_pos == 2
        i.backspace()
        assert i.value == "ab"
        assert i.cursor_pos == 1

    def test_render_self_shows_value(self, mock_context, buffer_10x5):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "Hi", "width": 10, "height": 1})
        i.x, i.y, i.width, i.height = 0, 0, 10, 1
        i.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "H"
        assert buffer_10x5.get_cell(1, 0).char == "i"

    def test_cursor_position_and_insert_text_delete_character(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "ab", "width": 20, "height": 1})
        assert i.cursor_position == 2
        i.cursor_position = 1
        assert i.cursor_pos == 1
        i.insert_text("XY")
        assert i.value == "aXYb"
        assert i.cursor_position == 3
        i.delete_character("backward")
        assert i.value == "aXb"
        i.delete_character("forward")  # deletes 'b' at cursor
        assert i.value == "aX"

    def test_placeholder_property_and_events(self, mock_context):
        from pytui.components.input import Input, INPUT_EVENT, CHANGE_EVENT, ENTER_EVENT

        i = Input(mock_context, {"value": "x", "width": 10, "height": 1})
        assert i.placeholder == ""
        i.placeholder = "hint"
        assert i.placeholder == "hint"
        events = []
        i.on(INPUT_EVENT, lambda v: events.append(("input", v)))
        i.on(CHANGE_EVENT, lambda v: events.append(("change", v)))
        i.on(ENTER_EVENT, lambda v: events.append(("enter", v)))
        i.value = "y"
        assert ("input", "y") in events
        i.blur()
        assert any(e[0] == "change" for e in events)

    def test_initialization_default_options(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"width": 20, "height": 1})
        r.root.add(i)
        assert i.value == ""
        assert i.focusable is True
        assert i.width >= 0 and i.height >= 0

    def test_initialization_custom_options(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "test", "placeholder": "Enter text", "maxLength": 50, "width": 20, "height": 1})
        r.root.add(i)
        assert i.value == "test"
        assert i.focusable is True

    def test_focus_blur_correctly(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "test", "width": 20, "height": 1})
        r.root.add(i)
        assert i.focused is False
        i.focus()
        assert i.focused is True
        i.blur()
        assert i.focused is False

    def test_emit_change_on_blur_if_value_changed(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, INPUT_EVENT, CHANGE_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "initial", "width": 20, "height": 1})
        r.root.add(i)
        change_fired = []
        i.on(CHANGE_EVENT, lambda v: change_fired.append(v))
        i.focus()
        i.value = "modified"
        assert len(change_fired) == 0
        i.blur()
        assert len(change_fired) == 1
        assert change_fired[0] == "modified"

    def test_no_change_on_blur_if_unchanged(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, CHANGE_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "unchanged", "width": 20, "height": 1})
        r.root.add(i)
        change_fired = []
        i.on(CHANGE_EVENT, lambda: change_fired.append(1))
        i.focus()
        i.blur()
        assert len(change_fired) == 0

    def test_text_input_when_focused(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, INPUT_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        input_vals = []
        i.on(INPUT_EVENT, lambda v: input_vals.append(v))
        _emit_key(r, "h")
        assert i.value == "h"
        assert input_vals and input_vals[-1] == "h"
        _emit_key(r, "e")
        _emit_key(r, "l")
        _emit_key(r, "l")
        _emit_key(r, "o")
        assert i.value == "hello"

    def test_not_handle_keys_when_not_focused(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, INPUT_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"width": 20, "height": 1})
        r.root.add(i)
        input_fired = []
        i.on(INPUT_EVENT, lambda: input_fired.append(1))
        _emit_key(r, "a")
        assert i.value == ""
        assert len(input_fired) == 0

    def test_backspace_correctly(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "hello", "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        _emit_key(r, name="backspace", char="\x08")
        assert i.value == "hell"
        _emit_key(r, name="backspace")
        assert i.value == "hel"

    def test_delete_correctly(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "hello", "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        i.cursor_offset = 1
        _emit_key(r, "delete")
        assert i.value == "hllo"

    def test_arrow_keys_cursor_movement(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "hello", "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        assert i.cursor_offset == 5
        _emit_key(r, "left")
        assert i.cursor_offset == 4
        _emit_key(r, "left")
        assert i.cursor_offset == 3
        _emit_key(r, "right")
        assert i.cursor_offset == 4
        _emit_key(r, "home")
        assert i.cursor_offset == 0
        _emit_key(r, "end")
        assert i.cursor_offset == 5

    def test_enter_key_emits_enter_event(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, ENTER_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "test input", "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        enter_fired = []
        i.on(ENTER_EVENT, lambda v: enter_fired.append(v))
        _emit_key(r, "enter", "\r")
        assert len(enter_fired) == 1
        assert enter_fired[0] == "test input"

    def test_max_length_respected(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"maxLength": 3, "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        _emit_key(r, "a")
        assert i.value == "a"
        _emit_key(r, "b")
        assert i.value == "ab"
        _emit_key(r, "c")
        assert i.value == "abc"
        _emit_key(r, "d")
        assert i.value == "abc"

    def test_cursor_position_with_text_insertion(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "hello", "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        i.cursor_offset = 2
        _emit_key(r, "x")
        assert i.value == "hexllo"
        assert i.cursor_offset == 3

    def test_value_setting_moves_cursor_to_end(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"width": 20, "height": 1})
        i.value = "programmatic"
        assert i.value == "programmatic"
        assert i.cursor_offset == len("programmatic")

    def test_value_change_cursor_to_end(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "hello", "width": 20, "height": 1})
        r.root.add(i)
        i.focus()
        i.cursor_offset = 2
        i.value = "world"
        assert i.value == "world"
        assert i.cursor_offset == 5

    def test_empty_value_setting(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "not empty", "width": 20, "height": 1})
        r.root.add(i)
        i.value = ""
        assert i.value == ""
        assert i.cursor_offset == 0

    def test_emit_input_on_programmatic_value_change(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, INPUT_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"width": 20, "height": 1})
        r.root.add(i)
        input_fired = []
        i.on(INPUT_EVENT, lambda v: input_fired.append(v))
        i.value = "changed"
        assert len(input_fired) == 1
        assert input_fired[0] == "changed"

    def test_max_length_truncates_existing_value(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "verylongtext", "maxLength": 20, "width": 20, "height": 1})
        r.root.add(i)
        assert i.value == "verylongtext"
        i.maxLength = 5
        assert i.value == "veryl"

    def test_plain_text_alias(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "foo", "width": 10, "height": 1})
        assert i.plain_text == "foo"
        assert i.plain_text == i.value

    def test_delete_char_backward_returns_bool(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "ab", "width": 10, "height": 1})
        i.cursor_offset = 1
        assert i.delete_char_backward() is True
        assert i.value == "b"
        assert i.cursor_offset == 0
        assert i.delete_char_backward() is False  # at start, nothing to delete
        i.cursor_offset = 1
        assert i.delete_char_backward() is True
        assert i.value == ""
        assert i.delete_char_backward() is False

    def test_delete_char_returns_bool(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "ab", "width": 10, "height": 1})
        i.cursor_offset = 0
        assert i.delete_char() is True
        assert i.value == "b"
        i.cursor_offset = 1
        assert i.delete_char() is False

    def test_submit_returns_true(self, mock_context):
        from pytui.components.input import Input, ENTER_EVENT

        i = Input(mock_context, {"value": "x", "width": 10, "height": 1})
        entered = []
        i.on(ENTER_EVENT, lambda v: entered.append(v))
        assert i.submit() is True
        assert len(entered) == 1

    def test_global_prevent_default_blocks_input(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, INPUT_EVENT

        r = create_test_renderer(40, 24)
        i = Input(r.context, {"value": "initial", "width": 20, "height": 1})
        r.root.add(i)
        MutableKey = _key_event_preventable()

        def global_handler(key):
            if key.name == "a":
                key.prevent_default()

        r.events.on("keypress", global_handler)
        input_fired = []
        i.on(INPUT_EVENT, lambda v: input_fired.append(1))
        i.focus()
        k = MutableKey("a", "a")
        r.events.emit("keypress", k)
        assert i.value == "initial"
        assert len(input_fired) == 0
        k2 = MutableKey("b", "b")
        r.events.emit("keypress", k2)
        assert i.value == "initialb"
        assert len(input_fired) == 1
        r.events.remove_listener("keypress", global_handler)

    def test_only_one_input_focused_at_a_time(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input

        r = create_test_renderer(40, 24)
        i1 = Input(r.context, {"value": "first", "width": 20, "height": 1})
        i2 = Input(r.context, {"value": "second", "width": 20, "height": 1})
        r.root.add(i1)
        r.root.add(i2)
        assert i1.focused is False
        assert i2.focused is False
        i1.focus()
        assert i1.focused is True
        assert i2.focused is False
        i2.focus()
        assert i1.focused is False
        assert i2.focused is True

    def test_key_events_only_for_focused_input(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, INPUT_EVENT

        r = create_test_renderer(40, 24)
        i1 = Input(r.context, {"value": "first", "width": 20, "height": 1})
        i2 = Input(r.context, {"value": "second", "width": 20, "height": 1})
        r.root.add(i1)
        r.root.add(i2)
        f1 = []
        f2 = []
        i1.on(INPUT_EVENT, lambda v: f1.append(1))
        i2.on(INPUT_EVENT, lambda v: f2.append(1))
        i1.focus()
        _emit_key(r, "a")
        assert len(f1) == 1
        assert len(f2) == 0
        assert i1.value == "firsta"
        assert i2.value == "second"
        i2.focus()
        f1.clear()
        f2.clear()
        _emit_key(r, "b")
        assert len(f1) == 0
        assert len(f2) == 1
        assert i1.value == "firsta"
        assert i2.value == "secondb"

    def test_focus_switch_emits_change_for_previous(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.components.input import Input, CHANGE_EVENT

        r = create_test_renderer(40, 24)
        i1 = Input(r.context, {"value": "first", "width": 20, "height": 1})
        i2 = Input(r.context, {"value": "second", "width": 20, "height": 1})
        r.root.add(i1)
        r.root.add(i2)
        c1 = []
        c2 = []
        i1.on(CHANGE_EVENT, lambda v: c1.append(1))
        i2.on(CHANGE_EVENT, lambda v: c2.append(1))
        i1.focus()
        _emit_key(r, "x")
        i2.focus()
        assert len(c1) == 1
        assert len(c2) == 0
        assert i1.focused is False
        assert i2.focused is True

    def test_new_line_returns_false(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"width": 10, "height": 1})
        assert i.new_line() is False

    def test_value_strips_newlines(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "a\nb\r\nc", "width": 20, "height": 1})
        assert i.value == "abc"

    def test_insert_text_strips_newlines(self, mock_context):
        from pytui.components.input import Input

        i = Input(mock_context, {"value": "", "width": 20, "height": 1})
        i.insert_text("x\ny\r\nz")
        assert i.value == "xyz"
