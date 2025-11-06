
from builtins import zip
from builtins import next
from builtins import object
import sys
import os
import os.path
from collections import deque
from itertools import tee, chain, islice
import settings


EXTENSIONS = ("%s.log", "%s.bak")
FETCH_SIZE = 4 * 1024


class LogFile(object):

    def __init__(self, name, order, formatter):
        self._name = name
        self._order = order
        self._formatter = formatter
        self._file = None
        self._size = None
        self._data = None
        self._tell = None
        self._index = deque()
        self._exists = None

    def _get_filename(self):
        try:
            return os.path.join(settings.LOGS_LOCATION, EXTENSIONS[self._order] % self._name)
        except IndexError:
            raise Exception("Incorrect log file order")

    name = property(lambda self: self._name)
    filename = property(_get_filename)
    order = property(lambda self: self._order)
    size = property(lambda self: self._size)
    count = property(lambda self: len(self._index))

    def _open(self):
        self._file = open(self.filename, "a+b")
        self._file.seek(0, os.SEEK_END)
        self._size = self._file.tell()
        self._data = ""
        self._tell = self._size

    def read(self, start=0, count=sys.maxsize, into=None):
        if self._file is None:
            if self._exists is None:
                self._exists = os.path.exists(self.filename)
            if self._exists:
                self._open()
            else:
                return []

        result = [] if into is None else into

        if start < len(self._index):
            lefts, rights = tee(chain((self._size,), self._index))
            next(rights, None)
            for left, right in islice(zip(lefts, rights), start, start + count):
                self._file.seek(right)
                entry = self._formatter.parse(self._file.read(left - right).decode("utf8"))
                result.append(entry)
                count -= 1

        while count > 0 and self._tell:
            size = min(self._tell, FETCH_SIZE)
            self._tell -= size

            self._file.seek(self._tell)
            data = self._file.read(size) + self._data

            iterator = self._formatter.finditer(data)

            if self._tell:
                try:
                    tell = next(iterator)
                except StopIteration:
                    self._data = data
                    continue
                else:
                    self._data = data[:tell]
            else:
                self._data = None
                tell = 0

            index, entries = deque(), deque()
            while 1:
                try:
                    position = next(iterator)
                except StopIteration:
                    break
                else:
                    entry = self._formatter.parse(data[tell:position].decode("utf8"))
                    index.appendleft(self._tell + tell)
                    entries.appendleft(entry)
                    count -= 1
                    tell = position

            self._index.extend(index)
            result.extend(islice(entries, len(entries) + count) if count < 0 else entries)

        return result

    def write(self, *entries):
        if self._file is None:
            self._open()

        assert self._order == 0

        tell = self._size
        self._file.seek(tell)

        for entry in entries:
            data = self._formatter.format(*entry).encode("utf8")
            self._file.write(data)
            self._index.appendleft(tell)
            tell += len(data)

        self._file.flush()
        self._size = tell

    def shift(self):
        last_filename = self.filename
        if self._file is None:
            state = None
        else:
            if self._order:
                os.fsync(self._file.fileno())
            state = os.stat(last_filename)
            self._file.close()
            self._file = None
        self._order += 1
        next_filename = self.filename
        if os.path.exists(next_filename):
            os.remove(next_filename)
        if state or os.path.exists(last_filename):
            os.rename(last_filename, next_filename)
        if state is not None:
            self._file = open(next_filename, "r+b")
            if state != os.stat(next_filename):
                self._file.close()
                self._file = None
        if self._file is None:
            self._size = None
            self._data = None
            self._tell = None
            self._index = deque()

    def drop(self):
        if self._file:
            self._file.close()
