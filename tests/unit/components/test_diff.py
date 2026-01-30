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
