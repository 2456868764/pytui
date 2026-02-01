import pytest

from pytui.lib.singleton import destroy_singleton, has_singleton, singleton


def test_singleton_returns_same_instance():
    v = singleton("test-key-1", lambda: object())
    v2 = singleton("test-key-1", lambda: object())
    assert v is v2


def test_singleton_different_keys_different_values():
    a = singleton("key-a", lambda: 1)
    b = singleton("key-b", lambda: 2)
    assert a == 1
    assert b == 2


def test_has_singleton():
    destroy_singleton("key-has")
    assert has_singleton("key-has") is False
    singleton("key-has", lambda: 42)
    assert has_singleton("key-has") is True
    destroy_singleton("key-has")
    assert has_singleton("key-has") is False


def test_destroy_singleton():
    singleton("key-destroy", lambda: 99)
    assert singleton("key-destroy", lambda: 0) == 99
    destroy_singleton("key-destroy")
    assert singleton("key-destroy", lambda: 100) == 100
