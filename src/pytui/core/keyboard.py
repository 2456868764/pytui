# pytui.core.keyboard - KeyboardHandler with feed(); uses lib.key_handler.KeyHandler + lib.stdin_buffer.StdinBuffer
#
# Functionality:
#   - KeyboardHandler: composes StdinBuffer + KeyHandler; feed(data) → buffer → complete seq → process_input/process_paste → emit keypress/keyrelease/paste.
#   - Does not read stdin; caller (e.g. renderer) must call feed() with raw input.
#
# OpenTUI correspondence:
#   - This module (StdinBuffer + KeyHandler composition + feed()): renderer.ts keyboard wiring (stdin → StdinBuffer.process → KeyHandler.processInput/processPaste).
#   - Base KeyHandler, KeyEvent, PasteEvent, processInput, processPaste: opentui lib/KeyHandler.ts.
#   - Buffering: opentui lib/stdin-buffer.ts (pytui lib/stdin_buffer.py).
#   - Parsing: opentui lib/parse.keypress.ts + parse.keypress-kitty.ts (pytui lib/parse_keypress.py).
#   - InternalKeyHandler (priority emit, global vs renderable): KeyHandler.ts; in pytui may live in renderer or key_input wrapper.

from pyee import EventEmitter

from pytui.lib.key_handler import KeyHandler
from pytui.lib.stdin_buffer import StdinBuffer


class KeyboardHandler(KeyHandler):
    """Keyboard input with feed(); buffers via StdinBuffer and emits keypress/keyrelease/paste. Aligns OpenTUI KeyHandler + renderer keyboard wiring."""

    def __init__(self, use_kitty_keyboard: bool = False, input_handlers_getter=None) -> None:
        super().__init__(use_kitty_keyboard=use_kitty_keyboard)
        self._stdin = StdinBuffer()
        self._stdin.on("data", self._on_data)
        self._stdin.on("paste", self._on_paste)
        self._input_handlers_getter = input_handlers_getter

    def _on_data(self, seq: str) -> None:
        if self._input_handlers_getter:
            for h in self._input_handlers_getter():
                if h(seq):
                    return
        self.process_input(seq)

    def _on_paste(self, text: str) -> None:
        self.process_paste(text)

    def feed(self, data: str | bytes) -> None:
        """Feed raw input; buffer and emit keypress/keyrelease/paste for complete sequences."""
        self._stdin.process(data)
