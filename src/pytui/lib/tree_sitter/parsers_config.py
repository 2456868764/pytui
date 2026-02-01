# pytui.lib.tree_sitter.parsers_config - Aligns OpenTUI default parsers (empty stub; no WASM)

from __future__ import annotations

from typing import Any

_DEFAULT_PARSERS: list[dict[str, Any]] = []


def get_default_parsers() -> list[dict[str, Any]]:
    """Return default filetype parser options. Aligns OpenTUI getParsers / DEFAULT_PARSERS."""
    return list(_DEFAULT_PARSERS)


def add_default_parsers(parsers: list[dict[str, Any]]) -> None:
    """Align with OpenTUI addDefaultParsers. Add or replace parsers by filetype."""
    global _DEFAULT_PARSERS
    for p in parsers:
        opts = dict(p)
        ft = opts.get("filetype")
        if not ft:
            continue
        existing = next((i for i, x in enumerate(_DEFAULT_PARSERS) if x.get("filetype") == ft), -1)
        if existing >= 0:
            _DEFAULT_PARSERS[existing] = opts
        else:
            _DEFAULT_PARSERS.append(opts)
