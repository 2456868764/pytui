# tests/integration/test_test_renderer_snapshot.py - TestRenderer + Mock + 快照

import pytest

pytest.importorskip("pytui.testing")


def test_test_renderer_with_mock_keys_and_snapshot():
    """挂载 Box+Text，注入按键，render_once，用 assert_buffer_snapshot 校验。"""
    from pytui.components import Box, Text
    from pytui.testing import create_test_renderer, create_mock_keys, assert_buffer_snapshot

    r = create_test_renderer(20, 5)
    box = Box(r.context, {"width": 20, "height": 5, "border": False})
    text = Text(r.context, {"content": "Hello", "width": 20, "height": 1})
    box.add(text)
    r.root.add(box)
    r.render_once()

    expected = ["Hello               ", "                    ", "                    ", "                    ", "                    "]
    assert len(expected) == 5
    assert len(expected[0]) == 20
    assert_buffer_snapshot(r.front_buffer, expected)

    keys = create_mock_keys(r)
    keys.feed("x")
    r.render_once()
    # 内容未变（无 state 更新），快照仍为 Hello
    assert_buffer_snapshot(r.front_buffer, expected)
