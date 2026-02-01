# pytui.lib.queue - Aligns with OpenTUI lib/queue.ts
# Generic processing queue that handles asynchronous job processing (FIFO).

import logging
import threading
from typing import Callable, TypeVar

T = TypeVar("T")

_log = logging.getLogger(__name__)


class ProcessQueue:
    """FIFO queue that processes items with a processor. Aligns with OpenTUI ProcessQueue."""

    def __init__(self, processor: Callable[[T], None], auto_process: bool = True) -> None:
        self._queue: list[T] = []
        self._processing = False
        self._auto_process = auto_process
        self._processor = processor
        self._lock = threading.Lock()

    def enqueue(self, item: T) -> None:
        """Append item and start processing if not already running and auto_process is True."""
        with self._lock:
            self._queue.append(item)
            if not self._processing and self._auto_process:
                self._processing = True
                threading.Thread(target=self._drain, daemon=True).start()

    def _drain(self) -> None:
        while True:
            with self._lock:
                if not self._queue:
                    self._processing = False
                    return
                item = self._queue.pop(0)
            try:
                self._processor(item)
            except Exception as e:
                _log.exception("Error processing queue item: %s", e)
            with self._lock:
                if not self._queue:
                    self._processing = False
                    return

    def clear(self) -> None:
        """Remove all items from the queue."""
        with self._lock:
            self._queue.clear()

    def is_processing(self) -> bool:
        """Returns True if a drain is currently running."""
        return self._processing

    def size(self) -> int:
        """Returns the number of items in the queue."""
        return len(self._queue)
