# tests/unit/testing/test_renderer.py

import pytest

pytest.importorskip("pytui.testing.test_renderer")


class TestCreateTestRenderer:
    def test_create_test_renderer_has_size(self):
        from pytui.testing.test_renderer import create_test_renderer

        r = create_test_renderer(40, 20)
        assert r.width == 40
        assert r.height == 20
        assert r.terminal.get_size() == (40, 20)

    def test_render_once_no_tty(self):
        from pytui.components.text import Text
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.testing.snapshot import buffer_snapshot_lines

        r = create_test_renderer(10, 3)
        t = Text(r.context, {"content": "Hi", "width": 10, "height": 1})
        r.root.add(t)
        r.render_once()
        lines = buffer_snapshot_lines(r.front_buffer)
        assert lines[0].strip() == "Hi"
