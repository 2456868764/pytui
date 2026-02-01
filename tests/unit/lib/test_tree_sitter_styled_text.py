# Unit tests for pytui.lib.tree_sitter_styled_text - aligned with OpenTUI tree-sitter-styled-text

from __future__ import annotations

from typing import Any

import pytest

from pytui.lib.styled_text import StyledText, create_text_attributes
from pytui.lib.tree_sitter_styled_text import (
    ConcealOptions,
    SyntaxStyleProtocol,
    tree_sitter_to_text_chunks,
    tree_sitter_to_styled_text,
)


class _MockSyntaxStyle(SyntaxStyleProtocol):
    def __init__(self) -> None:
        self._styles: dict[str, dict[str, Any]] = {
            "default": {"fg": (1.0, 1.0, 1.0, 1.0), "bold": False, "italic": False, "underline": False, "dim": False},
            "keyword": {"fg": (1.0, 0.4, 0.4, 1.0), "bold": True},
            "string": {"fg": (0.4, 1.0, 0.4, 1.0)},
            "function": {"fg": (1.0, 1.0, 0.4, 1.0), "italic": True},
            "variable": {"fg": (0.78, 0.78, 1.0, 1.0)},
            "number": {"fg": (0.4, 0.4, 1.0, 1.0)},
        }

    def get_style(self, name: str) -> dict[str, Any] | None:
        if name in self._styles:
            return self._styles[name]
        if "." in name:
            return self._styles.get(name.split(".")[0])
        return None

    def merge_styles(self, name: str) -> dict[str, Any]:
        s = self.get_style(name)
        if not s:
            return {"fg": None, "bg": None, "attributes": 0}
        return {
            "fg": s.get("fg"),
            "bg": s.get("bg"),
            "attributes": create_text_attributes(
                bold=s.get("bold", False),
                italic=s.get("italic", False),
                underline=s.get("underline", False),
                dim=s.get("dim", False),
            ),
        }


class _MockClient:
    async def highlight_once(self, content: str, filetype: str) -> dict[str, Any]:
        return {"highlights": []}


@pytest.mark.asyncio
class TestTreeSitterToStyledText:
    async def test_no_highlights_returns_single_chunk(self) -> None:
        style = _MockSyntaxStyle()
        client = _MockClient()
        result = await tree_sitter_to_styled_text("hello world", "plaintext", style, client)
        assert isinstance(result, StyledText)
        assert len(result.chunks) == 1
        assert result.chunks[0]["text"] == "hello world"

    async def test_with_highlights_uses_chunks(self) -> None:
        style = _MockSyntaxStyle()

        class ClientWithHighlights:
            async def highlight_once(self, content: str, filetype: str) -> dict[str, Any]:
                return {
                    "highlights": [
                        (0, 5, "keyword", None),
                        (6, 11, "string", None),
                    ]
                }

        result = await tree_sitter_to_styled_text(
            "hello world", "javascript", style, ClientWithHighlights()
        )
        assert len(result.chunks) >= 2
        joined = "".join(c["text"] for c in result.chunks)
        assert joined == "hello world"


