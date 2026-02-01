# pytui.lib.tree_sitter.resolve_ft - Aligns with OpenTUI lib/tree-sitter/resolve-ft.ts

from __future__ import annotations

_EXTENSION_TO_FILETYPE: dict[str, str] = {
    "js": "javascript",
    "jsx": "javascriptreact",
    "ts": "typescript",
    "tsx": "typescriptreact",
    "md": "markdown",
    "json": "json",
    "py": "python",
    "rb": "ruby",
    "go": "go",
    "rs": "rust",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "cs": "csharp",
    "java": "java",
    "kt": "kotlin",
    "swift": "swift",
    "php": "php",
    "sql": "sql",
    "pl": "perl",
    "lua": "lua",
    "erl": "erlang",
    "exs": "elixir",
    "ex": "elixir",
    "elm": "elm",
    "fsharp": "fsharp",
    "fs": "fsharp",
    "fsx": "fsharp",
    "fsscript": "fsharp",
    "fsi": "fsharp",
    "h": "c",
    "hpp": "cpp",
    "html": "html",
    "css": "css",
    "scss": "scss",
    "less": "less",
    "sh": "shell",
    "bash": "shell",
    "zsh": "shell",
    "vim": "vim",
    "yaml": "yaml",
    "yml": "yaml",
    "toml": "toml",
    "xml": "xml",
    "zig": "zig",
}


def ext_to_filetype(extension: str) -> str | None:
    """Align with OpenTUI extToFiletype(extension)."""
    return _EXTENSION_TO_FILETYPE.get(extension)


def path_to_filetype(path: str) -> str | None:
    """Align with OpenTUI pathToFiletype(path)."""
    if not isinstance(path, str):
        return None
    last_dot = path.rfind(".")
    if last_dot == -1 or last_dot == len(path) - 1:
        return None
    extension = path[last_dot + 1 :]
    return ext_to_filetype(extension)
