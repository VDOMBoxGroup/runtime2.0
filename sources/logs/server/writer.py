
import os
import os.path
from collections import deque
from weakref import WeakSet
from threading import Lock
import settings
from .file import EXTENSIONS, LogFile


ROLLOVER_SIZE = 100 * 1024 * 1024
# Entries kept while the file cannot be written, written with the next ones.
PENDING_LIMIT = 10000


class LogWriter(object):

    def __init__(self, name, formatter):
        self._name = name
        self._files = deque(LogFile(name, order, formatter) for order in range(len(EXTENSIONS)))
        self._formatter = formatter
        self._readers = WeakSet()
        self._lock = Lock()
        self._pending = deque(maxlen=PENDING_LIMIT)
        path = settings.LOGS_LOCATION
        for part in name.split("/")[:-1]:
            path = "%s/%s" % (path, part)
            if not os.path.isdir(path):
                os.mkdir(path)

    name = property(lambda self: self._name)

    def write(self, *entries):
        with self._lock:
            # A file another process holds a moment (a sync tool, an
            # antivirus) refuses the write with an OSError. It used to reach
            # the log session, whose "except socket.error" (an alias of
            # OSError) stopped it for good: server.log was no longer written
            # while the console went on. The entries wait for the next write.
            entries = tuple(self._pending) + entries
            try:
                self._files[0].write(*entries)
            except OSError:
                self._files[0].reset()
                self._pending = deque(entries, maxlen=PENDING_LIMIT)
                return
            self._pending.clear()
            count = len(entries)
            for reader in self._readers:
                reader._index += count
            if self._files[0].size > ROLLOVER_SIZE:
                self._files.pop().drop()
                for log_file in reversed(self._files):
                    log_file.shift()
                self._files.appendleft(LogFile(self._name, 0, self._formatter))
