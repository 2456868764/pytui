# pytui.lib.selection - Aligns with OpenTUI lib/selection.ts
# Selection, LocalSelectionBounds, convert_global_to_local_selection, ASCIIFontSelectionHelper;
# SelectionState (from core). Merged from core/selection.py + utils/selection.py.

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pytui.core.renderable import Renderable


def _coordinate_to_character_index(x: int, text: str, font: Any) -> int:
    """Use lib.ascii_font to avoid circular dependency with components.ascii_font."""
    from pytui.lib.ascii_font import coordinate_to_character_index
    return coordinate_to_character_index(x, text, font)


@dataclass
class LocalSelectionBounds:
    """Local selection bounds. Aligns with OpenTUI LocalSelectionBounds."""
    anchor_x: int
    anchor_y: int
    focus_x: int
    focus_y: int
    is_active: bool = True


class SelectionState:
    """Selection state: anchor and cursor (char offset). Aligns with core/selection.SelectionState."""

    def __init__(self, length: int = 0) -> None:
        self._anchor: int | None = None
        self._cursor = 0
        self._length = max(0, length)

    def set_length(self, length: int) -> None:
        self._length = max(0, length)
        self._cursor = max(0, min(self._cursor, self._length))
        if self._anchor is not None:
            self._anchor = max(0, min(self._anchor, self._length))

    def get_range(self) -> tuple[int, int] | None:
        if self._anchor is None:
            return None
        a, b = self._anchor, self._cursor
        if a > b:
            a, b = b, a
        return (a, b)

    @property
    def cursor(self) -> int:
        return self._cursor

    @cursor.setter
    def cursor(self, value: int) -> None:
        self._cursor = max(0, min(value, self._length))

    @property
    def anchor(self) -> int | None:
        return self._anchor

    def set_cursor(self, pos: int) -> None:
        self._cursor = max(0, min(pos, self._length))
        self._anchor = None

    def set_selection(self, anchor: int, cursor: int) -> None:
        self._anchor = max(0, min(anchor, self._length))
        self._cursor = max(0, min(cursor, self._length))

    def clear_selection(self) -> None:
        self._anchor = None

    def has_selection(self) -> bool:
        return self._anchor is not None


class Selection:
    """Viewport selection: anchor/focus (x,y), bounds, selected_renderables, get_selected_text. Aligns with OpenTUI Selection."""

    __slots__ = (
        "_anchor_x", "_anchor_y", "_focus_x", "_focus_y",
        "_is_active", "_is_selecting", "_is_start",
        "_selected_renderables", "_touched_renderables",
    )

    def __init__(
        self,
        anchor_renderable_or_anchor_x: Renderable | int | None,
        anchor_x_or_anchor_y: int | None = None,
        anchor_y_or_focus_x: int | None = None,
        focus_x_or_focus_y: int | None = None,
        focus_y_or_is_active: int | bool | None = None,
        is_active: bool = True,
        is_selecting: bool = True,
        is_start: bool = False,
    ) -> None:
        # Backward compat: Selection(anchor_x, anchor_y, focus_x, focus_y) or Selection(anchor_x, anchor_y, focus_x, focus_y, is_active=...)
        if isinstance(anchor_renderable_or_anchor_x, int) and anchor_x_or_anchor_y is not None:
            self._anchor_x = anchor_renderable_or_anchor_x
            self._anchor_y = int(anchor_x_or_anchor_y)
            self._focus_x = int(anchor_y_or_focus_x)
            self._focus_y = int(focus_x_or_focus_y or 0)
            self._is_active = is_active  # keyword
        else:
            renderable = anchor_renderable_or_anchor_x
            self._anchor_x = int(anchor_x_or_anchor_y or 0)
            self._anchor_y = int(anchor_y_or_focus_x or 0)
            self._focus_x = int(focus_x_or_focus_y or 0)
            self._focus_y = int(focus_y_or_is_active or 0) if isinstance(focus_y_or_is_active, (int, float)) else 0
            self._is_active = is_active
        self._is_selecting = is_selecting
        self._is_start = is_start
        self._selected_renderables = []
        self._touched_renderables = []

    @property
    def is_start(self) -> bool:
        return self._is_start

    @is_start.setter
    def is_start(self, value: bool) -> None:
        self._is_start = value

    @property
    def anchor(self) -> tuple[int, int]:
        return (self._anchor_x, self._anchor_y)

    @property
    def focus(self) -> tuple[int, int]:
        return (self._focus_x, self._focus_y)

    @focus.setter
    def focus(self, value: tuple[int, int]) -> None:
        self._focus_x, self._focus_y = value

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._is_active = value

    @property
    def is_selecting(self) -> bool:
        return self._is_selecting

    @is_selecting.setter
    def is_selecting(self, value: bool) -> None:
        self._is_selecting = value

    @property
    def bounds(self) -> dict[str, int]:
        """ViewportBounds: x, y, width, height (inclusive). Aligns with OpenTUI bounds."""
        min_x = min(self._anchor_x, self._focus_x)
        max_x = max(self._anchor_x, self._focus_x)
        min_y = min(self._anchor_y, self._focus_y)
        max_y = max(self._anchor_y, self._focus_y)
        return {
            "x": min_x,
            "y": min_y,
            "width": max_x - min_x + 1,
            "height": max_y - min_y + 1,
        }

    def update_selected_renderables(self, renderables: list[Any]) -> None:
        """Aligns with OpenTUI updateSelectedRenderables()."""
        self._selected_renderables = list(renderables)

    @property
    def selected_renderables(self) -> list[Any]:
        return self._selected_renderables

    def update_touched_renderables(self, renderables: list[Any]) -> None:
        """Aligns with OpenTUI updateTouchedRenderables()."""
        self._touched_renderables = list(renderables)

    @property
    def touched_renderables(self) -> list[Any]:
        return self._touched_renderables

    def get_selected_text(self) -> str:
        """Aligns with OpenTUI getSelectedText(): sort by y,x and join get_selected_text()."""
        sorted_list = sorted(
            self._selected_renderables,
            key=lambda r: (getattr(r, "y", 0), getattr(r, "x", 0)),
        )
        texts = []
        for r in sorted_list:
            if getattr(r, "is_destroyed", True):
                continue
            t = getattr(r, "get_selected_text", None)
            if callable(t):
                s = t()
                if s:
                    texts.append(s)
        return "\n".join(texts) if texts else ""

    def to_local(self, local_x: int, local_y: int) -> LocalSelectionBounds:
        """Convert global selection to local bounds. Aligns with OpenTUI to_local."""
        return LocalSelectionBounds(
            anchor_x=self._anchor_x - local_x,
            anchor_y=self._anchor_y - local_y,
            focus_x=self._focus_x - local_x,
            focus_y=self._focus_y - local_y,
            is_active=self._is_active,
        )


