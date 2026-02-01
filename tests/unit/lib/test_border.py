# Aligns with OpenTUI lib/border.test.ts - isValidBorderStyle, parseBorderStyle

import logging

import pytest

from pytui.lib.border import (
    VALID_BORDER_STYLES,
    is_valid_border_style,
    parse_border_style,
)


class TestIsValidBorderStyle:
    """Aligns: border.test.ts - describe('isValidBorderStyle')"""

    def test_returns_true_for_valid_border_styles(self):
        assert is_valid_border_style("single") is True
        assert is_valid_border_style("double") is True
        assert is_valid_border_style("rounded") is True
        assert is_valid_border_style("heavy") is True

    def test_returns_false_for_invalid_border_styles(self):
        assert is_valid_border_style("invalid") is False
        assert is_valid_border_style("") is False
        assert is_valid_border_style(None) is False
        assert is_valid_border_style(123) is False
        assert is_valid_border_style({}) is False
        assert is_valid_border_style([]) is False


class TestParseBorderStyle:
    """Aligns: border.test.ts - describe('parseBorderStyle')"""

    def test_returns_valid_border_styles_unchanged(self):
        assert parse_border_style("single") == "single"
        assert parse_border_style("double") == "double"
        assert parse_border_style("rounded") == "rounded"
        assert parse_border_style("heavy") == "heavy"

    def test_falls_back_to_single_for_invalid_string_values(self, caplog):
        with caplog.at_level(logging.WARNING):
            assert parse_border_style("invalid") == "single"
            assert parse_border_style("") == "single"
            assert parse_border_style("SINGLE") == "single"  # case sensitive
            assert parse_border_style("Single") == "single"

    def test_falls_back_to_custom_fallback_for_invalid_values(self, caplog):
        with caplog.at_level(logging.WARNING):
            assert parse_border_style("invalid", fallback="double") == "double"
            assert parse_border_style("invalid", fallback="rounded") == "rounded"
            assert parse_border_style("invalid", fallback="heavy") == "heavy"

    def test_falls_back_silently_for_none_without_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            assert parse_border_style(None) == "single"
            assert parse_border_style(None, fallback="double") == "double"
        assert not [r for r in caplog.records if r.levelname == "WARNING"]

    def test_logs_warning_for_invalid_non_null_values(self, caplog):
        with caplog.at_level(logging.WARNING):
            parse_border_style("invalid-style")
        assert len(caplog.records) == 1
        assert "Invalid borderStyle \"invalid-style\"" in caplog.records[0].message
        assert "falling back to \"single\"" in caplog.records[0].message
        assert "single, double, rounded, heavy" in caplog.records[0].message

    def test_regression_handles_invalid_value_types(self, caplog):
        """Aligns: border.test.ts - regression: does not crash with unexpected value types"""
        with caplog.at_level(logging.WARNING):
            assert parse_border_style(123) == "single"
            assert parse_border_style({}) == "single"
            assert parse_border_style(True) == "single"
            assert parse_border_style(lambda: "single") == "single"