class TestTreeSitterToTextChunks:
    def test_empty_highlights_returns_single_default_chunk(self) -> None:
        style = _MockSyntaxStyle()
        chunks = tree_sitter_to_text_chunks("abc", [], style)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "abc"

    def test_non_overlapping_highlights(self) -> None:
        style = _MockSyntaxStyle()
        highlights: list[tuple[int, int, str, Any]] = [
            (0, 5, "keyword", None),
            (6, 11, "string", None),
        ]
        chunks = tree_sitter_to_text_chunks("hello world", highlights, style)
        assert len(chunks) == 3
        assert chunks[0]["text"] == "hello"
        assert chunks[1]["text"] == " "
        assert chunks[2]["text"] == "world"

    def test_conceal_options_disabled(self) -> None:
        style = _MockSyntaxStyle()
        highlights: list[tuple[int, int, str, Any]] = [
            (0, 3, "conceal", {"conceal": ""}),
        ]
        chunks = tree_sitter_to_text_chunks("foo", highlights, style, ConcealOptions(enabled=False))
        assert len(chunks) == 1
        assert chunks[0]["text"] == "foo"

    def test_conceal_options_dict(self) -> None:
        style = _MockSyntaxStyle()
        highlights: list[tuple[int, int, str, Any]] = [
            (0, 1, "conceal.with.space", None),
        ]
        chunks = tree_sitter_to_text_chunks("x", highlights, style, {"enabled": True})
        assert len(chunks) >= 1
        texts = [c["text"] for c in chunks]
        assert " ".join(texts).replace(" ", "") == "x" or " " in texts

    def test_dot_delimited_groups_and_overlapping_resolution(self) -> None:
        """Align OpenTUI: should resolve styles for dot-delimited groups and multiple overlapping groups."""
        style = _MockSyntaxStyle()
        mock_highlights: list[tuple[int, int, str, Any]] = [
            (0, 4, "variable.member", None),
            (0, 4, "function.method", None),
            (0, 4, "nonexistent", None),
            (4, 8, "keyword", None),
        ]
        content = "testfunc"
        chunks = tree_sitter_to_text_chunks(content, mock_highlights, style)
        assert len(chunks) == 2
        function_style = style.get_style("function")
        assert function_style is not None
        assert chunks[0]["text"] == "test"
        assert chunks[0]["fg"] == (1, 1, 0, 1)  # function (1.0, 1.0, 0.4, 1.0) -> int
        assert chunks[0]["attributes"] == create_text_attributes(
            bold=function_style.get("bold", False),
            italic=function_style.get("italic", False),
            underline=function_style.get("underline", False),
            dim=function_style.get("dim", False),
        )
        keyword_style = style.get_style("keyword")
        assert keyword_style is not None
        assert chunks[1]["text"] == "func"
        assert chunks[1]["fg"] == (1, 0, 0, 1)
        assert chunks[1]["attributes"] == create_text_attributes(
            bold=keyword_style.get("bold", False),
            italic=keyword_style.get("italic", False),
            underline=keyword_style.get("underline", False),
            dim=keyword_style.get("dim", False),
        )

    def test_constructor_group_resolves_to_function(self) -> None:
        """Align OpenTUI: constructor group returns undefined; variable.member + function.method win."""
        style = _MockSyntaxStyle()
        assert style.get_style("constructor") is None
        mock_highlights: list[tuple[int, int, str, Any]] = [
            (0, 11, "variable.member", None),
            (0, 11, "constructor", None),
            (0, 11, "function.method", None),
        ]
        content = "constructor"
        chunks = tree_sitter_to_text_chunks(content, mock_highlights, style)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "constructor"
        assert chunks[0]["fg"] == (1, 1, 0, 1)
        assert chunks[0]["attributes"] == create_text_attributes(
            bold=False, italic=True, underline=False, dim=False
        )

    def test_overlapping_highlights_specificity_resolution(self) -> None:
        """Align OpenTUI: more specific group wins (variable.member over variable, keyword.coroutine over keyword)."""
        style = _MockSyntaxStyle()
        mock_highlights: list[tuple[int, int, str, Any]] = [
            (0, 10, "variable", None),
            (0, 10, "variable.member", None),
            (0, 10, "type", None),
            (11, 16, "keyword", None),
            (11, 16, "keyword.coroutine", None),
        ]
        content = "identifier const"
        chunks = tree_sitter_to_text_chunks(content, mock_highlights, style)
        assert len(chunks) == 3
        variable_style = style.get_style("variable")
        assert variable_style is not None
        assert chunks[0]["text"] == "identifier"
        assert chunks[0]["fg"] == (0, 0, 1, 1)  # variable (0.78, 0.78, 1.0) -> int
        assert chunks[1]["text"] == " "
        assert chunks[2]["text"] == "const"
        assert chunks[2]["fg"] == (1, 0, 0, 1)

    def test_non_overlapping_highlights_preserve_behavior(self) -> None:
        """Align OpenTUI: keyword, string, number with gaps -> 5 chunks with correct styles."""
        style = _MockSyntaxStyle()
        mock_highlights: list[tuple[int, int, str, Any]] = [
            (0, 5, "keyword", None),
            (6, 11, "string", None),
            (12, 15, "number", None),
        ]
        content = "const 'str' 123"
        chunks = tree_sitter_to_text_chunks(content, mock_highlights, style)
        assert len(chunks) == 5
        assert chunks[0]["text"] == "const"
        assert chunks[0]["fg"] == (1, 0, 0, 1)
        assert chunks[0]["attributes"] == create_text_attributes(bold=True)
        assert chunks[1]["text"] == " "
        assert chunks[2]["text"] == "'str'"
        assert chunks[2]["fg"] == (0, 1, 0, 1)
        assert chunks[3]["text"] == " "
        assert chunks[4]["text"] == "123"
        assert chunks[4]["fg"] == (0, 0, 1, 1)
