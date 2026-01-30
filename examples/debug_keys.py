#!/usr/bin/env python3
"""调试按键：按任意键打印 keypress 的 name/char，按 q 退出。用于确认方向键等是否被正确解析。"""

import select
import sys

from pytui.core.keyboard import KeyboardHandler


def main() -> None:
    try:
        import termios
        import tty
        fd = sys.stdin.fileno()
        saved = termios.tcgetattr(fd)
        tty.setraw(fd)
    except Exception as e:
        print("Raw mode failed:", e, file=sys.stderr)
        return

    k = KeyboardHandler()
    print("Press keys (arrows, Tab, etc.). Press 'q' to quit.", flush=True)

    def on_key(key: dict) -> None:
        name = key.get("name", "")
        char = key.get("char", "")
        ctrl = key.get("ctrl", False)
        alt = key.get("alt", False)
        shift = key.get("shift", False)
        mods = []
        if ctrl:
            mods.append("ctrl")
        if alt:
            mods.append("alt")
        if shift:
            mods.append("shift")
        mod = "+".join(mods) if mods else ""
        rep = repr(char) if char else '""'
        line = f"  name={name!r} char={rep} {mod}".strip()
        print(line, flush=True)
        if name == "q" or (char == "q" and not ctrl):
            raise SystemExit(0)

    k.on("keypress", on_key)

    try:
        while True:
            # 排空当前可用输入，保证多字节序列（如方向键）一次解析
            n = 0
            while n < 64 and select.select([sys.stdin], [], [], 0)[0]:
                data = sys.stdin.read(1)
                if data:
                    k.feed(data)
                    n += 1
                else:
                    break
            if not select.select([sys.stdin], [], [], 0.05)[0]:
                pass  # 无输入时短暂等待，避免忙等
    except SystemExit:
        pass
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        except Exception:
            pass
        print("Bye.", flush=True)


if __name__ == "__main__":
    main()
