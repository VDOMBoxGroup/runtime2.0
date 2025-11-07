
import os
import os.path
from collections import deque
from weakref import WeakSet
from threading import Lock
import settings
from .file import EXTENSIONS, LogFile


ROLLOVER_SIZE = 100 * 1024 * 1024


class LogWriter(object):

    def __init__(self, name, formatter):
        self._name = name
        self._files = deque(LogFile(name, order, formatter) for order in range(len(EXTENSIONS)))
        self._formatter = formatter
        self._readers = WeakSet()
        self._lock = Lock()
        path = settings.LOGS_LOCATION
        for part in name.split("/")[:-1]:
            path = "%s/%s" % (path, part)
            if not os.path.isdir(path):
                os.mkdir(path)

    name = property(lambda self: self._name)

    def write(self, *entries):
        with self._lock:
            self._files[0].write(*entries)
            count = len(entries)
            for reader in self._readers:
                reader._index += count
            if self._files[0].size > ROLLOVER_SIZE:
                self._files.pop().drop()
                for log_file in reversed(self._files):
                    log_file.shift()
                self._files.appendleft(LogFile(self._name, 0, self._formatter))
