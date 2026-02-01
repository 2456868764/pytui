# pytui.lib.keymapping - Aligns with OpenTUI lib/keymapping.ts
# KeyBinding type, merge_key_bindings, get_key_binding_key, build_key_bindings_map, key_binding_to_string.

from typing import Any, TypedDict

# Action is string; KeyBinding is generic over action name
Action = str


class KeyBinding(TypedDict, total=False):
    """Aligns with OpenTUI KeyBinding<Action>. name and action required; ctrl/shift/meta/super optional."""
    name: str
    action: str
    ctrl: bool
    shift: bool
    meta: bool
    super: bool


KeyAliasMap = dict[str, str]

default_key_aliases: KeyAliasMap = {
    "enter": "return",
    "esc": "escape",
}


def merge_key_aliases(defaults: KeyAliasMap, custom: KeyAliasMap) -> KeyAliasMap:
    """Merge default and custom aliases; custom overrides. Aligns with OpenTUI mergeKeyAliases()."""
    return {**defaults, **custom}


def get_key_binding_key(binding: KeyBinding) -> str:
    """Unique key string for a binding (name:ctrl:shift:meta:super). Aligns with OpenTUI getKeyBindingKey()."""
    return "{}:{}:{}:{}:{}".format(
        binding["name"],
        1 if binding.get("ctrl") else 0,
        1 if binding.get("shift") else 0,
        1 if binding.get("meta") else 0,
        1 if binding.get("super") else 0,
    )


def merge_key_bindings(
    defaults: list[KeyBinding],
    custom: list[KeyBinding],
) -> list[KeyBinding]:
    """Merge default and custom bindings; custom overrides same key. Aligns with OpenTUI mergeKeyBindings()."""
    m: dict[str, KeyBinding] = {}
    for b in defaults:
        m[get_key_binding_key(b)] = b
    for b in custom:
        m[get_key_binding_key(b)] = b
    return list(m.values())


def build_key_bindings_map(
    bindings: list[KeyBinding],
    alias_map: KeyAliasMap | None = None,
) -> dict[str, str]:
    """Build name:ctrl:shift:meta:super -> action. Adds aliased keys (e.g. enter -> return). Aligns with OpenTUI buildKeyBindingsMap()."""
    result: dict[str, str] = {}
    aliases = alias_map or {}
    for b in bindings:
        result[get_key_binding_key(b)] = b["action"]
    for b in bindings:
        normalized = aliases.get(b["name"], b["name"])
        if normalized != b["name"]:
            key = get_key_binding_key({**b, "name": normalized})
            result[key] = b["action"]
    return result


def key_binding_to_string(binding: KeyBinding) -> str:
    """Human-readable string e.g. 'ctrl+shift+y' or 'escape'. Aligns with OpenTUI keyBindingToString()."""
    parts: list[str] = []
    if binding.get("ctrl"):
        parts.append("ctrl")
    if binding.get("shift"):
        parts.append("shift")
    if binding.get("meta"):
        parts.append("meta")
    if binding.get("super"):
        parts.append("super")
    parts.append(binding["name"])
    return "+".join(parts)
