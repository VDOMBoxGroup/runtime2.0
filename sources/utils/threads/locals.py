
import threading
from contextlib import contextmanager


MISSING = "MISSING"


local = threading.local()


@contextmanager
def localcontext(**keywords):
    backup = {}

    for name, value in keywords.items():
        previous_value = getattr(local, name, MISSING)
        backup[name] = previous_value
        setattr(local, name, value)

    yield

    for name, value in backup.items():
        if value is MISSING:
            delattr(local, name)
        else:
            setattr(local, name, value)


def getlocal(name, default=None):
    return getattr(local, name, default)


def setlocal(name, value):
    setattr(local, name, value)


def dellocal(name):
    delattr(local, name)
