# tests.unit.react.test_jsx

import pytest

pytest.importorskip("pytui.react.jsx")


class TestCreateElement:
    def test_h_text_props(self):
        from pytui.react.jsx import create_element, h

        el = h("text", {"content": "Hi", "width": 10})
        assert el["type"] == "text"
        assert el["props"]["content"] == "Hi"
        assert el["props"]["width"] == 10
        assert el["children"] == []

    def test_h_single_string_child_becomes_content(self):
        from pytui.react.jsx import h

        el = h("text", {}, "Hello")
        assert el["props"]["content"] == "Hello"
        assert el["children"] == []

    def test_h_box_with_children(self):
        from pytui.react.jsx import h

        el = h("box", {"width": 40}, h("text", {"content": "A", "width": 1, "height": 1}))
        assert el["type"] == "box"
        assert len(el["children"]) == 1
        assert el["children"][0]["type"] == "text"
        assert el["children"][0]["props"]["content"] == "A"

    def test_h_filters_none(self):
        from pytui.react.jsx import h

        el = h("box", {}, None, h("text", {"content": "x", "width": 1, "height": 1}), None)
        assert len(el["children"]) == 1
