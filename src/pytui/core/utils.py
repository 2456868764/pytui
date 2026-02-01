# pytui.core.utils - Aligns with OpenTUI core/utils.ts
# createTextAttributes, attributesWithLink, getLinkId, visualizeRenderableTree.

from __future__ import annotations

from typing import Any, Protocol

from pytui.core.types import ATTRIBUTE_BASE_MASK, TextAttributes


class _RenderableLike(Protocol):
    """Minimal protocol for visualize_renderable_tree (aligns OpenTUI Renderable with getChildren)."""

    id: str


# Link attribute helpers (bits 8-31 encode link_id), align OpenTUI utils.ts
LINK_ID_SHIFT = 8
LINK_ID_PAYLOAD_MASK = 0xFFFFFF


def create_text_attributes(
    *,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    dim: bool = False,
    blink: bool = False,
    inverse: bool = False,
    hidden: bool = False,
    strikethrough: bool = False,
) -> int:
    """Build a combined text-attributes bitmask. Aligns OpenTUI createTextAttributes()."""
    attributes = TextAttributes.NONE
    if bold:
        attributes |= TextAttributes.BOLD
    if italic:
        attributes |= TextAttributes.ITALIC
    if underline:
        attributes |= TextAttributes.UNDERLINE
    if dim:
        attributes |= TextAttributes.DIM
    if blink:
        attributes |= TextAttributes.BLINK
    if inverse:
        attributes |= TextAttributes.INVERSE
    if hidden:
        attributes |= TextAttributes.HIDDEN
    if strikethrough:
        attributes |= TextAttributes.STRIKETHROUGH
    return attributes


def attributes_with_link(base_attributes: int, link_id: int) -> int:
    """Encode base attributes plus link_id in high bits. Aligns OpenTUI attributesWithLink()."""
    base = base_attributes & ATTRIBUTE_BASE_MASK
    link_bits = (link_id & LINK_ID_PAYLOAD_MASK) << LINK_ID_SHIFT
    return base | link_bits


def get_link_id(attributes: int) -> int:
    """Extract link_id from attributes. Aligns OpenTUI getLinkId()."""
    return (attributes >> LINK_ID_SHIFT) & LINK_ID_PAYLOAD_MASK


def _get_children(node: _RenderableLike) -> list[Any]:
    """Get children for a renderable (align OpenTUI getChildren())."""
    if hasattr(node, "get_children") and callable(node.get_children):
        return list(node.get_children())
    return list(getattr(node, "children", []))


def visualize_renderable_tree(renderable: _RenderableLike, max_depth: int = 10) -> None:
    """Print a tree of renderable ids to console for debugging. Aligns OpenTUI visualizeRenderableTree()."""
    lines: list[str] = []

    def build_tree_lines(
        node: _RenderableLike,
        prefix: str = "",
        parent_prefix: str = "",
        is_last_child: bool = True,
        depth: int = 0,
    ) -> list[str]:
        if depth >= max_depth:
            return [f"{prefix}{node.id} ... (max depth reached)"]
        out: list[str] = []
        children = _get_children(node)
        out.append(f"{prefix}{node.id}")
        if children:
            last_idx = len(children) - 1
            for i, child in enumerate(children):
                child_is_last = i == last_idx
                connector = "└── " if child_is_last else "├── "
                child_prefix = parent_prefix + ("    " if is_last_child else "│   ")
                child_lines = build_tree_lines(
                    child, parent_prefix + connector, child_prefix, child_is_last, depth + 1
                )
                out.extend(child_lines)
        return out

    lines = build_tree_lines(renderable)
    print("Renderable Tree:\n" + "\n".join(lines))
