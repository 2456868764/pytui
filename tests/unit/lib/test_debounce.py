import time

import pytest

from pytui.lib.debounce import (
    DebounceController,
    clear_all_debounces,
    clear_debounce_scope,
    create_debounce,
)


def test_debounce_resolves_after_ms():
    c = create_debounce("scope1")
    out = []
    f = c.debounce("id1", 50, lambda: out.append(1) or 42)
    result = f.result(timeout=1)
    assert result == 42
    assert out == [1]


def test_debounce_clears_previous():
    c = create_debounce("scope2")
    out = []
    c.debounce("id2", 100, lambda: out.append("slow"))
    c.debounce("id2", 30, lambda: out.append("fast"))
    time.sleep(0.2)
    assert out == ["fast"]


def test_clear_debounce():
    c = create_debounce("scope3")
    out = []
    c.debounce("id3", 200, lambda: out.append(1))
    c.clear_debounce("id3")
    time.sleep(0.25)
    assert out == []


def test_clear_scope():
    c = create_debounce("scope4")
    out = []
    c.debounce("a", 200, lambda: out.append(1))
    c.clear()
    time.sleep(0.25)
    assert out == []


def test_clear_debounce_scope():
    c = create_debounce("scope5")
    c.debounce("x", 500, lambda: None)
    clear_debounce_scope("scope5")
    time.sleep(0.1)
    assert c.debounce("x", 20, lambda: 1).result(timeout=1) == 1


def test_clear_all_debounces():
    c1 = create_debounce("scope6a")
    c2 = create_debounce("scope6b")
    out = []
    c1.debounce("a", 300, lambda: out.append(1))
    c2.debounce("b", 300, lambda: out.append(2))
    clear_all_debounces()
    time.sleep(0.35)
    assert out == []
