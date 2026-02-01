# pytui.react.utils_id - get_next_id (aligns OpenTUI react utils/id.ts)

from __future__ import annotations

_id_counter: dict[str, int] = {}


def get_next_id(type_name: str) -> str:
    """Generate unique id for a host element type. Aligns OpenTUI getNextId(type)."""
    global _id_counter
    if type_name not in _id_counter:
        _id_counter[type_name] = 0
    _id_counter[type_name] += 1
    return f"{type_name}-{_id_counter[type_name]}"