def convert_global_to_local_selection(
    global_selection: Selection | None,
    local_x: int,
    local_y: int,
) -> LocalSelectionBounds | None:
    """Convert global Selection to local bounds; None if inactive. Aligns with OpenTUI convertGlobalToLocalSelection()."""
    if global_selection is None or not global_selection.is_active:
        return None
    return global_selection.to_local(local_x, local_y)


class ASCIIFontSelectionHelper:
    """ASCIIFont selection helper: local coords -> (start, end) char indices. Aligns with OpenTUI ASCIIFontSelectionHelper."""

    def __init__(
        self,
        get_text: Callable[[], str],
        get_font: Callable[[], Any],
    ) -> None:
        self._get_text = get_text
        self._get_font = get_font
        self._selection: tuple[int, int] | None = None  # backward compat name

    def has_selection(self) -> bool:
        return self._selection is not None

    def get_selection(self) -> tuple[int, int] | None:
        return self._selection

    def coordinate_to_character_index(self, local_x: int, text: str | None = None) -> int:
        """Local x -> character index; text defaults to get_text(). Backward compat."""
        t = text if text is not None else self._get_text()
        font = self._get_font()
        return _coordinate_to_character_index(local_x, t, font)

    def should_start_selection(self, local_x: int, local_y: int, width: int, height: int) -> bool:
        """Aligns with OpenTUI shouldStartSelection(): true if (local_x, local_y) maps to valid char index."""
        if local_x < 0 or local_x >= width or local_y < 0 or local_y >= height:
            return False
        text = self._get_text()
        font = self._get_font()
        char_index = _coordinate_to_character_index(local_x, text, font)
        return 0 <= char_index <= len(text)

    def on_local_selection_changed(
        self,
        local_selection: LocalSelectionBounds | None,
        width: int,
        height: int,
    ) -> bool:
        """Update internal (start, end) from local bounds; return True if changed. Aligns with OpenTUI onLocalSelectionChanged()."""
        previous = self._selection
        if local_selection is None or not local_selection.is_active:
            self._selection = None
            return previous is not None

        text = self._get_text()
        font = self._get_font()
        sel_start = (local_selection.anchor_x, local_selection.anchor_y)
        sel_end = (local_selection.focus_x, local_selection.focus_y)

        if height - 1 < sel_start[1] or 0 > sel_end[1]:
            self._selection = None
            return previous is not None

        start_char = 0
        end_char = len(text)

        if sel_start[1] > height - 1:
            self._selection = None
            return previous is not None
        if 0 <= sel_start[1] <= height - 1 and sel_start[0] > 0:
            start_char = _coordinate_to_character_index(sel_start[0], text, font)

        if sel_end[1] < 0:
            self._selection = None
            return previous is not None
        if 0 <= sel_end[1] <= height - 1:
            if sel_end[0] >= 0:
                end_char = _coordinate_to_character_index(sel_end[0], text, font)
            else:
                end_char = 0

        if start_char < end_char and 0 <= start_char <= len(text) and 0 <= end_char <= len(text):
            self._selection = (start_char, end_char)
        else:
            self._selection = None

        return (
            (previous is None and self._selection is not None)
            or (previous is not None and self._selection is None)
            or (previous is not None and self._selection is not None and (previous[0] != self._selection[0] or previous[1] != self._selection[1]))
        )
