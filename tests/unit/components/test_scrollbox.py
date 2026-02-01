# tests/unit/components/test_scrollbox.py

import pytest

pytest.importorskip("pytui.components.scrollbox")


class TestScrollbox:
    def test_scroll_up_down_default(self, mock_context):
        from pytui.components.box import Box
        from pytui.components.scrollbox import Scrollbox

        s = Scrollbox(mock_context, {"width": 20, "height": 10})
        # Add a tall child so scroll_height > height and scroll_top can change
        child = Box(mock_context, {"width": 20, "height": 30})
        child.x, child.y, child.width, child.height = 0, 0, 20, 30
        s.children.append(child)
        s.x, s.y, s.width, s.height = 0, 0, 20, 10
        assert s.scroll_height == 30
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
        from pytui.components.box import Box
        from pytui.components.scrollbox import Scrollbox
        from pytui.lib.scroll_acceleration import MacOSScrollAccel

        accel = MacOSScrollAccel()  # OpenTUI-aligned: A, tau, max_multiplier
        s = Scrollbox(
            mock_context,
            {"width": 20, "height": 10, "scroll_acceleration": accel},
        )
        child = Box(mock_context, {"width": 20, "height": 30})
        child.x, child.y, child.width, child.height = 0, 0, 20, 30
        s.children.append(child)
        s.x, s.y, s.width, s.height = 0, 0, 20, 10
        assert s.scroll_y == 0
        s.scroll_down()
        assert s.scroll_y >= 1
        s.scroll_down()
        assert s.scroll_y >= 2

    def test_set_scroll(self, mock_context):
        from pytui.components.box import Box
        from pytui.components.scrollbox import Scrollbox

        s = Scrollbox(mock_context, {"width": 20, "height": 10})
        # Child larger than viewport so both scroll_top and scroll_left can change
        child = Box(mock_context, {"width": 25, "height": 30})
        child.x, child.y, child.width, child.height = 0, 0, 25, 30
        s.children.append(child)
        s.x, s.y, s.width, s.height = 0, 0, 20, 10
        s.set_scroll(0, 5)
        assert s.scroll_x == 0
        assert s.scroll_y == 5
        s.set_scroll(3, 0)
        assert s.scroll_x == 3
        assert s.scroll_y == 0
