# pytui.lib.extmarks - Aligns with OpenTUI lib/extmarks.ts
# Extmark, ExtmarksStore (add, remove, get, get_in_range, clear). ExtmarksController not migrated (edit-buffer specific).

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Extmark:
    """Inline mark; display-width offsets. Aligns with OpenTUI Extmark."""

    id: int
    start: int  # display-width offset (including newlines), NOT string index
    end: int
    virtual: bool = False
    style_id: int | None = None
    priority: int | None = None
    data: Any = None
    type_id: int = 0


class ExtmarksStore:
    """Store extmarks by id; query by range. Aligns with OpenTUI extmarks store (add/remove/get/get_in_range/clear)."""

    def __init__(self) -> None:
        self._marks: dict[int, Extmark] = {}
        self._next_id = 1

    def add(
        self,
        start: int,
        end: int,
        *,
        virtual: bool = False,
        style_id: int | None = None,
        priority: int | None = None,
        data: Any = None,
        type_id: int = 0,
    ) -> int:
        """Add an extmark; return id. Aligns with OpenTUI add()."""
        eid = self._next_id
        self._next_id += 1
        self._marks[eid] = Extmark(
            id=eid,
            start=start,
            end=end,
            virtual=virtual,
            style_id=style_id,
            priority=priority,
            data=data,
            type_id=type_id,
        )
        return eid

    def remove(self, eid: int) -> bool:
        """Remove extmark by id. Aligns with OpenTUI remove()."""
        if eid in self._marks:
            del self._marks[eid]
            return True
        return False

    def get(self, eid: int) -> Extmark | None:
        """Get extmark by id."""
        return self._marks.get(eid)

    def get_in_range(self, start: int, end: int) -> list[Extmark]:
        """Return extmarks overlapping [start, end), sorted by priority desc, start asc. Aligns with OpenTUI get_in_range()."""
        out = [m for m in self._marks.values() if m.start < end and m.end > start]
        out.sort(key=lambda m: (-(m.priority or 0), m.start))
        return out

    def clear(self) -> None:
        """Clear all extmarks."""
        self._marks.clear()

    def __len__(self) -> int:
        return len(self._marks)
