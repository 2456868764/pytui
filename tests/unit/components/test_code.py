# tests/unit/components/test_code.py

import pytest

pytest.importorskip("pytui.components.code")


class TestCode:
    def test_render_self_shows_content(self, mock_context, buffer_40x20):
        from pytui.components.code import Code

        c = Code(mock_context, {"content": "x = 1", "width": 40, "height": 5})
        c.x, c.y, c.width, c.height = 0, 0, 40, 5
        c.render_self(buffer_40x20)
        # 行号或代码中应出现 "x" 或 "1"
        found = False
        for y in range(5):
            for x in range(40):
                cell = buffer_40x20.get_cell(x, y)
                if cell and (cell.char == "x" or cell.char == "1"):
                    found = True
                    break
            if found:
                break
        assert found
