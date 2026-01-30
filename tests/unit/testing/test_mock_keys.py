# tests/unit/testing/test_mock_keys.py

import pytest

pytest.importorskip("pytui.testing.mock_keys")


class TestMockKeys:
    def test_feed_emits_keypress(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.testing.mock_keys import create_mock_keys

        r = create_test_renderer(20, 10)
        keys = create_mock_keys(r)
        seen = []

        def on_key(k):
            seen.append(k)

        r.events.on("keypress", on_key)
        keys.feed("a")
        assert len(seen) == 1
        assert seen[0].get("char") == "a"

    def test_feed_csi_arrow(self):
        from pytui.testing.test_renderer import create_test_renderer
        from pytui.testing.mock_keys import create_mock_keys

        r = create_test_renderer(20, 10)
        keys = create_mock_keys(r)
        seen = []

        r.events.on("keypress", lambda k: seen.append(k))
        keys.feed("\x1b[C")
        assert len(seen) == 1
        assert seen[0].get("name") == "right"
