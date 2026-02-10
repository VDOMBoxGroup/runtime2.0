

import sys
import settings

from threading import Lock
from . import levels
from .formatters import PrefixingLogFormatter


LOGGING = None
NAME = "console"


class Console:

    stdout = sys.stdout
    stderr = sys.stderr

    def __init__(self):
        self._lock = Lock()
        self._formatter = PrefixingLogFormatter(NAME)

    def write(self, message=None, warning=None, error=None, debug=None, module=None, level=None, format=True): 
        if level is None:
            level, message = \
                (levels.MESSAGE, message) if message is not None else \
                (levels.WARNING, warning) if warning is not None else \
                (levels.ERROR, error) if error is not None else \
                (levels.DEBUG, debug) if debug is not None else \
                (levels.MESSAGE, "")

        if level >= settings.CONSOLE_LOG_LEVEL:
            # if isinstance(message, str):
            #     message = message.encode((self.stderr.encoding if level is levels.ERROR
            #         else self.stdout.encoding) or "ascii", "backslashreplace")
            if isinstance(message, bytes):
                message = message.encode((self.stderr.encoding if level is levels.ERROR
                     else self.stdout.encoding) or "ascii", "backslashreplace")
            elif not isinstance(message, str):
                try:
                    message = message.encode()
                except Exception:
                    message = str(message)

            if format:
                message = self._formatter.format(module, level, message)

            with self._lock:
                (self.stderr if level is levels.ERROR else self.stdout).write(message)

    def flush(self):
        self.stdout.flush()
        self.stderr.flush()

    def debug(self, message, module=None):
        self.write(message, module=module, level=levels.DEBUG)

    def warning(self, message, module=None):
        self.write(message, module=module, level=levels.WARNING)

    def error(self, message, module=None):
        self.write(message, module=module, level=levels.ERROR)
