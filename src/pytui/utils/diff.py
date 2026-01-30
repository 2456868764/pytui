# pytui.utils.diff - line-based text diff


# (tag, line): tag is " " (unchanged), "+" (added), "-" (removed)
DiffLine = tuple[str, str]


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
