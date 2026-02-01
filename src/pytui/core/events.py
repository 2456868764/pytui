# pytui.core.events - event bus; aligns with OpenTUI event model (EventEmitter).

from __future__ import annotations

from pyee import EventEmitter

# EventBus: app-level events (resize, keypress, frame, etc.). OpenTUI uses EventEmitter;
# event names align: "resize", "keypress", "keyrelease", "paste", "frame", "mouse", etc.
EventBus = EventEmitter
