# tests/unit/components/test_diff.py

import pytest

pytest.importorskip("pytui.components.diff")


class TestDiffComponent:
    def test_render_self_shows_diff(self, mock_context, buffer_40x20):
        from pytui.components.diff import Diff

        d = Diff(
            mock_context,
            {"old_text": "a", "new_text": "a\nb", "width": 40, "height": 5},
        )
        d.x, d.y, d.width, d.height = 0, 0, 40, 5
        d.render_self(buffer_40x20)
        # 应有 "+" 或 "b"
        found = False
        for y in range(5):
            for x in range(40):
                cell = buffer_40x20.get_cell(x, y)
                if cell and (cell.char == "+" or cell.char == "b"):
                    found = True
                    break
            if found:
                break
        assert found

    def test_diff_string_and_view(self, mock_context):
        from pytui.components.diff import Diff

        d = Diff(mock_context, {"diff": "+ added\n- removed\n context"})
        assert d.diff == "+ added\n- removed\n context"
        assert d.view == "unified"
        d.diff = "+ only"
        assert d.diff == "+ only"
        d.view = "split"
        assert d.view == "split"
        d.view = "unified"
        assert d.view == "unified"

    def test_set_texts_clears_diff(self, mock_context):
        from pytui.components.diff import Diff

        d = Diff(mock_context, {"diff": "+ x"})
        assert d.diff == "+ x"
        d.set_texts("a", "b")
        assert d.diff == ""
        assert d.old_text == "a"
        assert d.new_text == "b"

    def test_openTUI_color_options_and_defaults(self, mock_context):
        from pytui.components.diff import Diff

        d = Diff(mock_context, {"old_text": "a", "new_text": "b"})
        assert d.added_bg is not None
        assert d.removed_bg is not None
        assert d.added_sign_color is not None
        assert d.removed_sign_color is not None
        assert d.show_line_numbers is True
        assert d.line_number_fg is not None

    def test_camelCase_aliases(self, mock_context, buffer_40x20):
        from pytui.components.diff import Diff

        d = Diff(
            mock_context,
            {
                "old_text": "x",
                "new_text": "y",
                "showLineNumbers": False,
                "addedBg": "#111111",
                "removedSignColor": "#222222",
                "width": 40,
                "height": 5,
            },
        )
        assert d.show_line_numbers is False
        assert d.added_bg is not None
        assert d.removed_sign_color is not None
        d.x, d.y, d.width, d.height = 0, 0, 40, 5
        d.render_self(buffer_40x20)
        found_plus_or_y = False
        for y in range(5):
            for x in range(40):
                cell = buffer_40x20.get_cell(x, y)
                if cell and (cell.char in "+-y"):
                    found_plus_or_y = True
                    break
            if found_plus_or_y:
                break
        assert found_plus_or_y

    def test_unified_diff_renders(self, mock_context, buffer_40x20):
        from pytui.components.diff import Diff

        d = Diff(
            mock_context,
            {"diff": "+ new line\n- old line", "width": 40, "height": 5},
        )
        d.x, d.y, d.width, d.height = 0, 0, 40, 5
        d.render_self(buffer_40x20)
        found_plus = found_minus = False
        for y in range(5):
            for x in range(40):
                cell = buffer_40x20.get_cell(x, y)
                if cell:
                    if cell.char == "+":
                        found_plus = True
                    if cell.char == "-":
                        found_minus = True
            if found_plus and found_minus:
                break
        assert found_plus
        assert found_minus

    def test_split_view_renders(self, mock_context, buffer_40x20):
        from pytui.components.diff import Diff

        d = Diff(
            mock_context,
            {"diff": "@@ -1,2 +1,2 @@\n line1\n-line2\n+new2", "view": "split", "width": 40, "height": 5},
        )
        d.x, d.y, d.width, d.height = 0, 0, 40, 5
        d.render_self(buffer_40x20)
        found_minus = found_plus = False
        for y in range(5):
            for x in range(40):
                cell = buffer_40x20.get_cell(x, y)
                if cell:
                    if cell.char == "-":
                        found_minus = True
                    if cell.char == "+":
                        found_plus = True
        assert found_minus or found_plus

    def test_property_setters_trigger_render(self, mock_context):
        from pytui.components.diff import Diff

        d = Diff(mock_context, {"old_text": "a", "new_text": "b"})
        d.added_bg = "#000000"
        d.removed_bg = "#111111"
        d.show_line_numbers = False
        d.filetype = "python"
        d.view = "split"
        assert d.added_bg is not None
        assert d.show_line_numbers is False
        assert d.filetype == "python"
        assert d.view == "split"

    def test_destroy_recursively(self, mock_context):
        from pytui.components.diff import Diff

        d = Diff(mock_context, {"diff": "+ x"})
        d.destroy_recursively()
        assert getattr(d, "_parse_error", None) is None
        assert getattr(d, "_parsed_patch", None) is None
