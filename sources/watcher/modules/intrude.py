


import ctypes
import re
from utils.threads import SmartThread
from ..exceptions import OptionError, WatcherError, WatcherManualException
from ..auxiliary import search_thread


pattern = re.compile("[A-Za-z][0-9A-Za-z]*$")


def intrude(options):
    if "raise" in options:
        value = options.get("raise")
        if value:
            if not pattern.match(value):
                raise OptionError("Incorrect name")
            exception = eval(value)
            if not issubclass(exception, Exception):
                raise OptionError("Not an exception")
        else:
            exception = WatcherManualException

        name_or_identifier = options["thread"]
        thread = search_thread(name_or_identifier)
        if thread is None:
            raise OptionError("Unable to find thread: %s" % name_or_identifier)

        result = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(exception))
        if result < 1:
            raise WatcherError("Thread not found")
        elif result > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
            raise WatcherError("Too many threads")

        yield "<reply/>"
    elif "stop" in options:
        thread = search_thread(options["thread"])
        if thread is None:
            raise OptionError("Unable to find thread")

        if not isinstance(thread, SmartThread):
            raise OptionError("Thread is not smart")

        thread.stop()
        yield "<reply/>"
