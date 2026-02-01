# tests/unit/components/test_slider.py

import pytest

pytest.importorskip("pytui.components.slider")


class TestSlider:
    def test_value_property(self, mock_context):
        from pytui.components.slider import Slider

        s = Slider(
            mock_context,
            {"min": 0, "max": 100, "value": 50, "width": 10, "height": 1},
        )
        assert s.value == 50.0

    def test_set_value_clamps_and_emits(self, mock_context):
        from pytui.components.slider import Slider

        s = Slider(
            mock_context,
            {"min": 0, "max": 10, "value": 5, "width": 10, "height": 1},
        )
        events = []
        s.on("change", lambda e: events.append(e))
        s.set_value(8)
        assert s.value == 8
        assert len(events) == 1 and (events[0].get("value") == 8 if isinstance(events[0], dict) else events[0] == 8)
        s.set_value(100)
        assert s.value == 10
        s.set_value(-1)
        assert s.value == 0

    def test_value_to_pos_and_pos_to_value(self, mock_context):
        from pytui.components.slider import Slider

        s = Slider(
            mock_context,
            {"min": 0, "max": 100, "value": 0, "width": 10, "height": 1},
        )
        s.x, s.y, s.width, s.height = 0, 0, 10, 1
        assert s._value_to_pos() == 0
        s._value = 100
        assert s._value_to_pos() == 9
        assert s._pos_to_value(0) == 0.0
        assert s._pos_to_value(9) == 100.0

    def test_render_self_draws_track_and_thumb(self, mock_context, buffer_10x5):
        from pytui.components.slider import Slider

        s = Slider(
            mock_context,
            {"min": 0, "max": 100, "value": 0, "width": 10, "height": 1},
        )
        s.x, s.y, s.width, s.height = 0, 0, 10, 1
        s.render_self(buffer_10x5)
        assert buffer_10x5.get_cell(0, 0).char == "●"
        assert buffer_10x5.get_cell(5, 0).char == "─"
