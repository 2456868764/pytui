# tests/unit/components/test_text.py

import pytest

pytest.importorskip("pytui.components.text")


class TestText:
    def test_set_content_triggers_request_render(self, mock_context):
        from pytui.components.text import Text

        t = Text(mock_context, {"content": "a", "width": 10, "height": 1})
        t.request_render = lambda: None
        t.set_content("b")
        assert t.content == "b"

    def test_render_self_draws_content(self, mock_context, buffer_10x5):
        from pytui.components.text import Text

        t = Text(mock_context, {"content": "Hi", "width": 10, "height": 1})
        t.x, t.y, t.width, t.height = 0, 0, 10, 1
        t.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "H"
        assert buffer_10x5.get_cell(1, 0).char == "i"

    def test_render_self_multiline_clips(self, mock_context, buffer_10x5):
        from pytui.components.text import Text

        t = Text(mock_context, {"content": "ab\ncd", "width": 10, "height": 2})
        t.x, t.y, t.width, t.height = 0, 0, 10, 2
        t.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "a"
        assert buffer_10x5.get_cell(1, 0).char == "b"
        assert buffer_10x5.get_cell(0, 1).char == "c"
        assert buffer_10x5.get_cell(1, 1).char == "d"
