
from builtins import object
from operator import itemgetter
from threading import RLock
import settings
import managers
from logs import server_log
from utils.auxiliary import align


NAME_WIDTH = 36


class Counters(object):

    def __init__(self):
        self._lock = RLock()
        self._items = {}

    def increase(self, name):
        with self._lock:
            try:
                self._items[name] += 1
            except KeyError:
                self._items[name] = 1

    def show(self, label=None, indent=""):
        with self._lock:
            lines = []

            if self._items and label:
                lines.append("%s%s statistics:" % (indent, label))
                indent += "    "

            items = list(self._items.items())
            items.sort(key=itemgetter(0))

            for name, value in items:
                lines.append("%s%s%d" % (indent, align(name, NAME_WIDTH, filler="."), value))

            server_log.write("\n".join(lines))


class Statistics(object):

    def __init__(self):
        self._counters = Counters()

    def _get_counters(self):
        try:
            request = managers.request_manager.current
        except:
            return self._counters
        else:
            try:
                counters = request.counters
            except AttributeError:
                request.counters = counters = Counters()
            return counters

    counters = property(_get_counters)

    def increase(self, name):
        if settings.PROFILING:
            self.counters.increase(name)

    def show(self, label=None, indent=""):
        if settings.PROFILING:
            self.counters.show(label, indent)


statistics = Statistics()
