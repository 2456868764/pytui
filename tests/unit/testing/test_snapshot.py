# tests/unit/testing/test_snapshot.py

import pytest

pytest.importorskip("pytui.testing.snapshot")


class TestSnapshot:
    def test_buffer_snapshot_lines(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.testing.snapshot import buffer_snapshot_lines

        buffer_10x5.set_cell(0, 0, Cell(char="X"))
        buffer_10x5.set_cell(1, 0, Cell(char="Y"))
        lines = buffer_snapshot_lines(buffer_10x5)
        assert len(lines) == 5
        assert len(lines[0]) == 10
        assert lines[0][:2] == "XY"

    def test_assert_buffer_snapshot_pass(self, buffer_10x5):
        from pytui.core.buffer import Cell
        from pytui.testing.snapshot import assert_buffer_snapshot

        buffer_10x5.set_cell(0, 0, Cell(char="A"))
        expected = ["A" + " " * 9] + [" " * 10] * 4
        assert_buffer_snapshot(buffer_10x5, expected)

    def test_assert_buffer_snapshot_fail_mismatch(self, buffer_10x5):
        from pytui.testing.snapshot import assert_buffer_snapshot

        expected = ["X" + " " * 9] + [" " * 10] * 4
        with pytest.raises(AssertionError, match="mismatch"):
            assert_buffer_snapshot(buffer_10x5, expected)
