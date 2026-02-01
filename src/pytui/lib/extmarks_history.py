# pytui.lib.extmarks_history - Aligns with OpenTUI lib/extmarks-history.ts
# ExtmarksSnapshot, ExtmarksHistory (undo/redo for extmarks).

from dataclasses import asdict
from typing import Any, TypedDict


class Extmark(TypedDict, total=False):
    """Minimal Extmark shape for snapshot; aligns with OpenTUI Extmark."""
    id: int
    start: int
    end: int
    virtual: bool
    styleId: int
    priority: int
    data: Any
    typeId: int


class ExtmarksSnapshot(TypedDict):
    """Aligns with OpenTUI ExtmarksSnapshot."""
    extmarks: dict[int, Any]
    nextId: int


def _copy_extmark(v: Any) -> dict:
    """Copy one extmark (dict or dataclass) to dict."""
    if isinstance(v, dict):
        return dict(v)
    try:
        return asdict(v)
    except TypeError:
        return dict(v)


class ExtmarksHistory:
    """Undo/redo stack for extmarks. Aligns with OpenTUI ExtmarksHistory."""

    def __init__(self) -> None:
        self._undo_stack: list[ExtmarksSnapshot] = []
        self._redo_stack: list[ExtmarksSnapshot] = []

    def save_snapshot(self, extmarks: dict[int, Any], next_id: int) -> None:
        """Push a copy of extmarks and next_id onto undo stack; clear redo. Aligns with OpenTUI saveSnapshot()."""
        snapshot: ExtmarksSnapshot = {
            "extmarks": {k: _copy_extmark(v) for k, v in extmarks.items()},
            "nextId": next_id,
        }
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    def undo(self) -> ExtmarksSnapshot | None:
        """Pop from undo stack and return snapshot; None if empty. Aligns with OpenTUI undo()."""
        if not self._undo_stack:
            return None
        return self._undo_stack.pop()

    def redo(self) -> ExtmarksSnapshot | None:
        """Pop from redo stack and return snapshot; None if empty. Aligns with OpenTUI redo()."""
        if not self._redo_stack:
            return None
        return self._redo_stack.pop()

    def push_redo(self, snapshot: ExtmarksSnapshot) -> None:
        """Push snapshot onto redo stack. Aligns with OpenTUI pushRedo()."""
        self._redo_stack.append(snapshot)

    def push_undo(self, snapshot: ExtmarksSnapshot) -> None:
        """Push snapshot onto undo stack. Aligns with OpenTUI pushUndo()."""
        self._undo_stack.append(snapshot)

    def clear(self) -> None:
        """Clear undo and redo stacks. Aligns with OpenTUI clear()."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        """True if undo stack is not empty. Aligns with OpenTUI canUndo()."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """True if redo stack is not empty. Aligns with OpenTUI canRedo()."""
        return len(self._redo_stack) > 0
