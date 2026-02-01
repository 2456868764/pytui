# tests/unit/core/test_keyboard.py
# Tests keyboard pipeline: StdinBuffer + InternalKeyHandler (same composition as Renderer). Aligns keyboard-alignment-refactor-plan.

import pytest

from pytui.lib.key_handler import InternalKeyHandler
from pytui.lib.stdin_buffer import StdinBuffer


def _make_pipeline(use_kitty_keyboard: bool = False) -> tuple[StdinBuffer, InternalKeyHandler]:
    """StdinBuffer + InternalKeyHandler wired as in Renderer."""
    buf = StdinBuffer()
    handler = InternalKeyHandler(use_kitty_keyboard=use_kitty_keyboard)
    buf.on("data", handler.process_input)
    buf.on("paste", handler.process_paste)
    return buf, handler


class TestKeyboardPipeline:
    def test_single_char(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("a")
        assert len(out) == 1
        assert out[0].get("char") == "a"
        assert out[0].get("name") == "a"

    def test_ctrl(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x03")  # Ctrl+C
        assert len(out) == 1
        assert out[0].get("ctrl") is True
        assert out[0].get("name") == "c"

    def test_backspace_ascii_127_and_08(self):
        """\x7f (DEL) 与 \x08 (BS) 均识别为 backspace（Mac 等终端发 \x7f）。"""
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x7f")
        assert len(out) == 1
        assert out[0].get("name") == "backspace"
        out.clear()
        buf.process("\x08")
        assert len(out) == 1
        assert out[0].get("name") == "backspace"

    def test_tab_emits_name_tab(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\t")
        assert len(out) == 1
        assert out[0].get("name") == "tab"
        assert out[0].get("char") == "\t"
        assert out[0].get("shift") is False

    def test_shift_tab_csi_z(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[Z")  # Shift+Tab (backtab)
        assert len(out) == 1
        assert out[0].get("name") == "backtab"
        assert out[0].get("shift") is True

    def test_kitty_csi_u_escape(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[27;1u")  # Escape, no modifier
        assert len(out) == 1
        assert out[0].get("name") == "escape"
        assert out[0].get("ctrl") is False

    def test_kitty_csi_u_ctrl_a(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[97;5u")  # Ctrl+a (97='a', 5=1+4)
        assert len(out) == 1
        assert out[0].get("name") == "a"
        assert out[0].get("ctrl") is True
        assert out[0].get("char") == "a"

    def test_kitty_csi_u_printable(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[98;1u")  # 'b' no modifier
        assert len(out) == 1
        assert out[0].get("name") == "b"
        assert out[0].get("char") == "b"

    def test_legacy_csi_with_modifier(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[1;5C")  # Ctrl+Right
        assert len(out) == 1
        assert out[0].get("name") == "right"
        assert out[0].get("ctrl") is True

    def test_ss3_arrow_keys(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b")
        buf.process("O")
        buf.process("C")  # right
        assert len(out) == 1
        assert out[0].get("name") == "right"
        out.clear()
        buf.process("\x1b")
        buf.process("O")
        buf.process("D")  # left
        assert len(out) == 1
        assert out[0].get("name") == "left"

    def test_csi_with_digit_mac_style(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[1A")
        assert len(out) == 1
        assert out[0].get("name") == "up"
        out.clear()
        buf.process("\x1b[0B")
        assert len(out) == 1
        assert out[0].get("name") == "down"
        out.clear()
        buf.process("\x1b[1C")
        assert len(out) == 1
        assert out[0].get("name") == "right"
        out.clear()
        buf.process("\x1b[1D")
        assert len(out) == 1
        assert out[0].get("name") == "left"

    def test_csi_o_arrow_keys_mac_application_cursor(self):
        """Mac/部分终端发 ESC [ O A 等（application cursor），应解析为 up/down/left/right。"""
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[OA")
        assert len(out) == 1
        assert out[0].get("name") == "up"
        out.clear()
        buf.process("\x1b[OB")
        assert len(out) == 1
        assert out[0].get("name") == "down"
        out.clear()
        buf.process("\x1b[OC")
        assert len(out) == 1
        assert out[0].get("name") == "right"
        out.clear()
        buf.process("\x1b[OD")
        assert len(out) == 1
        assert out[0].get("name") == "left"

    def test_key_event_has_sequence_meta_option(self):
        """KeyEvent aligns with OpenTUI: name, sequence, ctrl, shift, meta, option."""
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("a")
        assert out[0].get("sequence") == "a"
        assert out[0].get("meta") is False
        assert out[0].get("option") is False
        out.clear()
        buf.process("\x1b[OD")  # left
        assert out[0].get("sequence") == "\x1b[OD"
        assert out[0].get("meta") is False
        assert out[0].get("option") is False
        out.clear()
        buf.process("\x1bc")  # Alt+c
        assert out[0].get("meta") is True
        assert out[0].get("option") is True

    def test_bracketed_paste(self):
        """Bracketed paste: ESC [ 200 ~ ... ESC [ 201 ~ emits paste with text."""
        buf, handler = _make_pipeline()
        pasted = []
        handler.on("paste", lambda e: pasted.append(e))
        buf.process("\x1b[200~hello world\x1b[201~")
        assert len(pasted) == 1
        assert pasted[0].get("text") == "hello world"

    # --- Tab, Shift+Tab, Arrow keys (explicit navigation coverage) ---

    def test_tab_emits_tab_name_and_sequence(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\t")
        assert len(out) == 1
        assert out[0].get("name") == "tab"
        assert out[0].get("char") == "\t"
        assert out[0].get("shift") is False
        assert out[0].get("sequence") == "\t"

    def test_shift_tab_emits_backtab_with_shift(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\x1b[Z")
        assert len(out) == 1
        assert out[0].get("name") == "backtab"
        assert out[0].get("shift") is True
        assert out[0].get("sequence") == "\x1b[Z"

    def test_arrow_keys_csi_plain_up_down_left_right(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        for seq, name in [("\x1b[A", "up"), ("\x1b[B", "down"), ("\x1b[C", "right"), ("\x1b[D", "left")]:
            out.clear()
            buf.process(seq)
            assert len(out) == 1, f"sequence {seq!r} should emit one key"
            assert out[0].get("name") == name
            assert out[0].get("sequence") == seq

    def test_arrow_keys_csi_with_digit_up_down_left_right(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        for seq, name in [("\x1b[1A", "up"), ("\x1b[0B", "down"), ("\x1b[1C", "right"), ("\x1b[1D", "left")]:
            out.clear()
            buf.process(seq)
            assert len(out) == 1
            assert out[0].get("name") == name
            assert out[0].get("sequence") == seq

    def test_arrow_keys_ss3_application_up_down_left_right(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        for seq, name in [("\x1b[OA", "up"), ("\x1b[OB", "down"), ("\x1b[OC", "right"), ("\x1b[OD", "left")]:
            out.clear()
            buf.process(seq)
            assert len(out) == 1
            assert out[0].get("name") == name
            assert out[0].get("sequence") == seq

    def test_navigation_keys_tab_shift_tab_and_arrows_in_order(self):
        buf, handler = _make_pipeline()
        out = []
        handler.on("keypress", lambda key: out.append(key))
        buf.process("\t")
        buf.process("\x1b[Z")
        buf.process("\x1b[A")
        buf.process("\x1b[B")
        buf.process("\x1b[C")
        buf.process("\x1b[D")
        assert len(out) == 6
        assert out[0].get("name") == "tab" and out[0].get("shift") is False
        assert out[1].get("name") == "backtab" and out[1].get("shift") is True
        assert out[2].get("name") == "up"
        assert out[3].get("name") == "down"
        assert out[4].get("name") == "right"
        assert out[5].get("name") == "left"
