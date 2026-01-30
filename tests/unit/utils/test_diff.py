# tests/unit/utils/test_diff.py

import pytest

pytest.importorskip("pytui.utils.diff")


class TestDiff:
    def test_same_text(self):
        from pytui.utils.diff import diff_lines

        out = diff_lines("a\nb", "a\nb")
        assert all(tag == " " for tag, _ in out)
        assert [line for _, line in out] == ["a", "b"]

    def test_single_line_add(self):
        from pytui.utils.diff import diff_lines

        out = diff_lines("a", "a\nb")
        assert (" ", "a") in out
        assert ("+", "b") in out

    def test_single_line_remove(self):
        from pytui.utils.diff import diff_lines

        out = diff_lines("a\nb", "a")
        assert (" ", "a") in out
        assert ("-", "b") in out

    def test_multi_change(self):
        from pytui.utils.diff import diff_lines

        out = diff_lines("x\ny\nz", "x\nb\nz")
        lines = [line for _, line in out]
        assert "x" in lines
        assert "z" in lines
        assert any(tag == "-" and line == "y" for tag, line in out)
        assert any(tag == "+" and line == "b" for tag, line in out)
