"""Elapsed timer. Author: Han Zheng, 2026-10-11.
Purpose: start on first valid reveal, freeze at game end, reset for a new game.
Input: optional monotonic clock callable. Output: elapsed seconds.
External source: OpenAI Codex implementation and test assistance.
"""
from time import monotonic


class GameTimer:
    def __init__(self, clock=monotonic):
        self._clock = clock
        self.reset()

    def reset(self):
        self._started = None
        self._stopped = None

    def start(self):
        if self._started is None:
            self._started = self._clock()

    def stop(self):
        if self._started is not None and self._stopped is None:
            self._stopped = self._clock()

    @property
    def elapsed(self):
        if self._started is None:
            return 0.0
        end = self._clock() if self._stopped is None else self._stopped
        return max(0.0, end - self._started)
