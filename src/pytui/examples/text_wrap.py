# text_wrap.py - Aligns OpenTUI packages/core/src/examples/text-wrap.ts (simplified)
# Text wrapping: ScrollBox + Text with long content; scroll with j/k or Up/Down; L load file.

from __future__ import annotations

from typing import Any

from pytui.components.text_node import Span, bold

_parent_container: Any = None
_scrollbox: Any = None
_text_content: Any = None
_instructions_text: Any = None
_file_input_container: Any = None
_file_path_input: Any = None
_file_input_visible: bool = False

_DEMO_CONTENT = """OpenTUI Text Wrapping Demo

Welcome to the text wrapping demonstration. This example showcases how PyTUI handles multi-line text inside a scrollable box.

Key Features:
  Word-based wrapping - Preserves word boundaries when breaking lines.
  Character-based wrapping - Breaks at any character for precise control.
  Dynamic resizing - Text reflows as container dimensions change.
  Rich styling - Individual segments can have different colors and attributes.

How It Works:
Text is created with specific styling and composed together to form rich, formatted content. When the container is resized, the text automatically reflows to fit the new dimensions.

Try It Out:
  j / Down - Scroll down
  k / Up   - Scroll up
  L        - Load file (enter path when prompted)
  Ctrl+C   - Exit
"""


def _show_file_input() -> None:
    global _file_input_visible
    if _file_input_container is not None and _file_path_input is not None:
        _file_input_container.visible = True
        _file_path_input.value = ""
        _file_path_input.focus()
        _file_input_visible = True


def _hide_file_input() -> None:
    global _file_input_visible
    if _file_input_container is not None and _file_path_input is not None:
        _file_input_container.visible = False
        if getattr(_file_path_input, "blur", None):
            _file_path_input.blur()
        _file_input_visible = False


def _on_key(key_event: Any) -> None:
    global _file_input_visible
    name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
    if not name:
        return
    name = str(name).lower()
    if _file_input_visible:
        return
    if not _scrollbox:
        return
    if name in ("l",):
        _show_file_input()
        return
    if name in ("j", "down"):
        _scrollbox.scroll_top = min(_scrollbox.scroll_top + 1, max(0, _scrollbox.scroll_height - _scrollbox.height))
    elif name in ("k", "up"):
        _scrollbox.scroll_top = max(0, _scrollbox.scroll_top - 1)


def run(renderer: Any) -> None:
    global _parent_container, _scrollbox, _text_content, _instructions_text
    global _file_input_container, _file_path_input

    from pytui.components.box import Box
    from pytui.components.text import Text
    from pytui.components.scrollbox import Scrollbox
    from pytui.components.input import Input, ENTER_EVENT

    renderer.set_background_color("#0a0a14")

    _parent_container = Box(
        renderer.context,
        {
            "id": "main_container",
            "flex_direction": "column",
            "width": "100%",
            "height": "auto",
            "flex_grow": 1,
            "backgroundColor": "#0f0f23",
        },
    )
    renderer.root.add(_parent_container)

    # File path input (hidden until L pressed). Align OpenTUI filePathInput + showFileInput.
    _file_input_container = Box(
        renderer.context,
        {
            "id": "file_input_container",
            "width": "100%",
            "height": 3,
            "backgroundColor": "#1e1e2e",
            "visible": False,
        },
    )
    _parent_container.add(_file_input_container)
    def _file_input_on_key_down(key_event: Any) -> None:
        name = getattr(key_event, "name", None) or (key_event.get("name") if isinstance(key_event, dict) else None)
        n = (name or "").lower()
        if n in ("escape", "esc"):
            _hide_file_input()
        elif n == "backspace" and _file_path_input and not (_file_path_input.value or "").strip():
            _hide_file_input()

    _file_path_input = Input(
        renderer.context,
        {
            "id": "file-path-input",
            "width": 68,
            "height": 1,
            "value": "",
            "placeholder": "Enter file path (relative or absolute)...",
            "maxLength": 500,
            "on_key_down": _file_input_on_key_down,
        },
    )
    _file_input_container.add(_file_path_input)

    def _on_file_enter(path_value: str) -> None:
        _hide_file_input()
        path = (path_value or "").strip()
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if _text_content is not None:
                _text_content.set_content(f"// Loaded: {path}\n\n{content}")
            if _instructions_text is not None:
                _instructions_text.set_content(
                    [
                        bold("Text Wrap Demo", "#7aa2f7"),
                        Span(text=" - ", fg="#565f89"),
                        Span(text="Loaded: ", fg="#9ece6a"),
                        Span(text=path, fg="#c0caf5"),
                    ]
                )
        except Exception as e:
            if _text_content is not None:
                _text_content.set_content(f"ERROR: {e}\n\nPress L to try again.")
            if _instructions_text is not None:
                _instructions_text.set_content(
                    [
                        bold("Text Wrap Demo", "#7aa2f7"),
                        Span(text=" - ", fg="#f7768e"),
                        Span(text="Error loading file", fg="#c0caf5"),
                    ]
                )

    _file_path_input.on(ENTER_EVENT, _on_file_enter)

    content_box = Box(
        renderer.context,
        {
            "id": "content_box",
            "flex_grow": 1,
            "backgroundColor": "#1e1e2e",
            "border": True,
            "padding": 1,
        },
    )
    _parent_container.add(content_box)

    _scrollbox = Scrollbox(
        renderer.context,
        {
            "id": "text_box",
            "width": 70,
            "height": 18,
            "backgroundColor": "#11111b",
        },
    )
    content_box.add(_scrollbox)

    _text_content = Text(
        renderer.context,
        {
            "id": "text_content",
            "content": _DEMO_CONTENT,
            "width": 68,
            "height": 40,
            "fg": "#c0caf5",
        },
    )
    _scrollbox.add(_text_content)

    _instructions_text = Text(
        renderer.context,
        {
            "id": "instructions",
            "content": [
                bold("Text Wrap Demo", "#7aa2f7"),
                Span(text=" - ", fg="#565f89"),
                Span(text="j/k", fg="#9ece6a"),
                Span(text=" or ", fg="#c0caf5"),
                Span(text="Up/Down", fg="#9ece6a"),
                Span(text=" scroll  ", fg="#c0caf5"),
                Span(text="L", fg="#e0af68"),
                Span(text=" load file  ", fg="#c0caf5"),
                Span(text="Ctrl+C", fg="#f7768e"),
                Span(text=" exit", fg="#c0caf5"),
            ],
            "width": 72,
            "height": 2,
            "fg": "#c0caf5",
        },
    )
    _parent_container.add(_instructions_text)

    renderer.events.on("keypress", _on_key)


def destroy(renderer: Any) -> None:
    global _parent_container, _scrollbox, _text_content, _instructions_text
    global _file_input_container, _file_path_input, _file_input_visible
    _hide_file_input()
    try:
        renderer.events.remove_listener("keypress", _on_key)
    except Exception:
        pass
    if _parent_container and renderer.root:
        try:
            renderer.root.remove(_parent_container.id)
        except Exception:
            pass
    _parent_container = None
    _scrollbox = None
    _text_content = None
    _instructions_text = None
    _file_input_container = None
    _file_path_input = None
    _file_input_visible = False
