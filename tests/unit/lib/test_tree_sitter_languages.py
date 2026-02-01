# tests.unit.lib.test_tree_sitter_languages - get_language, get_parser, list_available_languages (migrated from syntax/languages)

from pathlib import Path
from unittest.mock import MagicMock, patch

from pytui.lib.tree_sitter.languages import (
    COMMON_LANGUAGE_NAMES,
    _language_from_data_path,
    get_language,
    get_parser,
    list_available_languages,
)


class TestCommonLanguageNames:
    def test_is_non_empty_tuple(self):
        assert isinstance(COMMON_LANGUAGE_NAMES, tuple)
        assert len(COMMON_LANGUAGE_NAMES) > 0

    def test_contains_python(self):
        assert "python" in COMMON_LANGUAGE_NAMES


class TestLanguageFromDataPath:
    def test_returns_none_when_tree_sitter_not_installed(self):
        with patch("builtins.__import__") as mock_import:
            def do_import(name, *args, **kwargs):
                if name == "tree_sitter":
                    raise ImportError("no tree_sitter")
                return __import__(name, *args, **kwargs)
            mock_import.side_effect = do_import
            result = _language_from_data_path("python")
            assert result is None

    def test_returns_none_when_lib_file_does_not_exist(self):
        with patch.dict(
            "sys.modules", {"tree_sitter": MagicMock(Language=MagicMock())}
        ):
            with patch(
                "pytui.lib.data_paths.get_data_dir",
                return_value=Path("/nonexistent"),
            ):
                result = _language_from_data_path("python")
        assert result is None


class TestGetLanguage:
    def test_returns_none_when_tree_sitter_not_available(self):
        with patch("builtins.__import__") as mock_import:
            def do_import(name, *args, **kwargs):
                if name == "tree_sitter":
                    raise ImportError("no tree_sitter")
                return __import__(name, *args, **kwargs)
            mock_import.side_effect = do_import
            result = get_language("python")
            assert result is None

    def test_uses_tree_sitter_languages_when_available(self):
        mock_lang = MagicMock()
        mock_tsl = MagicMock()
        mock_tsl.get_language = MagicMock(return_value=mock_lang)
        with patch.dict(
            "sys.modules",
            {
                "tree_sitter": MagicMock(),
                "tree_sitter_languages": mock_tsl,
            },
        ):
            result = get_language("python")
        assert result is mock_lang
        mock_tsl.get_language.assert_called_once_with("python")


class TestGetParser:
    def test_returns_none_when_language_unavailable(self):
        mock_tsl = MagicMock()
        mock_tsl.get_parser = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"tree_sitter_languages": mock_tsl}):
            with patch("pytui.lib.tree_sitter.languages.get_language", return_value=None):
                result = get_parser("python")
        assert result is None

    def test_returns_parser_when_language_available(self):
        mock_lang = MagicMock()
        mock_parser = MagicMock()
        mock_ts = MagicMock()
        mock_ts.Parser.return_value = mock_parser
        mock_tsl = MagicMock()
        mock_tsl.get_parser = MagicMock(return_value=None)
        with patch.dict(
            "sys.modules",
            {"tree_sitter": mock_ts, "tree_sitter_languages": mock_tsl},
        ):
            with patch("pytui.lib.tree_sitter.languages.get_language", return_value=mock_lang):
                result = get_parser("python")
        assert result is mock_parser
        mock_parser.set_language.assert_called_once_with(mock_lang)


class TestListAvailableLanguages:
    def test_returns_list(self):
        result = list_available_languages()
        assert isinstance(result, list)

    def test_returns_sorted(self):
        result = list_available_languages()
        assert result == sorted(result)

    def test_returns_empty_when_tree_sitter_not_installed(self):
        with patch("builtins.__import__") as mock_import:
            def do_import(name, *args, **kwargs):
                if name == "tree_sitter":
                    raise ImportError("no tree_sitter")
                return __import__(name, *args, **kwargs)
            mock_import.side_effect = do_import
            result = list_available_languages()
            assert result == []

    def test_only_includes_languages_that_load(self):
        with patch.dict("sys.modules", {"tree_sitter": MagicMock()}):
            with patch(
                "pytui.lib.tree_sitter.languages.get_language",
                side_effect=lambda name: MagicMock() if name == "python" else None,
            ):
                result = list_available_languages()
                assert result == ["python"]
