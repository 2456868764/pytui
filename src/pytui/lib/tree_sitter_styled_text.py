# pytui.lib.tree_sitter_styled_text - Aligns with OpenTUI lib/tree-sitter-styled-text.ts
# tree_sitter_to_text_chunks, tree_sitter_to_styled_text; ConcealOptions; OTUI_TS_STYLE_WARN

from __future__ import annotations

import warnings
from typing import Any, Protocol, TypedDict

from pytui.lib.env import env, register_env_var
from pytui.lib.styled_text import StyledText, create_text_attributes
from pytui.lib.rgba import RGBA, parse_color
from pytui.lib.tree_sitter.types import SimpleHighlight

register_env_var({
    "name": "OTUI_TS_STYLE_WARN",
    "default": False,
    "description": "Enable warnings for missing syntax styles",
    "type": "boolean",
})


def _style_to_tuple(val: Any) -> tuple[int, int, int, int] | None:
    if val is None:
        return None
    if isinstance(val, RGBA):
        return val.to_tuple()
    if isinstance(val, (tuple, list)) and len(val) >= 4:
        return (int(val[0]), int(val[1]), int(val[2]), int(val[3]))
    try:
        return parse_color(val).to_tuple()
    except Exception:
        return None


class ConcealOptions:
    """Align OpenTUI ConcealOptions."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled


class TreeSitterToStyledTextOptions(TypedDict, total=False):
    """Align OpenTUI TreeSitterToStyledTextOptions."""
    conceal: ConcealOptions | dict[str, Any]


class SyntaxStyleProtocol(Protocol):
    """Protocol: get_style(name) -> StyleDefinition. Aligns OpenTUI SyntaxStyle.getStyle."""

    def get_style(self, name: str) -> dict[str, Any] | None:
        ...


def _get_specificity(group: str) -> int:
    return len(group.split("."))


def _should_suppress_in_injection(group: str, meta: Any) -> bool:
    if meta and meta.get("isInjection"):
        return False
    return group == "markup.raw.block"


def tree_sitter_to_text_chunks(
    content: str,
    highlights: list[SimpleHighlight],
    syntax_style: SyntaxStyleProtocol,
    options: ConcealOptions | dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Align with OpenTUI treeSitterToTextChunks. Returns list of TextChunk dicts."""
    chunks: list[dict[str, Any]] = []
    default_style = syntax_style.get_style("default") if hasattr(syntax_style, "get_style") else None
    conceal_enabled = True
    if options is not None:
        conceal_enabled = (
            options.get("enabled", True)
            if isinstance(options, dict)
            else getattr(options, "enabled", True)
        )

    injection_container_ranges: list[dict[str, int]] = []
    boundaries: list[dict[str, Any]] = []

    for i, h in enumerate(highlights):
        start, end = h[0], h[1]
        meta = h[3] if len(h) >= 4 else None
        if start == end:
            continue
        if meta and meta.get("containsInjection"):
            injection_container_ranges.append({"start": start, "end": end})
        boundaries.append({"offset": start, "type": "start", "highlightIndex": i})
        boundaries.append({"offset": end, "type": "end", "highlightIndex": i})

    def sort_key(b: dict) -> tuple[int, int]:
        o = b["offset"]
        t = 0 if b["type"] == "end" else 1
        return (o, t)

    boundaries.sort(key=sort_key)
    active_highlights: set[int] = set()
    current_offset = 0

    for boundary in boundaries:
        if current_offset < boundary["offset"] and active_highlights:
            segment_text = content[current_offset : boundary["offset"]]
            active_groups = []
            for idx in active_highlights:
                hi = highlights[idx]
                group = hi[2]
                meta = hi[3] if len(hi) >= 4 else None
                active_groups.append({"group": group, "meta": meta, "index": idx})

            conceal_highlight = None
            if conceal_enabled:
                for ag in active_groups:
                    g, meta = ag.get("group", ""), ag.get("meta")
                    if (meta is not None and meta.get("conceal") is not None) or g == "conceal" or (g.startswith("conceal.")):
                        conceal_highlight = ag
                        break

            if conceal_highlight:
                replacement_text = ""
                meta = conceal_highlight.get("meta") or {}
                if meta.get("conceal") is not None:
                    replacement_text = meta.get("conceal") or ""
                elif conceal_highlight.get("group") == "conceal.with.space":
                    replacement_text = " "
                if replacement_text:
                    fg = _style_to_tuple(default_style.get("fg")) if default_style else None
                    bg = _style_to_tuple(default_style.get("bg")) if default_style else None
                    attrs = create_text_attributes(
                        bold=default_style.get("bold", False),
                        italic=default_style.get("italic", False),
                        underline=default_style.get("underline", False),
                        dim=default_style.get("dim", False),
                    ) if default_style else 0
                    chunk = {"__isChunk": True, "text": replacement_text, "attributes": attrs}
                    if fg is not None:
                        chunk["fg"] = fg
                    if bg is not None:
                        chunk["bg"] = bg
                    chunks.append(chunk)
            else:
                inside_injection = any(
                    current_offset >= r["start"] and current_offset < r["end"]
                    for r in injection_container_ranges
                )
                valid_groups = [
                    ag for ag in active_groups
                    if not (inside_injection and _should_suppress_in_injection(ag.get("group", ""), ag.get("meta")))
                ]
                valid_groups.sort(key=lambda x: (_get_specificity(x["group"]), x["index"]))
                merged_style: dict[str, Any] = {}
                for ag in valid_groups:
                    group = ag["group"]
                    style_for_group = syntax_style.get_style(group) if hasattr(syntax_style, "get_style") else None
                    if not style_for_group and "." in group:
                        style_for_group = syntax_style.get_style(group.split(".")[0]) if hasattr(syntax_style, "get_style") else None
                    if style_for_group:
                        if style_for_group.get("fg") is not None:
                            merged_style["fg"] = style_for_group["fg"]
                        if style_for_group.get("bg") is not None:
                            merged_style["bg"] = style_for_group["bg"]
                        for k in ("bold", "italic", "underline", "dim"):
                            if k in style_for_group:
                                merged_style[k] = style_for_group[k]
                    else:
                        if getattr(env, "OTUI_TS_STYLE_WARN", False):
                            if "." in group:
                                base_name = group.split(".")[0]
                                warnings.warn(
                                    f'Syntax style not found for group "{group}" or base scope "{base_name}", using default style',
                                    stacklevel=2,
                                )
                            else:
                                warnings.warn(
                                    f'Syntax style not found for group "{group}", using default style',
                                    stacklevel=2,
                                )
                final_style = merged_style if merged_style else default_style
                fg = _style_to_tuple(final_style.get("fg")) if final_style else None
                bg = _style_to_tuple(final_style.get("bg")) if final_style else None
                attrs = create_text_attributes(
                    bold=final_style.get("bold", False),
                    italic=final_style.get("italic", False),
                    underline=final_style.get("underline", False),
                    dim=final_style.get("dim", False),
                ) if final_style else 0
                chunk = {"__isChunk": True, "text": segment_text, "attributes": attrs}
                if fg is not None:
                    chunk["fg"] = fg
                if bg is not None:
                    chunk["bg"] = bg
                chunks.append(chunk)
        elif current_offset < boundary["offset"]:
            text = content[current_offset : boundary["offset"]]
            fg = _style_to_tuple(default_style.get("fg")) if default_style else None
            bg = _style_to_tuple(default_style.get("bg")) if default_style else None
            attrs = create_text_attributes(
                bold=default_style.get("bold", False),
                italic=default_style.get("italic", False),
                underline=default_style.get("underline", False),
                dim=default_style.get("dim", False),
            ) if default_style else 0
            chunk = {"__isChunk": True, "text": text, "attributes": attrs}
            if fg is not None:
                chunk["fg"] = fg
            if bg is not None:
                chunk["bg"] = bg
            chunks.append(chunk)

        if boundary["type"] == "start":
            active_highlights.add(boundary["highlightIndex"])
        else:
            active_highlights.discard(boundary["highlightIndex"])
            if conceal_enabled and boundary["highlightIndex"] < len(highlights):
                h = highlights[boundary["highlightIndex"]]
                meta = h[3] if len(h) >= 4 else None
                if meta and meta.get("concealLines") is not None:
                    if boundary["offset"] < len(content) and content[boundary["offset"]] == "\n":
                        current_offset = boundary["offset"] + 1
                        continue
                if meta and meta.get("conceal") is not None:
                    if meta.get("conceal") == " " and boundary["offset"] < len(content) and content[boundary["offset"]] == " ":
                        current_offset = boundary["offset"] + 1
                        continue
                    if meta.get("conceal") == "" and h[2] == "conceal" and not meta.get("isInjection"):
                        if boundary["offset"] < len(content) and content[boundary["offset"]] == " ":
                            current_offset = boundary["offset"] + 1
                            continue
        current_offset = boundary["offset"]

    if current_offset < len(content):
        text = content[current_offset:]
        fg = _style_to_tuple(default_style.get("fg")) if default_style else None
        bg = _style_to_tuple(default_style.get("bg")) if default_style else None
        attrs = create_text_attributes(
            bold=default_style.get("bold", False),
            italic=default_style.get("italic", False),
            underline=default_style.get("underline", False),
            dim=default_style.get("dim", False),
        ) if default_style else 0
        chunk = {"__isChunk": True, "text": text, "attributes": attrs}
        if fg is not None:
            chunk["fg"] = fg
        if bg is not None:
            chunk["bg"] = bg
        chunks.append(chunk)

    return chunks


