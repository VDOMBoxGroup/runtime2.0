
import logs
from .viewer import LogViewer


class BaseLog(object):

    def __init__(self, name=None):
        if name is not None:
            self.name = "/".join((self.name, name))

    def _format(self, *values):
        self._format = self.formatter().format
        return self._format(*values)

    def _enqueue(self, *values):
        self._enqueue = logs.logger.ascribe(self)
        return self._enqueue(*values)

    def view(self):
        return LogViewer(self)

    def accomplish(self, *values, **options):
        raise NotImplementedError

    def describe(self, *values):
        raise NotImplementedError

    def write(self, *arguments, **options):
        self._enqueue(*self.accomplish(*arguments, **options))

    def flush(self):
        pass
