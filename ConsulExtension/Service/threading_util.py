"""Utilities for threading implementation"""

import threading


class ThreadSafeDict(dict):
    """A thread safe dict

    Method for seeing that there is no race condition
    and using lock when accessing the thread_registry
    """

    def __init__(self, *p_arg, **n_arg):
        dict.__init__(self, *p_arg, **n_arg)
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self._lock.release()
