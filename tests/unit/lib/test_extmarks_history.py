import pytest

from pytui.lib.extmarks_history import ExtmarksHistory, ExtmarksSnapshot


def test_save_snapshot_and_undo():
    h = ExtmarksHistory()
    em = {1: {"id": 1, "start": 0, "end": 5, "virtual": False, "typeId": 0}}
    h.save_snapshot(em, 2)
    assert h.can_undo() is True
    assert h.can_redo() is False
    snap = h.undo()
    assert snap is not None
    assert snap["nextId"] == 2
    assert 1 in snap["extmarks"]
    assert h.can_undo() is False


def test_redo():
    h = ExtmarksHistory()
    em = {1: {"id": 1, "start": 0, "end": 5, "typeId": 0}}
    h.save_snapshot(em, 2)
    snap1 = h.undo()
    assert snap1 is not None
    h.push_redo(snap1)
    assert h.can_redo() is True
    snap2 = h.redo()
    assert snap2 == snap1


def test_save_clears_redo():
    h = ExtmarksHistory()
    h.save_snapshot({1: {"id": 1, "start": 0, "end": 5, "typeId": 0}}, 2)
    snap = h.undo()
    assert snap is not None
    h.push_redo(snap)
    h.save_snapshot({2: {"id": 2, "start": 0, "end": 3, "typeId": 0}}, 3)
    assert h.can_redo() is False


def test_clear():
    h = ExtmarksHistory()
    h.save_snapshot({1: {"id": 1, "start": 0, "end": 5, "typeId": 0}}, 2)
    h.clear()
    assert h.can_undo() is False
    assert h.can_redo() is False
    assert h.undo() is None
    assert h.redo() is None


def test_push_undo_push_redo():
    h = ExtmarksHistory()
    snap: ExtmarksSnapshot = {"extmarks": {1: {"id": 1, "start": 0, "end": 5, "typeId": 0}}, "nextId": 2}
    h.push_undo(snap)
    assert h.undo() == snap
    h.push_redo(snap)
    assert h.redo() == snap
