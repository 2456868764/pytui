# pytui.lib.terminal_capability_detection - Aligns with OpenTUI lib/terminal-capability-detection.ts
# is_capability_response, is_pixel_resolution_response, parse_pixel_resolution

import re


def is_capability_response(sequence: str) -> bool:
    """True if sequence matches any known terminal capability response (DECRPM, CPR, XTVersion, etc.)."""
    if re.search(r"\x1b\[\?\d+(?:;\d+)*\$y", sequence):
        return True
    if re.search(r"\x1b\[1;(?!1R)\d+R", sequence):
        return True
    if re.search(r"\x1bP>\|[\s\S]*?\x1b\\", sequence):
        return True
    if re.search(r"\x1b_G[\s\S]*?\x1b\\", sequence):
        return True
    if re.search(r"\x1b\[\?\d+(?:;\d+)?u", sequence):
        return True
    if re.search(r"\x1b\[\?[0-9;]*c", sequence):
        return True
    return False


def is_pixel_resolution_response(sequence: str) -> bool:
    """True if sequence is pixel resolution response (ESC[4;height;widtht)."""
    return bool(re.search(r"\x1b\[4;\d+;\d+t", sequence))


def parse_pixel_resolution(sequence: str) -> tuple[int, int] | None:
    """Parse pixel resolution from ESC[4;height;widtht. Returns (width, height) or None."""
    m = re.search(r"\x1b\[4;(\d+);(\d+)t", sequence)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    return None
