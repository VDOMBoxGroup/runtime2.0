
from builtins import str
import re
from logs.levels import NAME_TO_LEVEL as LOG_LEVEL_MAPPING
from .decorators import verificator


UUID_REGEX = re.compile(
    r"^[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}$",
    re.IGNORECASE)
NAME_REGEX = re.compile(
    r"^[A-Z][A-Z\d_]*$",
    re.IGNORECASE)
QUALIFIED_NAME_REGEX = re.compile(
    r"^[A-Z][A-Z\d_]*(?:\.[A-Z][A-Z\d_]*)*$",
    re.IGNORECASE)
NAME_OR_INTEGER_REGEX = re.compile(
    r"^(?:[A-Z][A-Z\d_]*|(-[1-9]\d*))$",
    re.IGNORECASE)
QUALIFIED_NAME_OR_INTEGER_REGEX = re.compile(
    r"^(?:[A-Z][A-Z\d_]*(?:\.[A-Z][A-Z\d_]*)*|(-[1-9]\d*))$",
    re.IGNORECASE)
UUID_OR_NAME_REGEX = re.compile(
    r"^(?:[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})|([A-Z][A-Z\d_]*)$",
    re.IGNORECASE)
UUID_OR_NONE_REGEX = re.compile(
    r"^(?:[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})|(none)$",
    re.IGNORECASE)
SIZE_REGEX = re.compile(
    r"^(?P<size>[0-9]+)(?P<measure>[KMG])?$",
    re.IGNORECASE)
LLP = "^%s$" % "|".join(LOG_LEVEL_MAPPING)
LOG_LEVEL_REGEX = re.compile(
    "^%s$" % "|".join(LOG_LEVEL_MAPPING),
    re.IGNORECASE)
EXCEPTION_REGEX = NAME_REGEX
THREAD_REGEX = re.compile(
    r"^(?:[A-Z][A-Z\d_-]*(?:\s[A-Z][A-Z\d_-]*)*|(-[1-9]\d*))$",
    re.IGNORECASE)

FLOAT = float


def complies(value, verificator):
    try:
        verificator(value)
        return True
    except ValueError:
        return False


@verificator
def none(value):
    return value


@verificator
def integer(value):
    try:
        return int(value)
    except ValueError:
        raise ValueError("Not an integer")


@verificator
def float(value):
    try:
        return FLOAT(value)
    except ValueError:
        raise ValueError("Not an float")


@verificator
def boolean(value):
    try:
        return {"0": False, "1": True, "no": False, "yes": True, "false": False, "true": True}[value.lower()]
    except KeyError:
        raise ValueError("Not a boolean")


@verificator
def port(value):
    try:
        value = int(value)
    except ValueError:
        raise ValueError("Port must be a number")
    else:
        if 0 <= value <= 65535:
            return value
        else:
            raise ValueError("Port must be greater then zero")


@verificator
def uuid(value):
    if UUID_REGEX.match(value):
        return str(value.lower())
    else:
        raise ValueError("Not an unique identifier")


@verificator
def name(value):
    if NAME_REGEX.match(value):
        return str(value)
    else:
        raise ValueError("Not a name")


@verificator
def qualified_name(value):
    if QUALIFIED_NAME_REGEX.match(value):
        return str(value)
    else:
        raise ValueError("Not a name")


@verificator
def name_or_integer(value):
    match = NAME_OR_INTEGER_REGEX.match(value)
    if match:
        return int(value) if match.lastindex else str(value.lower())
    else:
        raise ValueError("Not a name or integer")


@verificator
def qualified_name_or_integer(value):
    match = QUALIFIED_NAME_OR_INTEGER_REGEX.match(value)
    if match:
        return int(value) if match.lastindex else str(value.lower())
    else:
        raise ValueError("Not a name or integer")


@verificator
def uuid_or_name(value):
    match = UUID_OR_NAME_REGEX.match(value)
    if match:
        return str(value) if match.lastindex else str(value.lower())
    else:
        raise ValueError("Not an unique identifier or name")


@verificator
def uuid_or_none(value):
    match = UUID_OR_NONE_REGEX.match(value)
    if match:
        return str(value) if match.lastindex else str(value.lower())
    else:
        raise ValueError("Not an unique identifier or none")


@verificator
def size(value):
    match = SIZE_REGEX.match(value)
    if match:
        size, measure = match.group("size"), match.group("measure")
        if measure == "K":
            return size * 1024
        elif measure == "M":
            return size * 1024 * 1024
        elif measure == "G":
            return size * 1024 * 1024 * 1024
        else:
            return size
    else:
        raise ValueError("Not a size")


@verificator
def enable_or_disable(value):
    try:
        return {"enable": True, "disable": False}[value.lower()]
    except KeyError:
        raise ValueError("Not an enable or disable")


@verificator
def log_level(value):
    match = LOG_LEVEL_REGEX.match(value)
    if match:
        return LOG_LEVEL_MAPPING[value.upper()]
    else:
        raise ValueError("Not a log level")


@verificator
def exception(value):
    if EXCEPTION_REGEX.match(value):
        try:
            exception = eval(value)
        except Exception:
            raise ValueError("Not an exception: %s" % value)
        if not isinstance(exception, Exception):
            raise ValueError("Not an exception")
        return exception
    else:
        raise ValueError("Not an exception")


@verificator
def thread(value):
    print("???", value)
    match = THREAD_REGEX.match(value)
    if match:
        return int(value) if match.lastindex else str(value)
    else:
        raise ValueError("Not a name")
