# pytui.utils.diff - line-based text diff
# Aligns with OpenTUI parsePatch: hunks with oldStart/newStart and per-line +/-/space.

import re
from dataclasses import dataclass, field
from typing import Optional

# (tag, line): tag is " " (unchanged), "+" (added), "-" (removed)
DiffLine = tuple[str, str]


@dataclass
class DiffHunk:
    """Single hunk: @@ -old_start,old_count +new_start,new_count @@"""
    old_start: int
    new_start: int
    lines: list[DiffLine] = field(default_factory=list)


@dataclass
class ParsedPatch:
    """First patch from unified diff (OpenTUI uses patches[0])."""
    hunks: list[DiffHunk] = field(default_factory=list)


def parse_patch(diff_text: str) -> tuple[Optional[ParsedPatch], Optional[str]]:
    """Parse unified diff into hunks with line numbers. Returns (patch, None) or (None, error_message). Aligns with OpenTUI parsePatch."""
    if not (diff_text or "").strip():
        return ParsedPatch(), None
    text = (diff_text or "").strip()
    lines = text.splitlines()
    hunks: list[DiffHunk] = []
    # @@ -oldStart[,oldCount] +newStart[,newCount] @@
    hunk_re = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")
    i = 0
    while i < len(lines):
        raw = lines[i]
        m = hunk_re.match(raw)
        if m:
            old_start = int(m.group(1))
            new_start = int(m.group(3))
            hunk_lines: list[DiffLine] = []
            i += 1
            while i < len(lines):
                line = lines[i]
                if len(line) == 0:
                    i += 1
                    continue
                fc = line[0]
                if fc == " ":
                    hunk_lines.append((" ", line[1:]))
                    i += 1
                elif fc == "+" and not line.startswith("+++"):
                    hunk_lines.append(("+", line[1:]))
                    i += 1
                elif fc == "-" and not line.startswith("---"):
                    hunk_lines.append(("-", line[1:]))
                    i += 1
                elif fc == "\\":
                    i += 1
                else:
                    break
            hunks.append(DiffHunk(old_start=old_start, new_start=new_start, lines=hunk_lines))
            continue
        i += 1
    if not hunks:
        return None, "No valid hunks found"
    return ParsedPatch(hunks=hunks), None


# (tag, content, old_line_num or None, new_line_num or None)
UnifiedLine = tuple[str, str, Optional[int], Optional[int]]


def flattened_unified_lines(patch: ParsedPatch) -> list[UnifiedLine]:
    """Flatten hunks to list of (tag, content, old_num, new_num) for unified view. Aligns with OpenTUI buildUnifiedView."""
    out: list[UnifiedLine] = []
    for h in patch.hunks:
        old_num, new_num = h.old_start, h.new_start
        for tag, content in h.lines:
            if tag == "+":
                out.append((tag, content, None, new_num))
                new_num += 1
            elif tag == "-":
                out.append((tag, content, old_num, None))
                old_num += 1
            else:
                out.append((tag, content, old_num, new_num))
                old_num += 1
                new_num += 1
    return out


@dataclass
class LogicalLine:
    """One line in split view. Aligns with OpenTUI LogicalLine."""
    content: str
    line_num: Optional[int] = None
    hide_line_number: bool = False
    type: str = "context"  # "context" | "add" | "remove" | "empty"


def build_split_logical_lines(patch: ParsedPatch) -> tuple[list[LogicalLine], list[LogicalLine]]:
    """Build left (removed/context) and right (added/context) logical lines. Aligns with OpenTUI buildSplitView."""
    left_lines: list[LogicalLine] = []
    right_lines: list[LogicalLine] = []
    for h in patch.hunks:
        old_num, new_num = h.old_start, h.new_start
        i = 0
        lines = h.lines
        while i < len(lines):
            tag, content = lines[i][0], lines[i][1]
            if tag == " ":
                left_lines.append(LogicalLine(content=content, line_num=old_num, type="context"))
                right_lines.append(LogicalLine(content=content, line_num=new_num, type="context"))
                old_num += 1
                new_num += 1
                i += 1
            elif tag == "\\":
                i += 1
            else:
                removes: list[tuple[str, int]] = []
                adds: list[tuple[str, int]] = []
                while i < len(lines):
                    t, c = lines[i][0], lines[i][1]
                    if t == " " or t == "\\":
                        break
                    if t == "-":
                        removes.append((c, old_num))
                        old_num += 1
                    elif t == "+":
                        adds.append((c, new_num))
                        new_num += 1
                    i += 1
                max_len = max(len(removes), len(adds))
                for j in range(max_len):
                    if j < len(removes):
                        left_lines.append(LogicalLine(content=removes[j][0], line_num=removes[j][1], type="remove"))
                    else:
                        left_lines.append(LogicalLine(content="", hide_line_number=True, type="empty"))
                    if j < len(adds):
                        right_lines.append(LogicalLine(content=adds[j][0], line_num=adds[j][1], type="add"))
                    else:
                        right_lines.append(LogicalLine(content="", hide_line_number=True, type="empty"))
    return left_lines, right_lines


def parse_unified_diff(diff_text: str) -> list[DiffLine]:
    """Parse unified diff string into list of (tag, line_content). Fallback when parse_patch not used."""
    out: list[DiffLine] = []
    for raw in (diff_text or "").splitlines():
        if len(raw) >= 1 and raw[0] == "+" and not raw.startswith("+++"):
            out.append(("+", raw[1:]))
        elif len(raw) >= 1 and raw[0] == "-" and not raw.startswith("---"):
            out.append(("-", raw[1:]))
        elif len(raw) >= 1 and raw[0] == " ":
            out.append((" ", raw[1:]))
        else:
            out.append((" ", raw))
    return out


def diff_lines(a: str, b: str) -> list[DiffLine]:
    """比较两段文本（按行），返回 (tag, line) 列表。"""
    la = a.splitlines() if a else []
    lb = b.splitlines() if b else []
    return _diff_line_sequences(la, lb)


def _diff_line_sequences(la: list[str], lb: list[str]) -> list[DiffLine]:
    """LCS-based line diff。"""
    n, m = len(la), len(lb)
    # dp[i][j] = LCS length of la[:i], lb[:j]
    dp: list[list[int]] = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if la[i - 1] == lb[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    out: list[DiffLine] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and la[i - 1] == lb[j - 1]:
            out.append((" ", la[i - 1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
            out.append(("+", lb[j - 1]))
            j -= 1
        else:
            out.append(("-", la[i - 1]))
            i -= 1
    out.reverse()
    return out
