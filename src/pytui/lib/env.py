# pytui.lib.env - Aligns with OpenTUI lib/env.ts
# Environment variable registry: register_env_var, env proxy, clear_env_cache, generate_env_markdown/colored.

import os
from typing import Any, Literal

from pytui.lib.singleton import singleton

EnvVarType = Literal["string", "boolean", "number"]


class EnvVarConfig(dict):
    """Config for one env var. Aligns with OpenTUI EnvVarConfig. Use as dict or with .name, .description, etc."""

    def __init__(
        self,
        name: str,
        description: str,
        default: str | bool | int | None = None,
        type: EnvVarType | None = None,
    ) -> None:
        super().__init__(name=name, description=description, default=default, type=type or "string")
        self.name = name
        self.description = description
        self.default = default
        self.type = type or "string"


env_registry: dict[str, dict] = singleton("env-registry", lambda: {})


def register_env_var(config: EnvVarConfig | dict) -> None:
    """Register an env var. Same config twice is ok; different config for same name throws. Aligns with OpenTUI registerEnvVar()."""
    if isinstance(config, dict):
        name = config["name"]
        description = config["description"]
        default = config.get("default")
        type_ = config.get("type", "string")
    else:
        name = config.name
        description = config.description
        default = config.default
        type_ = config.type or "string"
    existing = env_registry.get(name)
    if existing:
        if (
            existing.get("description") != description
            or existing.get("type") != type_
            or existing.get("default") != default
        ):
            raise ValueError(
                f'Environment variable "{name}" is already registered with different configuration. '
                f"Existing: {existing}, New: {dict(name=name, description=description, type=type_, default=default)}"
            )
        return
    env_registry[name] = {"name": name, "description": description, "default": default, "type": type_}


def _normalize_boolean(value: str) -> bool:
    return value.lower() in ("true", "1", "on", "yes")


def _parse_env_value(config: dict) -> str | bool | int:
    name = config["name"]
    type_ = config.get("type", "string")
    default = config.get("default")
    env_value = os.environ.get(name)
    if env_value is None and default is not None:
        return default
    if env_value is None:
        raise ValueError(f"Required environment variable {name} is not set. {config.get('description', '')}")
    if type_ == "boolean":
        return _normalize_boolean(env_value) if isinstance(env_value, str) else bool(env_value)
    if type_ == "number":
        try:
            num = float(env_value) if isinstance(env_value, str) else float(env_value)
            return int(num) if num == int(num) else num
        except (ValueError, TypeError):
            raise ValueError(f"Environment variable {name} must be a valid number, got: {env_value}")
    return env_value


class _EnvStore:
    def __init__(self) -> None:
        self._parsed: dict[str, str | bool | int] = {}

    def get(self, key: str) -> Any:
        if key in self._parsed:
            return self._parsed[key]
        if key not in env_registry:
            raise ValueError(f"Environment variable {key} is not registered.")
        try:
            value = _parse_env_value(env_registry[key])
            self._parsed[key] = value
            return value
        except Exception as e:
            raise ValueError(f"Failed to parse env var {key}: {e}") from e

    def has(self, key: str) -> bool:
        return key in env_registry

    def clear_cache(self) -> None:
        self._parsed.clear()


_env_store = singleton("env-store", _EnvStore)


def clear_env_cache() -> None:
    """Clear parsed env cache. Aligns with OpenTUI clearEnvCache()."""
    _env_store.clear_cache()


def generate_env_markdown() -> str:
    """Generate markdown listing all registered env vars. Aligns with OpenTUI generateEnvMarkdown()."""
    configs = list(env_registry.values())
    if not configs:
        return "# Environment Variables\n\nNo environment variables registered.\n"
    out = ["# Environment Variables\n"]
    for c in configs:
        out.append(f"## {c['name']}\n\n{c['description']}\n\n")
        out.append(f"**Type:** `{c.get('type', 'string')}`  \n")
        if c.get("default") is not None:
            d = c["default"]
            out.append(f"**Default:** `{d if isinstance(d, str) else d}`\n")
        else:
            out.append("**Default:** *Required*\n")
        out.append("\n")
    return "".join(out)


def generate_env_colored() -> str:
    """Generate ANSI-colored listing. Aligns with OpenTUI generateEnvColored()."""
    configs = list(env_registry.values())
    if not configs:
        return "\x1b[1;36mEnvironment Variables\x1b[0m\n\nNo environment variables registered.\n"
    out = ["\x1b[1;36mEnvironment Variables\x1b[0m\n\n"]
    for c in configs:
        out.append(f"\x1b[1;33m{c['name']}\x1b[0m\n{c['description']}\n")
        out.append(f"\x1b[32mType:\x1b[0m \x1b[36m{c.get('type', 'string')}\x1b[0m\n")
        if c.get("default") is not None:
            d = c["default"]
            out.append(f"\x1b[32mDefault:\x1b[0m \x1b[35m{d if isinstance(d, str) else d}\x1b[0m\n")
        else:
            out.append("\x1b[32mDefault:\x1b[0m \x1b[31mRequired\x1b[0m\n")
        out.append("\n")
    return "".join(out)


class _EnvProxy:
    """Proxy for env.EXAMPLE access. Aligns with OpenTUI env proxy."""

    def __getattr__(self, name: str) -> Any:
        return _env_store.get(name)

    def __hasattr__(self, name: str) -> bool:
        return _env_store.has(name)

    def __dir__(self) -> list[str]:
        return list(env_registry.keys())


env = _EnvProxy()