async def tree_sitter_to_styled_text(
    content: str,
    filetype: str,
    syntax_style: SyntaxStyleProtocol,
    client: Any,
    options: dict[str, Any] | None = None,
) -> StyledText:
    """Align with OpenTUI treeSitterToStyledText. Async: calls client.highlight_once."""
    result = await client.highlight_once(content, filetype)
    highlights = result.get("highlights") if result else None
    if highlights and len(highlights) > 0:
        conceal_opts = (options or {}).get("conceal") if options else None
        chunks = tree_sitter_to_text_chunks(content, highlights, syntax_style, conceal_opts)
        return StyledText(chunks)
    default_merged: dict[str, Any]
    if hasattr(syntax_style, "merge_styles"):
        default_merged = syntax_style.merge_styles("default")
    else:
        default_style = syntax_style.get_style("default") if hasattr(syntax_style, "get_style") else None
        if default_style:
            default_merged = {
                "fg": default_style.get("fg"),
                "bg": default_style.get("bg"),
                "attributes": create_text_attributes(
                    bold=default_style.get("bold", False),
                    italic=default_style.get("italic", False),
                    underline=default_style.get("underline", False),
                    dim=default_style.get("dim", False),
                ),
            }
        else:
            default_merged = {"fg": None, "bg": None, "attributes": 0}
    fg = _style_to_tuple(default_merged.get("fg"))
    bg = _style_to_tuple(default_merged.get("bg"))
    attrs = default_merged.get("attributes", 0)
    chunk = {"__isChunk": True, "text": content, "attributes": attrs}
    if fg is not None:
        chunk["fg"] = fg
    if bg is not None:
        chunk["bg"] = bg
    return StyledText([chunk])
