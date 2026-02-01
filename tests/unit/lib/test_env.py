import os

import pytest

from pytui.lib.env import (
    clear_env_cache,
    env_registry,
    generate_env_colored,
    generate_env_markdown,
    register_env_var,
)
from pytui.lib.env import env  # noqa: F401 - env is the proxy


@pytest.fixture(autouse=True)
def cleanup_env():
    backup = dict(env_registry)
    clear_env_cache()
    yield
    for k in list(env_registry.keys()):
        if k.startswith("TEST_") and k not in backup:
            del env_registry[k]
    for k in list(os.environ.keys()):
        if k.startswith("TEST_"):
            del os.environ[k]


def test_register_and_access_string():
    register_env_var({
        "name": "TEST_STRING",
        "description": "A test string variable",
        "type": "string",
        "default": "default_value",
    })
    os.environ["TEST_STRING"] = "test_value"
    assert env.TEST_STRING == "test_value"


def test_boolean_true_values():
    register_env_var({
        "name": "TEST_BOOL_TRUE",
        "description": "A test boolean variable",
        "type": "boolean",
    })
    for val in ("true", "1", "on", "yes"):
        os.environ["TEST_BOOL_TRUE"] = val
        clear_env_cache()
        assert env.TEST_BOOL_TRUE is True


def test_boolean_false_values():
    register_env_var({
        "name": "TEST_BOOL_FALSE",
        "description": "A test boolean variable",
        "type": "boolean",
    })
    from pytui.lib.env import env
    os.environ["TEST_BOOL_FALSE"] = "false"
    clear_env_cache()
    assert env.TEST_BOOL_FALSE is False


def test_number_env_var():
    register_env_var({
        "name": "TEST_NUMBER",
        "description": "A test number variable",
        "type": "number",
    })
    os.environ["TEST_NUMBER"] = "42"
    clear_env_cache()
    assert env.TEST_NUMBER == 42


def test_required_env_var_raises():
    register_env_var({
        "name": "TEST_REQUIRED",
        "description": "Required variable",
        "type": "string",
    })
    if "TEST_REQUIRED" in os.environ:
        del os.environ["TEST_REQUIRED"]
    clear_env_cache()
    with pytest.raises(ValueError, match="not set"):
        _ = env.TEST_REQUIRED


def test_same_config_twice_ok():
    register_env_var({"name": "TEST_SAME", "description": "Same", "type": "string", "default": "x"})
    register_env_var({"name": "TEST_SAME", "description": "Same", "type": "string", "default": "x"})


def test_different_config_raises():
    register_env_var({"name": "TEST_DIFF", "description": "A", "type": "string"})
    with pytest.raises(ValueError, match="different configuration"):
        register_env_var({"name": "TEST_DIFF", "description": "B", "type": "string"})


def test_generate_env_markdown():
    register_env_var({"name": "TEST_MD", "description": "For markdown", "default": "v"})
    md = generate_env_markdown()
    assert "# Environment Variables" in md
    assert "TEST_MD" in md
    assert "For markdown" in md


def test_generate_env_colored():
    register_env_var({"name": "TEST_COL", "description": "For colored", "default": "v"})
    out = generate_env_colored()
    assert "Environment Variables" in out
    assert "TEST_COL" in out
