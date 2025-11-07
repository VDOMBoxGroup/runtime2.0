


import ctypes

from time import time
from threading import current_thread, RLock
from weakref import WeakKeyDictionary

import settings

from logs import log
from utils.tracing import describe_thread
from .daemon import ScriptCleaner


class ScriptTimeoutError(Exception):
    pass


class ScriptManager(object):

    def __init__(self):
        self._lock = RLock()
        self._threads = WeakKeyDictionary()
        self._cleaner = None

    def work(self):
        now = time()
        with self._lock:
            for thread, (overall, counter, deadline) in list(self._threads.items()):
                if counter and now > deadline:
                    log.warning("Terminate %s due to timeout" % describe_thread(thread))
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(ScriptTimeoutError))
                    self._threads.pop(thread, None)

    def start_cleaner(self):
        with self._lock:
            if self._cleaner is None:
                self._cleaner = ScriptCleaner(self)
                self._cleaner.start()
            return self._cleaner

    def ignore(self):
        ctypes.pythonapi.PyThreadState_SetAsyncExc(current_thread().ident, None)

    def constrain(self, overall):
        thread = current_thread()
        with self._lock:
            values = self._threads.get(thread)
            if values is None:
                self._threads[thread] = overall, 0, None

    def revoke(self):
        thread = current_thread()
        with self._lock:
            try:
                overall, counter, deadline = self._threads[thread]
            except KeyError:
                pass
            else:
                if counter:
                    self._threads[thread] = None, counter, deadline
                else:
                    del self._threads[thread]

    def watch(self, timeout=settings.SCRIPT_TIMEOUT):
        thread = current_thread()
        with self._lock:
            overall, counter, deadline = self._threads.get(thread, (None, 0, None))
            if deadline is None:
                self._threads[thread] = overall, counter + 1, time() + (overall or timeout)
            else:
                self._threads[thread] = overall, counter + 1, deadline

            if self._cleaner is None:
                self.start_cleaner()

    def leave(self):
        thread = current_thread()
        with self._lock:
            try:
                overall, counter, deadline = self._threads[thread]
            except KeyError:
                pass
            else:
                if counter == 1 and overall is None:
                    del self._threads[thread]
                else:
                    self._threads[thread] = overall, counter - 1, deadline

    def prolong(self, value):
        thread = current_thread()
        with self._lock:
            try:
                overall, counter, deadline = self._threads[thread]
            except KeyError:
                pass
            else:
                self._threads[thread] = overall, counter, deadline + value
