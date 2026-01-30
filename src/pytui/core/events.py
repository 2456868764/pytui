# pytui.core.events - event bus

from pyee import EventEmitter

# EventBus is an EventEmitter for app-level events (resize, keypress, etc.)
EventBus = EventEmitter
