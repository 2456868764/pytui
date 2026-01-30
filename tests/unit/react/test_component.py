# tests.unit.react.test_component

import pytest

pytest.importorskip("pytui.react.component")


class TestComponent:
    def test_props_and_state(self, mock_context):
        from pytui.react.component import Component

        class C(Component):
            def render(self):
                return None

        c = C(mock_context, {"a": 1})
        assert c.props == {"a": 1}
        assert c.state == {}
        c.state["x"] = 2
        assert c.state["x"] == 2

    def test_set_state_merges(self, mock_context):
        from pytui.react.component import Component

        class C(Component):
            def render(self):
                return None

        c = C(mock_context, {})
        c.state["x"] = 0
        c.set_state({"x": 1})
        assert c.state["x"] == 1
        c.set_state({"y": 2})
        assert c.state["x"] == 1
        assert c.state["y"] == 2

    def test_update_calls_on_update(self, mock_context):
        from pytui.react.component import Component

        class C(Component):
            def render(self):
                return None

        c = C(mock_context, {})
        called = []

        def cb():
            called.append(1)

        c._on_update = [cb]
        c.update()
        assert called == [1]
