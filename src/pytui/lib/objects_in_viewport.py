# pytui.lib.objects_in_viewport - Aligns with OpenTUI lib/objects-in-viewport.ts
# Returns objects that overlap the viewport; objects must be sorted by position (y for column, x for row).

from typing import Any, Protocol, TypedDict, TypeVar


class ViewportBounds(TypedDict):
    """Aligns with OpenTUI ViewportBounds (from types)."""
    x: int
    y: int
    width: int
    height: int


class ViewportObject(Protocol):
    """Object with x, y, width, height, zIndex. Aligns with OpenTUI ViewportObject."""
    x: int
    y: int
    width: int
    height: int
    z_index: int  # or zIndex for camelCase compatibility


T = TypeVar("T", bound=ViewportObject)

# Max look-behind when expanding left (aligns with OpenTUI maxLookBehind)
_MAX_LOOK_BEHIND = 50


def _val(obj: Any, key: str) -> Any:
    """Get x/y/width/height from dict or attribute."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def get_objects_in_viewport(
    viewport: ViewportBounds,
    objects: list[T],
    direction: str = "column",
    padding: int = 10,
    min_trigger_size: int = 16,
) -> list[T]:
    """
    Returns objects that overlap with the viewport bounds.
    Objects must be pre-sorted by start position (y for column, x for row).
    Aligns with OpenTUI getObjectsInViewport().
    """
    if viewport["width"] <= 0 or viewport["height"] <= 0:
        return []
    if not objects:
        return []
    if len(objects) < min_trigger_size:
        return list(objects)

    vp_x = viewport["x"]
    vp_y = viewport["y"]
    vp_w = viewport["width"]
    vp_h = viewport["height"]
    viewport_top = vp_y - padding
    viewport_bottom = vp_y + vp_h + padding
    viewport_left = vp_x - padding
    viewport_right = vp_x + vp_w + padding
    is_row = direction == "row"
    vp_start = viewport_left if is_row else viewport_top
    vp_end = viewport_right if is_row else viewport_bottom

    def start(obj: T) -> int:
        return int(_val(obj, "x") if is_row else _val(obj, "y"))

    def end(obj: T) -> int:
        if is_row:
            return int(_val(obj, "x") or 0) + int(_val(obj, "width") or 0)
        return int(_val(obj, "y") or 0) + int(_val(obj, "height") or 0)

    # Binary search for any overlapping candidate
    lo, hi = 0, len(objects) - 1
    candidate = -1
    while lo <= hi:
        mid = (lo + hi) >> 1
        c = objects[mid]
        s, e = start(c), end(c)
        if e < vp_start:
            lo = mid + 1
        elif s > vp_end:
            hi = mid - 1
        else:
            candidate = mid
            break

    visible: list[T] = []
    if candidate == -1:
        candidate = lo - 1 if lo > 0 else 0

    # Expand left
    left = candidate
    gap_count = 0
    while left - 1 >= 0:
        prev = objects[left - 1]
        prev_end = end(prev)
        if prev_end <= vp_start:
            gap_count += 1
            if gap_count >= _MAX_LOOK_BEHIND:
                break
        else:
            gap_count = 0
        left -= 1

    # Expand right
    right = candidate + 1
    while right < len(objects):
        n = objects[right]
        if start(n) >= vp_end:
            break
        right += 1

    # Collect overlapping and check cross-axis
    for i in range(left, right):
        child = objects[i]
        s, e = start(child), end(child)
        if e <= vp_start or s >= vp_end:
            continue
        if is_row:
            child_bottom = int(_val(child, "y") or 0) + int(_val(child, "height") or 0)
            child_top = int(_val(child, "y") or 0)
            if child_bottom < viewport_top or child_top > viewport_bottom:
                continue
        else:
            child_right = int(_val(child, "x") or 0) + int(_val(child, "width") or 0)
            child_left = int(_val(child, "x") or 0)
            if child_right < viewport_left or child_left > viewport_right:
                continue
        visible.append(child)

    if len(visible) > 1:
        def _z_index(o: Any) -> int:
            z = _val(o, "z_index") or _val(o, "zIndex")
            return int(z) if z is not None else 0
        visible.sort(key=_z_index)

    return visible
