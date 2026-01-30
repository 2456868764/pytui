# pytui.core.rgba - RGBA 统一表示


from __future__ import annotations


class RGBA:
    """RGBA 颜色，r/g/b/a 0–255。可与 parse_color 互用，colors 层可选用。"""

    __slots__ = ("r", "g", "b", "a")

    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255) -> None:
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.a = max(0, min(255, a))

    @classmethod
    def from_hex(cls, value: str) -> RGBA:
        """从 '#rrggbb' 或 '#rgb' 解析。"""
        from pytui.core.colors import parse_color

        t = parse_color(value)
        return cls(t[0], t[1], t[2], t[3])

    @classmethod
    def from_ints(cls, r: int, g: int, b: int, a: int = 255) -> RGBA:
        """从四个 0–255 整型构造。"""
        return cls(r, g, b, a)

    @classmethod
    def from_values(cls, r: float, g: float, b: float, a: float = 1.0) -> RGBA:
        """从 0–1 浮点构造，内部转为 0–255。"""
        return cls(
            int(round(r * 255)),
            int(round(g * 255)),
            int(round(b * 255)),
            int(round(a * 255)),
        )

    def to_tuple(self) -> tuple[int, int, int, int]:
        """转为 (r, g, b, a) 元组，供 buffer/ANSI 使用。"""
        return (self.r, self.g, self.b, self.a)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RGBA):
            return False
        return (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)

    def __repr__(self) -> str:
        return f"RGBA({self.r},{self.g},{self.b},{self.a})"
