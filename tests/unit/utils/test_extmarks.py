# tests/unit/utils/test_extmarks.py

import pytest

pytest.importorskip("pytui.lib.extmarks")


class TestExtmarksStore:
    def test_add_remove(self):
        from pytui.lib.extmarks import ExtmarksStore

        s = ExtmarksStore()
        eid = s.add(0, 5, type_id=1)
        assert eid == 1
        assert len(s) == 1
        assert s.remove(eid) is True
        assert len(s) == 0
        assert s.remove(999) is False

    def test_get_in_range(self):
        from pytui.lib.extmarks import ExtmarksStore

        s = ExtmarksStore()
        s.add(0, 3)
        s.add(2, 6)
        s.add(10, 12)
        out = s.get_in_range(1, 5)
        assert len(out) == 2
        out2 = s.get_in_range(0, 2)
        assert len(out2) >= 1
        out3 = s.get_in_range(20, 30)
        assert len(out3) == 0

    def test_clear(self):
        from pytui.lib.extmarks import ExtmarksStore

        s = ExtmarksStore()
        s.add(0, 1)
        s.clear()
        assert len(s) == 0
