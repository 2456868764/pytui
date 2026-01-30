# pytui.core.colors - color parsing


# RGBA: (r, g, b, a), a=0 表示透明
ColorTuple = tuple[int, int, int, int]


def parse_color(value: str) -> ColorTuple:
    """解析颜色字符串为 (r, g, b, a)。

    支持:
    - '#rrggbb' / '#RRGGBB'
    - '#rgb' -> 扩展为 #rrggbb
    - 'transparent' -> (0, 0, 0, 0)
    """
    if not value or value.strip().lower() == "transparent":
        return (0, 0, 0, 0)

    s = value.strip()
    if s.startswith("#"):
        s = s[1:]
    else:
        raise ValueError(f"Unsupported color format: {value!r}")

    hex_chars = set("0123456789abcdefABCDEF")
    if not all(c in hex_chars for c in s):
        raise ValueError(f"Invalid hex color: {value!r}")

    if len(s) == 6:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return (r, g, b, 255)
    if len(s) == 3:
        r = int(s[0] * 2, 16)
        g = int(s[1] * 2, 16)
        b = int(s[2] * 2, 16)
        return (r, g, b, 255)

    raise ValueError(f"Invalid hex color: {value!r}")
