# pytui.lib.tree_sitter.types - Aligns with OpenTUI lib/tree-sitter/types.ts

from __future__ import annotations

from typing import Any, TypedDict

# SimpleHighlight = [startIndex, endIndex, group, meta?] (OpenTUI)
SimpleHighlight = tuple[int, int, str, Any]  # (start, end, group, meta optional)


class HighlightRange(TypedDict):
    startCol: int
    endCol: int
    group: str


class HighlightResponse(TypedDict, total=False):
    line: int
    highlights: list[HighlightRange]
    droppedHighlights: list[HighlightRange]


class HighlightMeta(TypedDict, total=False):
    isInjection: bool
    injectionLang: str
    containsInjection: bool
    conceal: str | None
    concealLines: str | None


class InjectionMapping(TypedDict, total=False):
    nodeTypes: dict[str, str]
    infoStringMap: dict[str, str]


class FiletypeParserOptions(TypedDict, total=False):
    filetype: str
    queries: dict[str, list[str]]
    wasm: str
    injectionMapping: InjectionMapping


class BufferState(TypedDict, total=False):
    id: int
    version: int
    content: str
    filetype: str
    hasParser: bool


class ParsedBuffer(BufferState):
    """BufferState with hasParser: True. Aligns OpenTUI ParsedBuffer."""

    hasParser: bool  # True


class TreeSitterClientOptions(TypedDict, total=False):
    dataPath: str
    workerPath: str
    initTimeout: int


class Edit(TypedDict, total=False):
    startIndex: int
    oldEndIndex: int
    newEndIndex: int
    startPosition: dict[str, int]
    oldEndPosition: dict[str, int]
    newEndPosition: dict[str, int]


class PerformanceStats(TypedDict):
    averageParseTime: float
    parseTimes: list[float]
    averageQueryTime: float
    queryTimes: list[float]
