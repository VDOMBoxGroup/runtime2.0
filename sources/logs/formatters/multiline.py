
from builtins import zip
from builtins import range
import os
import re

from .formatter import LogFormatter


class MultilineLogFormatter(LogFormatter):

    def __init__(self, name, widths=None):
        super(MultilineLogFormatter, self).__init__(name)
        self._widths = widths or ()
        self._positions = tuple(sum(self._widths[:index]) for index in range(len(self._widths) + 1))

    def _make_caption(self, *values):
        return "".join(value[:width - 5] + "...  " if len(value) + 2 > width else value.ljust(width)
            for value, width in zip(values[:-1], self._widths))

    FORMAT_REGEX = re.compile("([^\r\n]*?)[ \t]*(?:(?:\n|\r\n|\r)?($)|(?:\n|\r\n|\r))")

    def format(self, *values):
        return self.FORMAT_REGEX.sub(lambda match:
            "" if match.group(1) == '' else "%s%s%s" % (
                self._make_caption(*values), match.group(1), os.linesep), values[-1])

    FIND_REGEX = re.compile("(?: \n| \r\n| \r|.)*(?:\n|\r\n|\r)")

    def finditer(self, data):
        for match in self.FIND_REGEX.finditer(data):
            yield match.end(0)

    PARSE_REGEX = re.compile("([^\r\n]*?) ?(?:\n|\r\n|\r)")

    def parse(self, data):
        return tuple(data[self._positions[index]:self._positions[index + 1]].rstrip()
                for index in range(len(self._widths))) + \
            (self.PARSE_REGEX.sub(lambda match: match.group(1)[self._positions[2]:] + "\n", data),)
