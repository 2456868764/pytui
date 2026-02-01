# Aligns with OpenTUI lib/stdin-buffer.test.ts

import time

import pytest

from pytui.lib.stdin_buffer import StdinBuffer


@pytest.fixture
def buffer():
    b = StdinBuffer({"timeout": 10})
    return b


@pytest.fixture
def emitted(buffer):
    out: list[str] = []

    def on_data(seq: str) -> None:
        out.append(seq)

    buffer.on("data", on_data)
    return out


def process_input(buf: StdinBuffer, data: str | bytes) -> None:
    buf.process(data)


class TestStdinBufferRegularCharacters:
    """Aligns: stdin-buffer.test.ts - Regular Characters"""

    def test_pass_through_regular_characters_immediately(self, buffer, emitted):
        process_input(buffer, "a")
        assert emitted == ["a"]

    def test_pass_through_multiple_regular_characters(self, buffer, emitted):
        process_input(buffer, "abc")
        assert emitted == ["a", "b", "c"]

    def test_handle_unicode_characters(self, buffer, emitted):
        process_input(buffer, "hello 世界")
        assert emitted == ["h", "e", "l", "l", "o", " ", "世", "界"]


class TestStdinBufferCompleteEscapeSequences:
    """Aligns: stdin-buffer.test.ts - Complete Escape Sequences"""

    def test_pass_through_complete_mouse_sgr_sequences(self, buffer, emitted):
        mouse_seq = "\x1b[<35;20;5m"
        process_input(buffer, mouse_seq)
        assert emitted == [mouse_seq]

    def test_pass_through_complete_arrow_key_sequences(self, buffer, emitted):
        up_arrow = "\x1b[A"
        process_input(buffer, up_arrow)
        assert emitted == [up_arrow]

    def test_pass_through_complete_function_key_sequences(self, buffer, emitted):
        f1 = "\x1b[11~"
        process_input(buffer, f1)
        assert emitted == [f1]

    def test_pass_through_meta_key_sequences(self, buffer, emitted):
        meta_a = "\x1ba"
        process_input(buffer, meta_a)
        assert emitted == [meta_a]

    def test_pass_through_ss3_sequences(self, buffer, emitted):
        ss3 = "\x1bOA"
        process_input(buffer, ss3)
        assert emitted == [ss3]


class TestStdinBufferPartialEscapeSequences:
    """Aligns: stdin-buffer.test.ts - Partial Escape Sequences"""

    def test_buffer_incomplete_mouse_sgr_sequence(self, buffer, emitted):
        process_input(buffer, "\x1b")
        assert emitted == []
        assert buffer.get_buffer() == "\x1b"

        process_input(buffer, "[<35")
        assert emitted == []
        assert buffer.get_buffer() == "\x1b[<35"

        process_input(buffer, ";20;5m")
        assert emitted == ["\x1b[<35;20;5m"]
        assert buffer.get_buffer() == ""

    def test_buffer_incomplete_csi_sequence(self, buffer, emitted):
        process_input(buffer, "\x1b[")
        assert emitted == []

        process_input(buffer, "1;")
        assert emitted == []

        process_input(buffer, "5H")
        assert emitted == ["\x1b[1;5H"]

    def test_buffer_split_across_many_chunks(self, buffer, emitted):
        for ch in "\x1b[<35;20;5m":
            process_input(buffer, ch)
        assert emitted == ["\x1b[<35;20;5m"]

    def test_flush_incomplete_sequence_after_timeout(self, buffer, emitted):
        process_input(buffer, "\x1b[<35")
        assert emitted == []
        time.sleep(0.02)
        assert len(emitted) >= 1
        assert emitted[0] == "\x1b[<35"


class TestStdinBufferFlushAndClear:
    def test_flush_returns_pending(self, buffer, emitted):
        process_input(buffer, "\x1b[")
        assert buffer.get_buffer() == "\x1b["
        flushed = buffer.flush()
        assert flushed == ["\x1b["]
        assert buffer.get_buffer() == ""

    def test_clear_resets_buffer(self, buffer, emitted):
        process_input(buffer, "\x1b[")
        buffer.clear()
        assert buffer.get_buffer() == ""

    def test_get_buffer_returns_current(self, buffer):
        process_input(buffer, "a")
        buffer.process("b")
        assert buffer.get_buffer() == ""

    def test_destroy_clears(self, buffer):
        process_input(buffer, "\x1b[")
        buffer.destroy()
        assert buffer.get_buffer() == ""


class TestStdinBufferBracketedPaste:
    """Aligns: stdin-buffer.test.ts - Bracketed Paste"""

    def test_emit_paste_for_bracketed_paste(self, buffer):
        pasted: list[str] = []
        buffer.on("paste", lambda s: pasted.append(s))
        process_input(buffer, "\x1b[200~hello\x1b[201~")
        assert pasted == ["hello"]

    def test_data_before_paste_emitted_as_data(self, buffer, emitted):
        pasted: list[str] = []
        buffer.on("paste", lambda s: pasted.append(s))
        process_input(buffer, "ab\x1b[200~x\x1b[201~")
        assert emitted == ["a", "b"]
        assert pasted == ["x"]
