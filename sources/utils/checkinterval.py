
import sys
from threading import RLock


class MaximalCheckInterval(object):

    def __init__(self):
        self._lock = RLock()
        self._value = None
        self._count = 0

    def __enter__(self):
        self._lock.acquire()
        if self._count == 0:
            self._value = sys.getcheckinterval()
            sys.setswitchinterval(sys.maxsize)
        self._count += 1

    def __exit__(self, extype, exvalue, extraceback):
        self._count -= 1
        if self._count == 0:
            sys.setswitchinterval(self._value)
            self._value = None
        self._lock.release()


maximal_check_interval = MaximalCheckInterval()
