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

    def test_parse_unified_diff(self):
        from pytui.utils.diff import parse_unified_diff

        out = parse_unified_diff("+ new\n- old\n context")
        assert out == [("+", " new"), ("-", " old"), (" ", "context")]
        out2 = parse_unified_diff("+line\n")
        assert out2 == [("+", "line")]
        out3 = parse_unified_diff("--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n+new")
        assert any(tag == "-" for tag, _ in out3)
        assert any(tag == "+" for tag, _ in out3)

    def test_parse_patch_and_flattened(self):
        from pytui.utils.diff import parse_patch, flattened_unified_lines, build_split_logical_lines

        patch, err = parse_patch("@@ -1,2 +1,2 @@\n line1\n-line2\n+new2")
        assert err is None
        assert patch is not None
        assert len(patch.hunks) == 1
        assert patch.hunks[0].old_start == 1
        assert patch.hunks[0].new_start == 1
        assert len(patch.hunks[0].lines) == 3
        flat = flattened_unified_lines(patch)
        assert len(flat) == 3
        assert flat[0][0] == " " and flat[0][2] == 1 and flat[0][3] == 1
        assert flat[1][0] == "-"
        assert flat[2][0] == "+"
        left, right = build_split_logical_lines(patch)
        assert len(left) == len(right)
        assert left[0].type == "context"
        assert left[1].type == "remove"
        assert right[1].type == "add"

    def test_parse_patch_no_hunks(self):
        from pytui.utils.diff import parse_patch

        patch, err = parse_patch("+only\n-no @@")
        assert patch is None
        assert err == "No valid hunks found"
