# pytui.react.error_boundary - ErrorBoundary component (aligns OpenTUI components/error-boundary.tsx)

from __future__ import annotations

import traceback
from typing import Any

from pytui.react.component import Component
from pytui.react.jsx import h


class ErrorBoundary(Component):
    """Catches render errors in children and displays error UI. Aligns OpenTUI ErrorBoundary."""

    def __init__(self, ctx: Any, props: dict[str, Any] | None = None) -> None:
        super().__init__(ctx, props)
        self._has_error = False
        self._error: BaseException | None = None

    def set_error(self, error: BaseException) -> None:
        """Set error state (called by reconciler when child throws)."""
        self._has_error = True
        self._error = error

    def render(self) -> Any:
        if self._has_error and self._error is not None:
            err = self._error
            msg = "".join(traceback.format_exception(type(err), err, err.__traceback__))
            if not msg.strip():
                msg = str(err)
            return h("box", {"style": {"flex_direction": "column", "padding": 2}}, [
                h("text", {"fg": "red"}, [msg]),
            ])
        children = self.props.get("children")
        if children is None:
            return h("box", {"style": {"flex_direction": "column"}}, [])
        if isinstance(children, dict) and children.get("type"):
            return children
        wrap = [children] if not isinstance(children, list) else children
        return h("box", {"style": {"flex_direction": "column"}}, wrap)
