import threading
import time

import pytest

from pytui.lib.queue import ProcessQueue


def test_enqueue_and_process():
    out = []
    q = ProcessQueue(lambda x: out.append(x))
    q.enqueue(1)
    q.enqueue(2)
    time.sleep(0.15)
    assert out == [1, 2]


def test_clear():
    out = []
    q = ProcessQueue(lambda x: out.append(x))
    q.enqueue(1)
    q.clear()
    time.sleep(0.05)
    assert q.size() == 0
    assert len(out) <= 1


def test_is_processing():
    ev = threading.Event()
    q = ProcessQueue(lambda x: ev.wait())
    assert q.is_processing() is False
    q.enqueue(1)
    time.sleep(0.02)
    assert q.is_processing() is True
    ev.set()
    time.sleep(0.05)
    assert q.is_processing() is False


def test_size():
    q = ProcessQueue(lambda x: None)
    assert q.size() == 0
    q.enqueue(1)
    assert q.size() >= 1
    time.sleep(0.1)
    assert q.size() == 0


def test_processor_exception_logged():
    q = ProcessQueue(lambda x: (_ for _ in ()).throw(ValueError("bad")))
    q.enqueue(1)
    time.sleep(0.1)
    assert q.size() == 0
