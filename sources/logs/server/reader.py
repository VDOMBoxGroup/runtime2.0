
import sys


class LogReader(object):

    def __init__(self, writer):
        self._writer = writer
        self._index = 0
        with self._writer._lock:
            writer._readers.add(self)

    def update(self):
        with self._writer._lock:
            result = self._index
            self._index = 0
        return result

    def read(self, start=0, count=sys.maxsize, into=None):
        start += self._index
        entries = [] if into is None else into
        with self._writer._lock:
            for log_file in self._writer._files:
                log_file.read(start, count - len(entries), into=entries)
                if len(entries) == count:
                    break
                start = max(0, start - log_file.count)
        return entries
