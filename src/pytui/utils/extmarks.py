# pytui.utils.extmarks - 行内标记/装饰（高亮、诊断等）扩展点


from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Extmark:
    """行内标记：在 [start, end) 显示宽度偏移上的装饰。"""

    id: int
    start: int  # 显示宽度偏移（含换行），非字符串索引
    end: int
    virtual: bool = False
    style_id: int | None = None
    priority: int | None = None
    data: Any = None
    type_id: int = 0


class ExtmarksStore:
    """extmarks 存储：按 id 管理，支持按区间查询。用于高亮、诊断等叠加层。"""

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
        """添加一条 extmark，返回 id。"""
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
        """移除指定 id 的 extmark。"""
        if eid in self._marks:
            del self._marks[eid]
            return True
        return False

    def get(self, eid: int) -> Extmark | None:
        return self._marks.get(eid)

    def get_in_range(self, start: int, end: int) -> list[Extmark]:
        """返回与 [start, end) 有交集的 extmarks，按 priority 降序、start 升序。"""
        out = [
            m
            for m in self._marks.values()
            if m.start < end and m.end > start
        ]
        out.sort(key=lambda m: (-(m.priority or 0), m.start))
        return out

    def clear(self) -> None:
        self._marks.clear()

    def __len__(self) -> int:
        return len(self._marks)
