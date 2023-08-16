#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.2.8 "
__status__ = "Production"
__date__ = "2023.08.16"
__license__ = "MIT"

from queue import Queue
from threading import Lock


class History:
    def __init__(self):
        self._queue = Queue()
        self._lock = Lock()

    def add(self, item):
        with self._lock:
            self._queue.put(item)

    def get(self):
        with self._lock:
            history = list(self._queue.queue)
        return history

    def clear(self):
        with self._lock:
            self._queue.queue.clear()
