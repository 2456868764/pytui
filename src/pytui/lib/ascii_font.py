# pytui.lib.ascii_font - Aligns with OpenTUI lib/ascii.font.ts
# measureText, getCharacterPositions, coordinateToCharacterIndex, renderFontToFrameBuffer, fonts.

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_LOG = logging.getLogger(__name__)

# Font name type. Aligns OpenTUI ASCIIFontName.
ASCIIFontName = str  # "tiny" | "block" | "shade" | "slick" | "huge" | "grid" | "pallet"

_FONTS_DIR = Path(__file__).resolve().parent / "fonts"
_loaded_fonts: dict[str, dict[str, Any]] = {}

# Aligns OpenTUI fonts: lazy dict of name -> font def (load on first access).
FONT_NAMES = ("tiny", "block", "shade", "slick", "huge", "grid", "pallet")


class _FontsProxy:
    """Lazy proxy for fonts dict. Aligns OpenTUI export const fonts = { tiny, block, ... }."""

    def __getitem__(self, key: str) -> dict[str, Any]:
        return _load_font(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return _load_font(key)
        except Exception:
            return default

    def __contains__(self, key: str) -> bool:
        return key in FONT_NAMES


fonts: _FontsProxy = _FontsProxy()


def _load_font(name: str | dict[str, Any]) -> dict[str, Any]:
    """Load font by name (str) or return inline font def (dict)."""
    if isinstance(name, dict):
        return name
    if name not in _loaded_fonts:
        path = _FONTS_DIR / f"{name}.json"
        if not path.exists():
            _loaded_fonts[name] = {"name": name, "lines": 1, "letterspace_size": 0, "chars": {}}
            return _loaded_fonts[name]
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("lines", data.get("lines", 1))
        data.setdefault("letterspace_size", data.get("letterspace_size", 1))
        data.setdefault("chars", data.get("chars", {}))
        _loaded_fonts[name] = data
    return _loaded_fonts[name]


def get_font(name: str | dict[str, Any]) -> dict[str, Any]:
    """Get parsed font definition. Aligns with OpenTUI getParsedFont."""
    return _load_font(name)


def register_font(name: str, font_def: dict[str, Any]) -> None:
    """Register a custom font by name (for tests / compatibility)."""
    _loaded_fonts[name] = dict(font_def)


class _MeasureResult:
    """Result of measure_text; supports dict-style ['width']/['height'] and tuple unpack (w, h)."""

    __slots__ = ("width", "height")

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def __getitem__(self, key: str | int) -> int:
        if key in (0, "width"):
            return self.width
        if key in (1, "height"):
            return self.height
        raise KeyError(key)

    def __iter__(self) -> Any:
        yield self.width
        yield self.height


def measure_text(text: str = "", font: str | dict[str, Any] = "tiny") -> _MeasureResult:
    """Return width and height of text in font. Aligns with OpenTUI measureText(). Font not found -> (0,0) + warn."""
    font_def = _load_font(font)
    chars_map = font_def.get("chars", {})
    if not chars_map and not isinstance(font, dict):
        _LOG.warning("Font '%s' not found", font)
        return _MeasureResult(0, 0)
    lines_count = font_def.get("lines", 1)
    letterspace_size = font_def.get("letterspace_size", 1)
    current_x = 0
    for i, char in enumerate(text):
        c = char.upper() if len(char) == 1 else " "
        char_def = chars_map.get(c)
        if char_def is None:
            space_def = chars_map.get(" ")
            if space_def and space_def:
                char_width = sum(len(ln) for ln in space_def[0:1])
            else:
                char_width = 1
        else:
            char_width = sum(len(ln) for ln in (char_def[0] if char_def else []))
        current_x += char_width
        if i < len(text) - 1:
            current_x += letterspace_size
    return _MeasureResult(current_x or 1, lines_count)


def get_character_positions(text: str, font: str | dict[str, Any] = "tiny") -> list[int]:
    """Return x position for each character boundary. Aligns with OpenTUI getCharacterPositions(). Font not found -> [0]."""
    font_def = _load_font(font)
    chars_map = font_def.get("chars", {})
    if not chars_map and not isinstance(font, dict):
        return [0]
    letterspace_size = font_def.get("letterspace_size", 1)
    positions = [0]
    current_x = 0
    for i, char in enumerate(text):
        c = char.upper() if len(char) == 1 else " "
        char_def = chars_map.get(c)
        if char_def is None:
            space_def = chars_map.get(" ")
            char_width = sum(len(line) for line in (space_def[0:1] if space_def else [])) or 1
        else:
            char_width = sum(len(line) for line in (char_def[0] if char_def else []))
        current_x += char_width
        if i < len(text) - 1:
            current_x += letterspace_size
        positions.append(current_x)
    return positions


def coordinate_to_character_index(x: int, text: str, font: str | dict[str, Any] = "tiny") -> int:
    """Map local x to character index. Aligns with OpenTUI coordinateToCharacterIndex()."""
    positions = get_character_positions(text, font)
    if x < 0:
        return 0
    for i in range(len(positions) - 1):
        curr, nxt = positions[i], positions[i + 1]
        if curr <= x < nxt:
            mid = curr + (nxt - curr) / 2
            return i + 1 if x >= mid else i
    if positions and x >= positions[-1]:
        return len(text)
    return 0


def render_font_to_frame_buffer(
    buffer: Any,
    text: str,
    x: int = 0,
    y: int = 0,
    color: Any = None,
    backgroundColor: Any = None,
    font: str = "tiny",
) -> dict[str, int]:
    """Render ASCII font text into buffer. Aligns with OpenTUI renderFontToFrameBuffer().
    color/backgroundColor can be (r,g,b,a) or ColorInput; buffer must have set_cell/set_cell_with_alpha.
    """
    from pytui.core.buffer import Cell
    from pytui.lib.rgba import parse_color_to_tuple

    width = buffer.width
    height = buffer.height
    font_def = _load_font(font)
    chars_map = font_def.get("chars", {})
    lines_count = font_def.get("lines", 1)
    letterspace_size = font_def.get("letterspace_size", 1)
    fg = parse_color_to_tuple(color) if color is not None else (255, 255, 255, 255)
    bg = parse_color_to_tuple(backgroundColor) if backgroundColor is not None else (0, 0, 0, 255)
    colors = [fg]
    current_x = x
    start_x = x
    for i, char in enumerate(text):
        c = char.upper() if len(char) == 1 else " "
        char_def = chars_map.get(c)
        if char_def is None:
            space_def = chars_map.get(" ")
            if space_def:
                space_width = sum(len(line) for line in space_def[0:1])
            else:
                space_width = 1
            current_x += space_width
            if i < len(text) - 1:
                current_x += letterspace_size
            continue
        char_width = sum(len(line) for line in (char_def[0] if char_def else []))
        if current_x >= width:
            break
        if current_x + char_width < 0:
            current_x += char_width + letterspace_size
            continue
        for line_idx, line in enumerate(char_def):
            if line_idx >= lines_count:
                break
            render_y = y + line_idx
            if render_y < 0 or render_y >= height:
                continue
            seg_fg = colors[0] if colors else fg
            for ch_idx, ch in enumerate(line):
                render_x = current_x + ch_idx
                if 0 <= render_x < width and ch != " ":
                    buffer.set_cell(render_x, render_y, Cell(char=ch, fg=seg_fg, bg=bg))
        current_x += char_width
        if i < len(text) - 1:
            current_x += letterspace_size
    return {"width": current_x - start_x, "height": lines_count}
