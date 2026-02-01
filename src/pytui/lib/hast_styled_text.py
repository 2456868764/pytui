# pytui.lib.hast_styled_text - Aligns with OpenTUI lib/hast-styled-text.ts (optional)
# HAST to StyledText; SyntaxStyle protocol with merge_styles.

from __future__ import annotations

from typing import Any, Protocol, TypedDict, Union

from pytui.lib.styled_text import StyledText

# HASTNode = HASTText | HASTElement (OpenTUI)


class HASTText(TypedDict):
    type: str  # "text"
    value: str


class HASTElement(TypedDict, total=False):
    type: str  # "element"
    tagName: str
    properties: dict[str, Any]  # className?: string
    children: list[HASTNode]


HASTNode = Union[HASTText, HASTElement]


class SyntaxStyleProtocol(Protocol):
    """Protocol: merge_styles(*style_names) -> dict with fg, bg, attributes. Aligns OpenTUI SyntaxStyle.mergeStyles."""

    def merge_styles(self, *style_names: str) -> dict[str, Any]:
        ...


def _hast_to_chunks(
    node: HASTNode,
    syntax_style: SyntaxStyleProtocol,
    parent_styles: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Align with OpenTUI hastToTextChunks."""
    chunks: list[dict[str, Any]] = []
    styles = parent_styles or []
    if node.get("type") == "text":
        names = styles if styles else ["default"]
        merged = syntax_style.merge_styles(*names)
        chunks.append({
            "__isChunk": True,
            "text": node["value"],
            "fg": merged.get("fg"),
            "bg": merged.get("bg"),
            "attributes": merged.get("attributes", 0),
        })
    elif node.get("type") == "element":
        current = list(styles)
        props = node.get("properties") or {}
        if props.get("className"):
            for cls in props["className"].split():
                current.append(cls)
        for child in node.get("children") or []:
            chunks.extend(_hast_to_chunks(child, syntax_style, current))
    return chunks


def hast_to_styled_text(hast: HASTNode, syntax_style: SyntaxStyleProtocol) -> StyledText:
    """Align with OpenTUI hastToStyledText."""
    chunks = _hast_to_chunks(hast, syntax_style)
    return StyledText(chunks)
