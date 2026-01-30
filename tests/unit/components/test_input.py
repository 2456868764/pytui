# tests/unit/components/test_input.py

import pytest

pytest.importorskip("pytui.components.input")


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
