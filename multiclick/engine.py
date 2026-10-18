"""Thread-safe click scheduling, independent of the desktop platform."""

from collections import deque
from threading import Condition, Thread


class ClickEngine:
    def __init__(self, send_click):
        self._send_click = send_click
        self._condition = Condition()
        self._queue = deque()
        self._enabled = False
        self._closed = False
        self._generation = 0
        self._multiplier = 5
        self._interval = 0.04
        self.physical_clicks = 0
        self.extra_clicks = 0
        self.error = None
        self._worker = Thread(target=self._run, daemon=True, name="click-worker")
        self._worker.start()

    def configure(self, multiplier, interval_ms):
        if not isinstance(multiplier, int) or not 2 <= multiplier <= 100:
            raise ValueError("Choose between 2 and 100 clicks.")
        if not isinstance(interval_ms, int) or not 10 <= interval_ms <= 1000:
            raise ValueError("Choose an interval between 10 and 1000 ms.")
        with self._condition:
            self._multiplier = multiplier
            self._interval = interval_ms / 1000

    def set_enabled(self, enabled):
        with self._condition:
            self._enabled = bool(enabled) and not self._closed
            self._generation += 1
            self._queue.clear()
            self._condition.notify_all()
            return self._enabled

    def snapshot(self):
        with self._condition:
            return self._enabled, self.physical_clicks, self.extra_clicks, self.error

    def physical_click(self):
        """Call once on a physical left-button release, never for injected input."""
        with self._condition:
            if not self._enabled or self._closed:
                return
            # The original click already reached the application.
            self.physical_clicks += 1
            if len(self._queue) < 100:
                self._queue.append((self._multiplier - 1, self._interval))
                self._condition.notify_all()

    def _run(self):
        with self._condition:
            while not self._closed:
                self._condition.wait_for(lambda: self._closed or self._queue)
                if self._closed:
                    break
                count, interval = self._queue.popleft()
                generation = self._generation
                for _ in range(count):
                    cancelled = self._condition.wait_for(
                        lambda: self._closed or generation != self._generation,
                        timeout=interval,
                    )
                    if cancelled:
                        break
                    try:
                        self._send_click()
                        self.extra_clicks += 1
                    except Exception as exc:
                        self.error = str(exc)
                        self._enabled = False
                        self._queue.clear()
                        self._generation += 1
                        break

    def close(self):
        with self._condition:
            self._closed = True
            self._enabled = False
            self._generation += 1
            self._queue.clear()
            self._condition.notify_all()
        self._worker.join(timeout=2)
