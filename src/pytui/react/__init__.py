# pytui.react - 声明式 API (Component, Hooks, JSX, Reconciler) - aligns OpenTUI packages/react

from pytui.react.app import use_app_context
from pytui.react.catalogue import (
    TEXT_NODE_KEYS,
    base_components,
    extend,
    get_component_catalogue,
)
from pytui.react.component import Component
from pytui.react.error_boundary import ErrorBoundary
from pytui.react.hooks import (
    useEffect,
    useEvent,
    useKeyboard,
    useOnResize,
    useRenderer,
    useResize,
    useState,
    useTerminalDimensions,
    useTimeline,
)
from pytui.react.jsx import create_element, h
from pytui.react.reconciler import create_reconciler, create_root, flush_sync, reconcile
from pytui.react.utils_id import get_next_id

__all__ = [
    "Component",
    "ErrorBoundary",
    "TEXT_NODE_KEYS",
    "base_components",
    "create_element",
    "create_root",
    "create_reconciler",
    "extend",
    "flush_sync",
    "get_component_catalogue",
    "get_next_id",
    "h",
    "reconcile",
    "use_app_context",
    "useEffect",
    "useEvent",
    "useKeyboard",
    "useOnResize",
    "useRenderer",
    "useResize",
    "useState",
    "useTerminalDimensions",
    "useTimeline",
]
