# tests/unit/core/test_keyboard.py

import pytest

pytest.importorskip("pytui.core.keyboard")


class TestKeyboardHandler:
    def test_single_char(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("a")
        assert len(out) == 1
        assert out[0].get("char") == "a"
        assert out[0].get("name") == "a"

    def test_ctrl(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x03")  # Ctrl+C
        assert len(out) == 1
        assert out[0].get("ctrl") is True
        assert out[0].get("name") == "c"

    def test_backspace_ascii_127_and_08(self):
        """\x7f (DEL) 与 \x08 (BS) 均识别为 backspace（Mac 等终端发 \x7f）。"""
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x7f")
        assert len(out) == 1
        assert out[0].get("name") == "backspace"
        out.clear()
        k.feed("\x08")
        assert len(out) == 1
        assert out[0].get("name") == "backspace"

    def test_tab_emits_name_tab(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\t")
        assert len(out) == 1
        assert out[0].get("name") == "tab"
        assert out[0].get("char") == "\t"
        assert out[0].get("shift") is False

    def test_shift_tab_csi_z(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[Z")  # Shift+Tab
        assert len(out) == 1
        assert out[0].get("name") == "tab"
        assert out[0].get("shift") is True

    def test_kitty_csi_u_escape(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[27;1u")  # Escape, no modifier
        assert len(out) == 1
        assert out[0].get("name") == "escape"
        assert out[0].get("ctrl") is False

    def test_kitty_csi_u_ctrl_a(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[97;5u")  # Ctrl+a (97='a', 5=1+4)
        assert len(out) == 1
        assert out[0].get("name") == "a"
        assert out[0].get("ctrl") is True
        assert out[0].get("char") == "a"

    def test_kitty_csi_u_printable(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[98;1u")  # 'b' no modifier
        assert len(out) == 1
        assert out[0].get("name") == "b"
        assert out[0].get("char") == "b"

    def test_legacy_csi_with_modifier(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[1;5C")  # Ctrl+Right
        assert len(out) == 1
        assert out[0].get("name") == "right"
        assert out[0].get("ctrl") is True

    def test_ss3_arrow_keys(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b")  # wait
        k.feed("O")  # still wait (ESC O)
        k.feed("C")  # right
        assert len(out) == 1
        assert out[0].get("name") == "right"
        out.clear()
        k.feed("\x1b")
        k.feed("O")
        k.feed("D")  # left
        assert len(out) == 1
        assert out[0].get("name") == "left"

    def test_csi_with_digit_mac_style(self):
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[1A")  # Mac 常见: up
        assert len(out) == 1
        assert out[0].get("name") == "up"
        out.clear()
        k.feed("\x1b[0B")  # down
        assert len(out) == 1
        assert out[0].get("name") == "down"
        out.clear()
        k.feed("\x1b[1C")  # right
        assert len(out) == 1
        assert out[0].get("name") == "right"
        out.clear()
        k.feed("\x1b[1D")  # left
        assert len(out) == 1
        assert out[0].get("name") == "left"

    def test_csi_o_arrow_keys_mac_application_cursor(self):
        """Mac/部分终端发 ESC [ O A 等（application cursor），应解析为 up/down/left/right。"""
        from pytui.core.keyboard import KeyboardHandler

        k = KeyboardHandler()
        out = []
        k.on("keypress", lambda key: out.append(key))
        k.feed("\x1b[OA")  # up
        assert len(out) == 1
        assert out[0].get("name") == "up"
        out.clear()
        k.feed("\x1b[OB")  # down
        assert len(out) == 1
        assert out[0].get("name") == "down"
        out.clear()
        k.feed("\x1b[OC")  # right
        assert len(out) == 1
        assert out[0].get("name") == "right"
        out.clear()
        k.feed("\x1b[OD")  # left
        assert len(out) == 1
        assert out[0].get("name") == "left"
