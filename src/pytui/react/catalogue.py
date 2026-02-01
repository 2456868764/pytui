# pytui.react.catalogue - base_components, component_catalogue, extend, get_component_catalogue
# Aligns with OpenTUI react components/index.ts

from __future__ import annotations

from typing import Any, Type

# Lazy imports to avoid circular deps and missing components (e.g. ascii_font, box)
def _get_base_components() -> dict[str, Type[Any]]:
    from pytui.components import (
        Code,
        Diff,
        Input,
        LineNumber,
        ScrollBar,
        Scrollbox,
        Select,
        Slider,
        TabSelect,
        Text,
        Textarea,
    )
    from pytui.react.text_components import (
        BoldSpanRenderable,
        ItalicSpanRenderable,
        LineBreakRenderable,
        LinkRenderable,
        SpanRenderable,
        UnderlineSpanRenderable,
    )
    base: dict[str, Type[Any]] = {
        "text": Text,
        "code": Code,
        "diff": Diff,
        "input": Input,
        "select": Select,
        "textarea": Textarea,
        "scrollbox": Scrollbox,
        "scrollbar": ScrollBar,
        "slider": Slider,
        "tab_select": TabSelect,
        "line_number": LineNumber,
        "span": SpanRenderable,
        "br": LineBreakRenderable,
        "b": BoldSpanRenderable,
        "strong": BoldSpanRenderable,
        "i": ItalicSpanRenderable,
        "em": ItalicSpanRenderable,
        "u": UnderlineSpanRenderable,
        "a": LinkRenderable,
    }
    try:
        from pytui.components import Box
        base["box"] = Box
    except ImportError:
        pass
    try:
        from pytui.components import ASCIIFont
        base["ascii_font"] = ASCIIFont
    except ImportError:
        pass
    return base


_component_catalogue: dict[str, Type[Any]] | None = None


def get_component_catalogue() -> dict[str, Type[Any]]:
    """Return the component catalogue. Aligns OpenTUI getComponentCatalogue()."""
    global _component_catalogue
    if _component_catalogue is None:
        _component_catalogue = dict(_get_base_components())
    return _component_catalogue


def extend(extra: dict[str, Type[Any]]) -> None:
    """Extend the component catalogue. Aligns OpenTUI extend(objects)."""
    cat = get_component_catalogue()
    for k, v in extra.items():
        cat[k] = v


# Base components (read-only snapshot for type/docs). Use get_component_catalogue() for mutable.
def base_components() -> dict[str, Type[Any]]:
    return dict(_get_base_components())


# Text node keys: must be created inside a text node (aligns OpenTUI textNodeKeys)
TEXT_NODE_KEYS = frozenset({"span", "br", "b", "strong", "i", "em", "u", "a"})
