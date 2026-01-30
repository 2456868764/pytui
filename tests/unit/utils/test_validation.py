# tests.unit.utils.test_validation

import pytest

pytest.importorskip("pytui.utils.validation")


class TestValidation:
    """合法/非法参数；错误信息。"""

    def test_validate_positive_int_ok(self):
        from pytui.utils.validation import validate_positive_int

        assert validate_positive_int(1) == 1
        assert validate_positive_int(42) == 42

    def test_validate_positive_int_invalid_type(self):
        from pytui.utils.validation import validate_positive_int

        with pytest.raises(ValueError, match="must be int"):
            validate_positive_int("1")
        with pytest.raises(ValueError, match="must be int"):
            validate_positive_int(1.0)

    def test_validate_positive_int_non_positive(self):
        from pytui.utils.validation import validate_positive_int

        with pytest.raises(ValueError, match="must be positive"):
            validate_positive_int(0)
        with pytest.raises(ValueError, match="must be positive"):
            validate_positive_int(-1)

    def test_validate_non_negative_int_ok(self):
        from pytui.utils.validation import validate_non_negative_int

        assert validate_non_negative_int(0) == 0
        assert validate_non_negative_int(1) == 1

    def test_validate_non_negative_int_negative(self):
        from pytui.utils.validation import validate_non_negative_int

        with pytest.raises(ValueError, match="must be non-negative"):
            validate_non_negative_int(-1)

    def test_validate_hex_color_ok(self):
        from pytui.utils.validation import validate_hex_color

        assert validate_hex_color("#fff") == "#fff"
        assert validate_hex_color("#ffffff") == "#ffffff"
        assert validate_hex_color("transparent") == "transparent"
        assert validate_hex_color("  #abc  ") == "  #abc  "

    def test_validate_hex_color_invalid(self):
        from pytui.utils.validation import validate_hex_color

        with pytest.raises(ValueError, match="must be str"):
            validate_hex_color(123)
        with pytest.raises(ValueError, match="#rgb, #rrggbb"):
            validate_hex_color("red")
        with pytest.raises(ValueError, match="#rgb, #rrggbb"):
            validate_hex_color("#ggg")
