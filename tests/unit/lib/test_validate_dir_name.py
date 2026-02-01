# Aligns with OpenTUI lib/validate-dir-name.ts - isValidDirectoryName

import pytest

from pytui.lib.validate_dir_name import is_valid_directory_name


class TestIsValidDirectoryName:
    """Aligns: validate-dir-name - isValidDirectoryName"""

    def test_returns_false_for_empty_or_non_string(self):
        assert is_valid_directory_name("") is False
        assert is_valid_directory_name("   ") is False
        assert is_valid_directory_name(None) is False  # type: ignore[arg-type]

    def test_returns_false_for_reserved_names(self):
        for name in ("CON", "PRN", "AUX", "NUL", "COM1", "LPT1"):
            assert is_valid_directory_name(name) is False
            assert is_valid_directory_name(name.lower()) is False

    def test_returns_false_for_invalid_chars(self):
        assert is_valid_directory_name("dir<name") is False
        assert is_valid_directory_name("dir>name") is False
        assert is_valid_directory_name('dir"name') is False
        assert is_valid_directory_name("dir|name") is False
        assert is_valid_directory_name("dir?name") is False
        assert is_valid_directory_name("dir*name") is False
        assert is_valid_directory_name("dir\\name") is False
        assert is_valid_directory_name("dir/name") is False

    def test_returns_false_for_trailing_dot_or_space(self):
        assert is_valid_directory_name("dir.") is False
        assert is_valid_directory_name("dir ") is False

    def test_returns_false_for_dot_and_dotdot(self):
        assert is_valid_directory_name(".") is False
        assert is_valid_directory_name("..") is False

    def test_returns_true_for_valid_names(self):
        assert is_valid_directory_name("my_dir") is True
        assert is_valid_directory_name("docs") is True
        assert is_valid_directory_name("a") is True
