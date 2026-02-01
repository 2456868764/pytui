import pytest

from pytui.lib.objects_in_viewport import ViewportBounds, get_objects_in_viewport


def create_obj(id: str, x: int, y: int, w: int, h: int, z_index: int = 0) -> dict:
    return {"id": id, "x": x, "y": y, "width": w, "height": h, "z_index": z_index}


def test_returns_empty_for_empty_input():
    viewport: ViewportBounds = {"x": 0, "y": 0, "width": 100, "height": 100}
    assert get_objects_in_viewport(viewport, []) == []


def test_returns_all_when_below_min_trigger_size():
    viewport: ViewportBounds = {"x": 0, "y": 0, "width": 100, "height": 100}
    objects = [create_obj("1", 0, 0, 10, 10), create_obj("2", 200, 200, 10, 10)]
    result = get_objects_in_viewport(viewport, objects, "column", 10, 16)
    assert len(result) == 2


def test_filters_column_direction():
    viewport: ViewportBounds = {"x": 0, "y": 100, "width": 100, "height": 100}
    objects = [create_obj(f"obj-{i}", 0, i * 20, 100, 20) for i in range(20)]
    result = get_objects_in_viewport(viewport, objects, "column", 0, 16)
    ids = [o["id"] for o in result]
    assert "obj-5" in ids
    assert "obj-6" in ids
    assert "obj-9" in ids
    assert "obj-0" not in ids
    assert "obj-15" not in ids


def test_filters_row_direction():
    viewport: ViewportBounds = {"x": 100, "y": 0, "width": 100, "height": 100}
    objects = [create_obj(f"obj-{i}", i * 20, 0, 20, 100) for i in range(20)]
    result = get_objects_in_viewport(viewport, objects, "row", 0, 16)
    ids = [o["id"] for o in result]
    assert "obj-5" in ids
    assert "obj-9" in ids
    assert "obj-0" not in ids


def test_sorts_by_z_index():
    viewport: ViewportBounds = {"x": 0, "y": 0, "width": 100, "height": 100}
    objects = [create_obj(f"obj-{i}", 0, i * 10, 100, 10, 20 - i) for i in range(20)]
    result = get_objects_in_viewport(viewport, objects, "column", 0, 16)
    for i in range(1, len(result)):
        z_cur = result[i].get("z_index") or result[i].get("zIndex", 0)
        z_prev = result[i - 1].get("z_index") or result[i - 1].get("zIndex", 0)
        assert z_cur >= z_prev


def test_zero_width_viewport_returns_empty():
    viewport: ViewportBounds = {"x": 100, "y": 100, "width": 0, "height": 100}
    objects = [create_obj(f"obj-{i}", 0, i * 20, 100, 20) for i in range(20)]
    assert get_objects_in_viewport(viewport, objects) == []


def test_zero_height_viewport_returns_empty():
    viewport: ViewportBounds = {"x": 100, "y": 100, "width": 100, "height": 0}
    objects = [create_obj(f"obj-{i}", 0, i * 20, 100, 20) for i in range(20)]
    assert get_objects_in_viewport(viewport, objects) == []
