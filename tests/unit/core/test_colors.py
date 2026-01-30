# tests/unit/core/test_colors.py
"""parse_color 单元测试。"""

import pytest

pytest.importorskip("pytui.core.colors")


class TestParseColor:
    """parse_color 六位/三位 hex、transparent、非法输入。"""

    def test_hex_6_digits(self):
        from pytui.core.colors import parse_color

        assert parse_color("#ffffff") == (255, 255, 255, 255)
        assert parse_color("#000000") == (0, 0, 0, 255)
        assert parse_color("#ff0000") == (255, 0, 0, 255)
        assert parse_color("#00ff00") == (0, 255, 0, 255)
        assert parse_color("#0000ff") == (0, 0, 255, 255)
        assert parse_color("#010203") == (1, 2, 3, 255)

    def test_hex_3_digits(self):
        from pytui.core.colors import parse_color

        assert parse_color("#fff") == (255, 255, 255, 255)
        assert parse_color("#000") == (0, 0, 0, 255)
        assert parse_color("#f00") == (255, 0, 0, 255)

    def test_transparent(self):
        from pytui.core.colors import parse_color

        assert parse_color("transparent") == (0, 0, 0, 0)
        assert parse_color("TRANSPARENT") == (0, 0, 0, 0)
        assert parse_color("  transparent  ") == (0, 0, 0, 0)
        assert parse_color("") == (0, 0, 0, 0)

    def test_invalid_hex_raises(self):
        from pytui.core.colors import parse_color

        with pytest.raises(ValueError, match="Invalid hex color|Unsupported"):
            parse_color("#gggggg")
        with pytest.raises(ValueError, match="Invalid hex color|Unsupported"):
            parse_color("#12")  # wrong length
        with pytest.raises(ValueError, match="Unsupported"):
            parse_color("red")
