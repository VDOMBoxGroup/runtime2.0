
from builtins import str
import gc
import re
import managers
from utils import verificators, profiling
from utils.decorators import verificator
from ..exceptions import NoSnapshotError


MISSING = "MISSING"
OBJECTS_SELECTOR_REGEX = re.compile(
    r"^(?:[A-Z_][A-Z\d_]*|[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})(?:\.[A-Z_][A-Z\d_]*)*$",
    re.IGNORECASE)
SERVER_OPTION = "server"


@verificator
def objects_selector(value):
    match = OBJECTS_SELECTOR_REGEX.match(value)
    if match:
        return int(value) if match.lastindex else str(value)
    else:
        raise ValueError("Not an identifier")


@verificator
def objects_source(value):
    if value == "objects":
        return lambda: gc.get_objects()
    elif value == "garbage":
        return lambda: gc.garbage
    elif value == "changes":

        def get_objects():
            value = managers.server.watcher.snapshot.recent
            if value is None:
                raise NoSnapshotError
            return value

        return get_objects
    else:
        return ValueError("Not a source")


@verificator
def objects_filter(value):
    if value == "pass":
        return None
    else:
        try:
            # NOTE: vulnerable place
            name, value = value.split("=")
            name = verificators.name(name)
            value = eval(value)
        except Exception:
            raise ValueError("Not a filter")
        else:

            def filter(object):
                try:
                    return getattr(object, name, MISSING) == value
                except Exception:
                    return False

            return filter


@verificator
def profiler_name(value):
    if value == "default":
        return profiling.profiler
    else:
        return verificators.name(value)


@verificator
def server_filter(value):
    if value == SERVER_OPTION:
        return True
    elif value == "":
        return False
    else:
        raise ValueError("Not a server filter")


@verificator
def objects_grouping(value):
    if value == "name":
        return True
    elif value == "":
        return False
    else:
        raise ValueError("Not a group")
