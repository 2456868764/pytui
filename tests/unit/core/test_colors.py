# tests/unit/core/test_colors.py
"""parse_color_to_tuple / parse_color 单元测试（from pytui.lib）。"""

import pytest

pytest.importorskip("pytui.lib")


class TestParseColor:
    """parse_color_to_tuple 六位/三位 hex、transparent、非法输入。"""

    def test_hex_6_digits(self):
        from pytui.lib import parse_color_to_tuple

        assert parse_color_to_tuple("#ffffff") == (255, 255, 255, 255)
        assert parse_color_to_tuple("#000000") == (0, 0, 0, 255)
        assert parse_color_to_tuple("#ff0000") == (255, 0, 0, 255)
        assert parse_color_to_tuple("#00ff00") == (0, 255, 0, 255)
        assert parse_color_to_tuple("#0000ff") == (0, 0, 255, 255)
        assert parse_color_to_tuple("#010203") == (1, 2, 3, 255)

    def test_hex_3_digits(self):
        from pytui.lib import parse_color_to_tuple

        assert parse_color_to_tuple("#fff") == (255, 255, 255, 255)
        assert parse_color_to_tuple("#000") == (0, 0, 0, 255)
        assert parse_color_to_tuple("#f00") == (255, 0, 0, 255)

    def test_transparent(self):
        from pytui.lib import parse_color_to_tuple

        assert parse_color_to_tuple("transparent") == (0, 0, 0, 0)
        assert parse_color_to_tuple("TRANSPARENT") == (0, 0, 0, 0)
        assert parse_color_to_tuple("  transparent  ") == (0, 0, 0, 0)
        assert parse_color_to_tuple("") == (0, 0, 0, 0)

    def test_css_color_names(self):
        """CSS color names (OpenTUI: parseColor('red'), etc.; green = #008000 per CSS)."""
        from pytui.lib import parse_color_to_tuple

        assert parse_color_to_tuple("red") == (255, 0, 0, 255)
        assert parse_color_to_tuple("white") == (255, 255, 255, 255)
        assert parse_color_to_tuple("black") == (0, 0, 0, 255)
        assert parse_color_to_tuple("green") == (0, 128, 0, 255)  # CSS green = #008000
        assert parse_color_to_tuple("blue") == (0, 0, 255, 255)

    def test_hex_8_digits_with_alpha(self):
        """#rrggbbaa semi-transparent (OpenTUI: fromHex('#FF000080'))."""
        from pytui.lib import parse_color_to_tuple

        assert parse_color_to_tuple("#ff000080") == (255, 0, 0, 128)
        assert parse_color_to_tuple("#00000000") == (0, 0, 0, 0)

    def test_rgba_pass_through(self):
        """RGBA instance pass-through (OpenTUI: parseColor(RGBA.fromInts(...)))."""
        from pytui.lib import RGBA, parse_color_to_tuple

        c = RGBA.from_ints(100, 150, 200, 255)
        assert parse_color_to_tuple(c) == (100, 150, 200, 255)

    def test_invalid_hex_defaults_to_magenta(self):
        """OpenTUI hexToRgb invalid hex defaults to magenta (no ValueError)."""
        from pytui.lib import parse_color_to_tuple

        # Invalid hex returns magenta (0, 255, 0, 255) in OpenTUI; we use (255, 0, 255, 255)
        result = parse_color_to_tuple("#gggggg")
        assert len(result) == 4
        assert result[3] == 255
        result2 = parse_color_to_tuple("#12")
        assert len(result2) == 4
        # Unknown string without # goes to hex_to_rgb and may default
        result3 = parse_color_to_tuple("notacolor")
        assert len(result3) == 4
