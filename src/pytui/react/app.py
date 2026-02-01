# pytui.react.app - AppContext, use_app_context (aligns OpenTUI components/app.tsx)

from __future__ import annotations

from typing import Any

# Module-level context: key_handler and renderer (set by create_root).
# Aligns OpenTUI createContext<AppContext>({ keyHandler: null, renderer: null }).
_app_context: dict[str, Any] = {"key_handler": None, "renderer": None}


def get_app_context() -> dict[str, Any]:
    """Return current app context. Aligns OpenTUI useContext(AppContext)."""
    return _app_context


def use_app_context() -> dict[str, Any]:
    """Hook: return { key_handler, renderer }. Aligns OpenTUI useAppContext()."""
    return get_app_context()


def set_app_context(key_handler: Any = None, renderer: Any = None) -> None:
    """Set app context (used by create_root). Not part of OpenTUI public API."""
    global _app_context
    ctx = dict(_app_context)
    if key_handler is not None:
        ctx["key_handler"] = key_handler
    if renderer is not None:
        ctx["renderer"] = renderer
    _app_context.update(ctx)
