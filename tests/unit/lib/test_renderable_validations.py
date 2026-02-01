# Phase 2: lib/renderable_validations (validate_options, is_valid_percentage, etc.)

import pytest

from pytui.lib.renderable_validations import (
    is_dimension_type,
    is_flex_basis_type,
    is_margin_type,
    is_overflow_type,
    is_padding_type,
    is_position_type,
    is_position_type_type,
    is_size_type,
    is_valid_percentage,
    validate_hex_color,
    validate_non_negative_int,
    validate_options,
    validate_positive_int,
)


def test_validate_options_width_negative():
    with pytest.raises(TypeError, match="Invalid width"):
        validate_options("id", {"width": -1, "height": 10})


def test_validate_options_height_negative():
    with pytest.raises(TypeError, match="Invalid height"):
        validate_options("id", {"width": 10, "height": -1})


def test_validate_options_ok():
    validate_options("id", {"width": 0, "height": 0})
    validate_options("id", {})


def test_is_valid_percentage():
    assert is_valid_percentage("50%") is True
    assert is_valid_percentage("100%") is True
    assert is_valid_percentage("0%") is True
    assert is_valid_percentage("50") is False
    assert is_valid_percentage(50) is False


def test_is_margin_type():
    assert is_margin_type(0) is True
    assert is_margin_type("auto") is True
    assert is_margin_type("50%") is True
    assert is_margin_type("x") is False


def test_is_padding_type():
    assert is_padding_type(0) is True
    assert is_padding_type("50%") is True


def test_is_position_type():
    assert is_position_type(0) is True
    assert is_position_type("auto") is True
    assert is_position_type("50%") is True


def test_is_position_type_type():
    assert is_position_type_type("relative") is True
    assert is_position_type_type("absolute") is True
    assert is_position_type_type("static") is False


def test_is_overflow_type():
    assert is_overflow_type("visible") is True
    assert is_overflow_type("hidden") is True
    assert is_overflow_type("scroll") is True
    assert is_overflow_type("auto") is False


def test_is_dimension_type():
    assert is_dimension_type(0) is True
    assert is_dimension_type("auto") is True


def test_is_flex_basis_type():
    assert is_flex_basis_type(None) is True
    assert is_flex_basis_type("auto") is True
    assert is_flex_basis_type(0) is True
    assert is_flex_basis_type("50%") is False


def test_is_size_type():
    assert is_size_type(None) is True
    assert is_size_type(0) is True
    assert is_size_type("50%") is True


def test_validate_positive_int():
    assert validate_positive_int(1) == 1
    with pytest.raises(ValueError):
        validate_positive_int(0)
    with pytest.raises(ValueError):
        validate_positive_int("x")


def test_validate_non_negative_int():
    assert validate_non_negative_int(0) == 0
    assert validate_non_negative_int(1) == 1
    with pytest.raises(ValueError):
        validate_non_negative_int(-1)


def test_validate_hex_color():
    assert validate_hex_color("#fff") == "#fff"
    assert validate_hex_color("#ffffff") == "#ffffff"
    assert validate_hex_color("transparent") == "transparent"
    with pytest.raises(ValueError):
        validate_hex_color("x")
