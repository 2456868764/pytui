# tests/unit/components/test_scrollbox.py

import pytest

pytest.importorskip("pytui.components.scrollbox")


class TestScrollbox:
    def test_scroll_up_down_default(self, mock_context):
        from pytui.components.scrollbox import Scrollbox

        s = Scrollbox(mock_context, {"width": 20, "height": 10})
        assert s.scroll_y == 0
        s.scroll_down()
        assert s.scroll_y == 1
        s.scroll_down()
        assert s.scroll_y == 2
        s.scroll_up()
        assert s.scroll_y == 1
        s.scroll_up()
        assert s.scroll_y == 0
        s.scroll_up()
        assert s.scroll_y == 0

    def test_scroll_with_acceleration(self, mock_context):
        from pytui.components.scrollbox import Scrollbox
        from pytui.utils.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel(threshold1=100, threshold2=50, multiplier1=2, multiplier2=4)
        s = Scrollbox(
            mock_context,
            {"width": 20, "height": 10, "scroll_acceleration": accel},
        )
        assert s.scroll_y == 0
        s.scroll_down()
        assert s.scroll_y >= 1
        s.scroll_down()
        assert s.scroll_y >= 2

    def test_set_scroll(self, mock_context):
        from pytui.components.scrollbox import Scrollbox

        s = Scrollbox(mock_context, {"width": 20, "height": 10})
        s.set_scroll(0, 5)
        assert s.scroll_x == 0
        assert s.scroll_y == 5
        s.set_scroll(3, 0)
        assert s.scroll_x == 3
        assert s.scroll_y == 0
