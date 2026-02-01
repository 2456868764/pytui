# Phase 2: lib/extmarks (Extmark, ExtmarksStore)

import pytest

from pytui.lib.extmarks import Extmark, ExtmarksStore


def test_extmarks_store_add_remove():
    store = ExtmarksStore()
    eid = store.add(0, 5)
    assert eid == 1
    assert store.get(eid) is not None
    assert store.get(eid).start == 0 and store.get(eid).end == 5
    assert store.remove(eid) is True
    assert store.get(eid) is None
    assert store.remove(999) is False


def test_extmarks_store_get_in_range():
    store = ExtmarksStore()
    store.add(0, 10)
    store.add(5, 15)
    store.add(20, 30)
    out = store.get_in_range(5, 12)
    assert len(out) >= 2
    out = store.get_in_range(100, 200)
    assert len(out) == 0


def test_extmarks_store_clear():
    store = ExtmarksStore()
    store.add(0, 5)
    store.add(10, 15)
    store.clear()
    assert len(store) == 0
