import pytest

from pytui.lib.output_capture import Capture, CapturedWritableStream


def test_capture_size():
    c = Capture()
    assert c.size == 0
    c.write("stdout", "a")
    c.write("stderr", "b")
    assert c.size == 2


def test_capture_claim_output():
    c = Capture()
    c.write("stdout", "hello ")
    c.write("stdout", "world")
    out = c.claim_output()
    assert out == "hello world"
    assert c.size == 0


def test_capture_emit_write():
    c = Capture()
    events = []
    c.on("write", lambda s, d: events.append((s, d)))
    c.write("stdout", "x")
    c.write("stderr", "y")
    assert events == [("stdout", "x"), ("stderr", "y")]


def test_captured_writable_stream():
    c = Capture()
    s = CapturedWritableStream("stdout", c)
    assert s.isTTY is True
    assert s.columns >= 1
    assert s.rows >= 1
    s.write("hello")
    s.write(" world")
    assert c.claim_output() == "hello world"


def test_captured_writable_stream_get_color_depth():
    c = Capture()
    s = CapturedWritableStream("stdout", c)
    assert s.getColorDepth() == 8
