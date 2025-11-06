
from builtins import str

import settings
import logs
from . import levels
from .auxiliary import discover_calling_module
from .baselog import BaseLog


LOGGING = None


class DebugLog(BaseLog):

    def write(self, message=None, warning=None, error=None, debug=None, module=None, level=None, **options):
        if level is None:
            level, message = (levels.MESSAGE, message) if message is not None \
                else (levels.WARNING, warning) if warning is not None \
                else (levels.ERROR, error) if error is not None \
                else (levels.DEBUG, debug) if debug is not None \
                else (levels.MESSAGE, "")

        if settings.LOGGER and (level >= settings.LOG_LEVEL or level >= settings.CONSOLE_LOG_LEVEL):
            if not isinstance(message, str):
                message = str(message)
            if module is None and settings.DISCOVER_LOGGING_MODULE:
                module = discover_calling_module()

            values = self.accomplish(module, level, message, **options)

            if level >= settings.LOG_LEVEL:
                self._enqueue(*values)
            if level >= settings.CONSOLE_LOG_LEVEL:
                logs.console.write(self._format(*values), level=level, format=False)
        elif level >= settings.LOG_LEVEL:
            logs.console.write(message, warning, error, debug, module, level)

    def flush(self):
        logs.console.flush()

    def debug(self, message, module=None, **options):
        self.write(message, module=module, level=levels.DEBUG, **options)

    def warning(self, message, module=None, **options):
        self.write(message, module=module, level=levels.WARNING, **options)

    def error(self, message, module=None, **options):
        self.write(message, module=module, level=levels.ERROR, **options)
