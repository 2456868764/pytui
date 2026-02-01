# pytui.lib.singleton - Aligns with OpenTUI lib/singleton.ts
# Ensures a value is initialized once per process; type-safe singleton cache.

from typing import Any, Callable, TypeVar

T = TypeVar("T")

_SINGLETON_CACHE_KEY = "__pytui_lib_singleton_cache__"


def _get_bag() -> dict[str, Any]:
    import sys
    mod = sys.modules.get("pytui.lib.singleton")
    if mod is None:
        return {}
    bag = getattr(mod, _SINGLETON_CACHE_KEY, None)
    if bag is None:
        bag = {}
        setattr(mod, _SINGLETON_CACHE_KEY, bag)
    return bag


def singleton(key: str, factory: Callable[[], T]) -> T:
    """Ensures a value is initialized once per process. Aligns with OpenTUI singleton()."""
    bag = _get_bag()
    if key not in bag:
        bag[key] = factory()
    return bag[key]


def destroy_singleton(key: str) -> None:
    """Removes a singleton by key. Aligns with OpenTUI destroySingleton()."""
    bag = _get_bag()
    if key in bag:
        del bag[key]


def has_singleton(key: str) -> bool:
    """Returns True if the key exists in the singleton cache. Aligns with OpenTUI hasSingleton()."""
    return key in _get_bag()
