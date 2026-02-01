import pytest

from pytui.lib.keymapping import (
    KeyBinding,
    build_key_bindings_map,
    default_key_aliases,
    get_key_binding_key,
    key_binding_to_string,
    merge_key_aliases,
    merge_key_bindings,
)


def test_get_key_binding_key_meta():
    b: KeyBinding = {"name": "a", "meta": True, "action": "test"}
    assert get_key_binding_key(b) == "a:0:0:1:0"


def test_get_key_binding_key_different_modifiers():
    no_mod = get_key_binding_key({"name": "a", "action": "test"})
    with_meta = get_key_binding_key({"name": "a", "meta": True, "action": "test"})
    with_ctrl = get_key_binding_key({"name": "a", "ctrl": True, "action": "test"})
    with_shift = get_key_binding_key({"name": "a", "shift": True, "action": "test"})
    assert no_mod != with_meta != with_ctrl != with_shift


def test_get_key_binding_key_super():
    b: KeyBinding = {"name": "z", "super": True, "action": "test"}
    assert get_key_binding_key(b) == "z:0:0:0:1"


def test_merge_key_bindings():
    defaults: list[KeyBinding] = [
        {"name": "a", "action": "action1"},
        {"name": "b", "action": "action2"},
    ]
    custom: list[KeyBinding] = [{"name": "c", "action": "action3"}]
    merged = merge_key_bindings(defaults, custom)
    assert len(merged) == 3


def test_merge_key_bindings_custom_overrides():
    defaults: list[KeyBinding] = [{"name": "a", "action": "action1"}]
    custom: list[KeyBinding] = [{"name": "a", "action": "action2"}]
    merged = merge_key_bindings(defaults, custom)
    assert len(merged) == 1
    assert merged[0]["action"] == "action2"


def test_build_key_bindings_map():
    bindings: list[KeyBinding] = [
        {"name": "a", "action": "action1"},
        {"name": "b", "meta": True, "action": "action2"},
    ]
    m = build_key_bindings_map(bindings)
    assert m.get("a:0:0:0:0") == "action1"
    assert m.get("b:0:0:1:0") == "action2"


def test_build_key_bindings_map_aliases():
    bindings: list[KeyBinding] = [{"name": "enter", "action": "submit"}]
    aliases = {"enter": "return"}
    m = build_key_bindings_map(bindings, aliases)
    assert m.get("enter:0:0:0:0") == "submit"
    assert m.get("return:0:0:0:0") == "submit"


def test_merge_key_aliases():
    merged = merge_key_aliases({"enter": "return"}, {"esc": "escape"})
    assert merged["enter"] == "return"
    assert merged["esc"] == "escape"


def test_default_key_aliases():
    assert default_key_aliases["enter"] == "return"
    assert default_key_aliases["esc"] == "escape"


def test_key_binding_to_string():
    assert key_binding_to_string({"name": "escape", "action": "cancel"}) == "escape"
    assert key_binding_to_string({"name": "c", "ctrl": True, "action": "copy"}) == "ctrl+c"
    assert key_binding_to_string({"name": "y", "ctrl": True, "shift": True, "action": "copy"}) == "ctrl+shift+y"
    assert key_binding_to_string({"name": "s", "meta": True, "action": "save"}) == "meta+s"
    assert key_binding_to_string({"name": "z", "super": True, "action": "undo"}) == "super+z"
