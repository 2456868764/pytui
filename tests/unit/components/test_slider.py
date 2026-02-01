# tests/unit/components/test_slider.py - Aligns OpenTUI packages/core/src/renderables/Slider.test.ts
# Value API, viewPortSize, getVirtualThumbSize/getVirtualThumbStart, render (half-blocks █▌▐), onChange.

import pytest

pytest.importorskip("pytui.components.slider")


def _create_slider(ctx, **options):
    from pytui.components.slider import Slider
    return Slider(ctx, {"orientation": "horizontal", **options})


class TestSliderValueBasedAPI:
    """Align OpenTUI: SliderRenderable > Value-based API."""

    def test_value_min_max_and_clamp(self, mock_context):
        from pytui.components.slider import Slider
        s = Slider(mock_context, {"orientation": "horizontal", "min": 0, "max": 100, "value": 50})
        assert s.value == 50
        assert s.min == 0
        assert s.max == 100

        s.value = 75
        assert s.value == 75
        s.value = 150
        assert s.value == 100
        s.value = -10
        assert s.value == 0

        s.min = 20
        assert s.value == 20
        s.max = 80
        s.value = 90
        assert s.value == 80


class TestSliderAutomaticThumbSize:
    """Align OpenTUI: Automatic thumb size calculation."""

    def test_dimensions_and_value(self, mock_context):
        s = _create_slider(mock_context, min=0, max=100, value=50, width=20, height=1)
        s.x, s.y, s.width, s.height = 0, 0, 20, 1
        assert s.width == 20
        assert s.height == 1
        assert s.min == 0
        assert s.max == 100
        assert s.value == 50


class TestSliderViewPortSize:
    """Align OpenTUI: Custom step size (viewPortSize)."""

    def test_view_port_size_get_set_and_clamp(self, mock_context):
        s = _create_slider(mock_context, min=0, max=100, value=50, width=100, height=1, viewPortSize=10)
        s.x, s.y, s.width, s.height = 0, 0, 100, 1
        assert s.viewPortSize == 10
        assert s.view_port_size == 10

        s.viewPortSize = 20
        assert s.viewPortSize == 20
        s.viewPortSize = 150
        assert s.viewPortSize == 100
        s.viewPortSize = 0
        assert s.viewPortSize == 0.01


class TestSliderMinimumThumbSize:
    """Align OpenTUI: Minimum thumb size."""

    def test_vertical_view_port_size_one(self, mock_context):
        from pytui.components.slider import Slider
        s = Slider(mock_context, {"orientation": "vertical", "min": 0, "max": 10000, "value": 0, "width": 2, "height": 100, "viewPortSize": 1})
        s.x, s.y, s.width, s.height = 0, 0, 2, 100
        assert s.viewPortSize == 1
        assert s.min == 0
        assert s.max == 10000


class TestSliderOnChangeCallback:
    """Align OpenTUI: onChange callback."""

    def test_on_change_called_on_value_set(self, mock_context):
        changed_value = []

        def on_change(v):
            changed_value.append(v)

        s = _create_slider(mock_context, min=0, max=100, value=0, onChange=on_change)
        s.value = 42
        assert changed_value == [42]


class TestSliderVirtualThumbSize:
    """Align OpenTUI: getVirtualThumbSize (vertical/horizontal)."""

    def test_vertical_thumb_size_calculation(self, mock_context):
        from pytui.components.slider import Slider
        s = Slider(mock_context, {"orientation": "vertical", "min": 0, "max": 100, "value": 0, "width": 3, "height": 50, "viewPortSize": 10})
        s.x, s.y, s.width, s.height = 0, 0, 3, 50
        thumb_size = s.get_virtual_thumb_size()
        assert thumb_size == 9
        s.viewPortSize = 1
        assert s.get_virtual_thumb_size() == 1
        s.viewPortSize = 150
        assert s.get_virtual_thumb_size() == 50

    def test_horizontal_thumb_size_calculation(self, mock_context):
        s = _create_slider(mock_context, min=0, max=200, value=0, width=80, height=2, viewPortSize=20)
        s.x, s.y, s.width, s.height = 0, 0, 80, 2
        thumb_size = s.get_virtual_thumb_size()
        assert thumb_size == 14
        s.viewPortSize = 40
        assert s.get_virtual_thumb_size() == 26
        s.viewPortSize = 0.1
        assert s.get_virtual_thumb_size() == 1

    def test_edge_cases_thumb_size(self, mock_context):
        from pytui.components.slider import Slider
        s = Slider(mock_context, {"orientation": "vertical", "min": 50, "max": 50, "value": 50, "width": 2, "height": 30, "viewPortSize": 10})
        s.x, s.y, s.width, s.height = 0, 0, 2, 30
        assert s.get_virtual_thumb_size() == 60
        s.min = 0
        s.max = 100000
        s.viewPortSize = 1
        assert s.get_virtual_thumb_size() == 1
        s.max = 30
        s.viewPortSize = 30
        assert s.get_virtual_thumb_size() == 30

    def test_thumb_size_minimum_clamping(self, mock_context):
        s = _create_slider(mock_context, min=0, max=1000, value=0, width=10, height=1, viewPortSize=1)
        s.x, s.y, s.width, s.height = 0, 0, 10, 1
        assert s.get_virtual_thumb_size() == 1

    def test_thumb_size_can_be_less_than_two(self, mock_context):
        s = _create_slider(mock_context, min=0, max=200, value=0, width=20, height=1, viewPortSize=2)
        s.x, s.y, s.width, s.height = 0, 0, 20, 1
        assert s.get_virtual_thumb_size() == 1


class TestSliderRender:
    """Align OpenTUI: render with half-blocks █▌▐ (horizontal), track = backgroundColor (space)."""

    def test_render_self_draws_track_and_thumb(self, mock_context, buffer_10x5):
        from pytui.components.slider import Slider
        s = Slider(mock_context, {"orientation": "horizontal", "min": 0, "max": 100, "value": 0, "width": 10, "height": 1})
        s.x, s.y, s.width, s.height = 0, 0, 10, 1
        s.render_self(buffer_10x5)
        # At value=0 thumb starts at left: first cell is left half-block ▌
        assert buffer_10x5.get_cell(0, 0).char == "▌"
        # Track (non-thumb) is filled with space
        assert buffer_10x5.get_cell(5, 0).char == " "

    def test_render_emit_change(self, mock_context):
        s = _create_slider(mock_context, min=0, max=10, value=5, width=10, height=1)
        events = []
        s.on("change", lambda e: events.append(e))
        s.value = 8
        assert s.value == 8
        assert len(events) == 1
        assert events[0].get("value") == 8


class TestSliderGetThumbRect:
    """Align OpenTUI: getThumbRect for hit test."""

    def test_get_thumb_rect_horizontal(self, mock_context):
        s = _create_slider(mock_context, min=0, max=100, value=0, width=10, height=1)
        s.x, s.y, s.width, s.height = 0, 0, 10, 1
        r = s.get_thumb_rect()
        assert "x" in r and "y" in r and "width" in r and "height" in r
        assert r["width"] >= 1 and r["height"] >= 1
