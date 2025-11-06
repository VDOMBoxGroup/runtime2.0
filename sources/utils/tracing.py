

from builtins import map
from builtins import next
from builtins import zip
from builtins import str

import sys
import gc
import types
import numbers
import linecache
import traceback
import inspect
import threading
import os
from collections import OrderedDict
from itertools import islice
import settings
from utils.auxiliary import enquote, headline, fit, align, lfill
from utils.representation import represent
from utils.console import width


LOGGING = None
TRACING = None

BINARY_ALIAS = "<sources>"
SERVER_ALIAS = "<server>"
TYPES_ALIAS = "<types>"
APPLICATIONS_ALIAS = "<applications>"
PYTHON_ALIAS = "<python>"

UNKNOWN_STATEMENT = "???"
COMPACT_DEFAULT_MODE = False
DEEPER_LATER = 1
DEFAULT_FILLER = "."

DESIRED_WIDTH = 139
CAPTION_WIDTH = 36
LOCATION_WIDTH = 99 if width == sys.maxsize else min(width * 2 // 3, 99)
STATEMENT_WIDTH = DESIRED_WIDTH - LOCATION_WIDTH
NAME_WIDTH = 32
VALUE_WIDTH = DESIRED_WIDTH - NAME_WIDTH

BINARY_PATH = os.path.dirname(sys.argv[0]) or os.getcwd()
SERVER_PATH = os.path.split(BINARY_PATH)[0]
TYPES_PATH = os.path.abspath(os.path.join(BINARY_PATH, settings.TYPES_LOCATION))
APPLICATIONS_PATH = os.path.abspath(os.path.join(BINARY_PATH, settings.APPLICATIONS_LOCATION))
PYTHON_PATH = sys.prefix

WELL_KNOWN_MODULES = "_json", "_ast", "thread", "operator", "itertools", "exceptions"

REPRESENTATION_WIDTH = 40
REPRESENTATION_VALUE_LIMIT = 40

MAXIMAL_CAUSES_EXTRACTION = 10


# types

def define_types(argument):
    global WrapperDescriptorType, TupleIterator

    def inner():
        global CellType
        CellType = type(inner.__closure__[0])

    inner()

    WrapperDescriptorType = type(str.__dict__["__add__"])
    TupleIterator = type(iter(()))


define_types("just a value")


# auxiliary

def iterlast(subject):
    if isinstance(subject, tuple):
        for last in subject:
            yield last
    else:
        last = subject
    while 1:
        yield last


def clarify_source_path(path):
    if path.startswith("<"):
        return path
    path = os.path.normpath(path if os.path.isabs(path) else os.path.join(BINARY_PATH, path))
    if path.startswith(BINARY_PATH):
        return BINARY_ALIAS + path[len(BINARY_PATH):]
    elif path.startswith(TYPES_PATH):
        return TYPES_ALIAS + path[len(TYPES_PATH):]
    elif path.startswith(APPLICATIONS_PATH):
        return APPLICATIONS_ALIAS + path[len(APPLICATIONS_PATH):]
    elif path.startswith(SERVER_PATH):
        return SERVER_ALIAS + path[len(SERVER_PATH):]
    elif path.startswith(PYTHON_PATH):
        return PYTHON_ALIAS + path[len(PYTHON_PATH):]
    else:
        return path


def restore_source_path(path):
    if path.startswith(BINARY_ALIAS):
        return BINARY_PATH + path[len(BINARY_ALIAS):]
    elif path.startswith(TYPES_ALIAS):
        return TYPES_PATH + path[len(TYPES_ALIAS):]
    elif path.startswith(APPLICATIONS_ALIAS):
        return APPLICATIONS_PATH + path[len(APPLICATIONS_ALIAS):]
    elif path.startswith(SERVER_ALIAS):
        return SERVER_PATH + path[len(SERVER_ALIAS):]
    elif path.startswith(PYTHON_ALIAS):
        return PYTHON_PATH + path[len(PYTHON_PATH):]
    else:
        return path


def extract_causes(exception):
    # NOTE: currently used in vscript to show original errors
    #       in Python 3 we can user native __cause__ mechanism
    result = []
    while 1:
        information = getattr(exception, "cause", None)
        if information is None or not isinstance(information, tuple) or len(information) != 3:
            break

        exception = information[1]
        if not isinstance(exception, BaseException):
            break

        result.append(information)
        if len(result) == MAXIMAL_CAUSES_EXTRACTION:
            break

    return result


def extract_stack(frame=None, skip_tracing=True, skip=None, until=None):
    if frame is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            frame = sys.exc_info()[2].tb_frame.f_back

    lines = []
    while frame is not None:
        namespace = frame.f_globals
        lineno = frame.f_lineno
        code = frame.f_code
        filename = code.co_filename
        name = code.co_name

        if skip_tracing:
            if namespace.get("TRACING", KeyError) is None:
                frame = frame.f_back
                continue
            else:
                skip_tracing = False

        if until:
            module_name = namespace.get("__name__")
            if module_name and module_name.startswith(until):
                break

        if skip and name in skip:
            frame = frame.f_back
            continue
        else:
            skip = None

        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, frame.f_globals)
        if line:
            line = line.strip()
        else:
            line = None

        lines.append((filename, lineno, name, line))
        frame = frame.f_back

    lines.reverse()
    return lines


def extract_caller(recursion=True):
    if recursion:
        frame = sys._getframe(3)
    else:
        frame = sys._getframe(2)
        code = frame.f_code
        while frame.f_code == code:
            frame = frame.f_back

    code = frame.f_code
    lineno = frame.f_lineno
    code = frame.f_code
    filename = code.co_filename
    name = code.co_name

    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, frame.f_globals)
    if line:
        line = line.strip()
    else:
        line = None

    return filename, lineno, name, line


def collect_referrers(referent, limit=16, depth=32, rank=9, exclude=None):

    ACCEPT = "ACCPET"
    REJECT = "REJECT"

    class Chain(tuple):

        class Part(str):
            pass

        class KeyValue(Part):
            key = None
            module = None

        class Cell(Part):
            uid = None

        parts = ()
        rank = 0.50
        depth = 1
        known = set()
        action = None

        description = property(lambda self: " < ".join(self.parts))

        referent = property(lambda self: self[0])
        referrer = property(lambda self: self[1])

        def combine(self, value):
            chain = Chain(self + (value,))
            chain.parts = self.parts
            chain.rank = self.rank
            chain.depth = self.depth + 1
            chain.known = self.known
            chain.action = self.action
            return chain

        def reduce(self, part, rank=1.00, action=None):
            chain = Chain(self[1:])
            chain.parts = self.parts + (part,)
            chain.rank = self.rank * rank
            chain.depth = self.depth
            chain.known = self.known.copy()
            chain.known.add(id(self[0]))
            chain.action = self.action if action is None else action
            return chain

        def modify(self, part=None, rank=1.00, action=False):
            if part is not None:
                self.parts += (part,)
            self.rank *= rank
            if action is not None:
                self.action = action
            return self

        def drop(self, count):
            self.parts = self.parts[:-count]
            return self

        def __repr__(self):
            return "<chain%s: %s>" % ({None: "", ACCEPT: "+A", REJECT: "+R"}[self.action],
                ", ".join([describe_object(item) for item in self]))

        __str__ = __repr__

    def represent(value):
        if isinstance(value, bytes):
            result = enquote(value)
            if len(result) > REPRESENTATION_VALUE_LIMIT:
                return "%s...%s" % (result[:REPRESENTATION_VALUE_LIMIT - 4], result[-1])
            else:
                return result
        elif isinstance(value, numbers.Number):
            return str(value)
        else:
            return describe_object(value)

    def describe(chain):

        def is_or_equal(value, referent):
            return value is referent or \
                (isinstance(value, types.DictProxyType) and value == referent)

        if len(chain) < 2:
            return chain.modify(rank=0.10, action=ACCEPT)
        elif isinstance(chain.referrer, (tuple, list, set, frozenset)):
            return chain.reduce(describe_object(chain.referrer), rank=0.80)
        elif isinstance(chain.referrer, dict):
            for key, value in chain.referrer.copy().items():
                if value is chain.referent:
                    part = "key %s in %s" % (represent(key), describe_object(chain.referrer))
                    if isinstance(key, bytes):
                        part = Chain.KeyValue(part)
                        part.key = key
                        if id(chain.referrer) in modules:
                            part.module = inspect.getmodule(chain.referent)
                    return chain.reduce(part, rank=0.80)
            return chain.reduce(describe_object(chain.referrer), rank=0.80)
        elif isinstance(chain.referrer, TupleIterator):
            return chain.reduce(describe_object(chain.referrer), rank=0.01)
        elif getattr(chain.referrer, "func_globals", None) is chain.referent:
            return chain.modify(action=REJECT)
        else:
            cycle = id(chain.referrer) in chain.known

            if getattr(chain.referrer, "__self__", None) is chain.referent:
                rank, part = 0.50, "instance of " + describe_object(chain.referrer)
            elif getattr(chain.referrer, "__closure__", None) is chain.referent:
                rank, part = 1.00, "closure of " + describe_object(chain.referrer)
                if len(chain.parts) > 1:
                    for name, value in zip(chain.referrer.__code__.co_freevars, chain.referrer.__closure__):
                        if id(value) == chain.parts[-2].uid:
                            rank, part = 1.25, "variable \"%s\" in %s" % (name, part)
                chain.drop(2)
            elif getattr(chain.referrer, "func_defaults", None) is chain.referent:
                rank, part = 1.25, "defaults of " + describe_object(chain.referrer)
            elif is_or_equal(getattr(chain.referrer, "__dict__", None), chain.referent):
                if chain.parts and isinstance(chain.parts[-1], Chain.KeyValue):
                    rank, part = 1.25, "attribute \"%s\" of %s" % (chain.parts[-1].key, describe_object(chain.referrer))
                    if isinstance(chain.referrer, types.ModuleType):
                        module = chain.parts[-1].module
                        if module is not None:
                            module_name = getattr(module, "__name__", "<module without name>")
                            name = getattr(chain.referrer, "__name__", "<referrer without name>")
                            if module_name == name:
                                rank = 4.00
                            elif module_name.startswith(name + "."):
                                rank = 2.00
                    chain.drop(1)
                else:
                    rank, part = 1.00, "namespace of %s" % describe_object(chain.referrer)
            elif getattr(chain.referrer, "__bases__", None) is chain.referent:
                rank, part = 0.75, "ancestors of " + describe_object(chain.referrer)
            elif getattr(chain.referrer, "__mro__", None) is chain.referent:
                rank, part = 0.50, "method resolution order of " + describe_object(chain.referrer)
            elif isinstance(chain.referrer, CellType):
                rank, part = 1.00, Chain.Cell(describe_object(chain.referrer))
                part.uid = id(chain.referrer)
                cycle = False
            else:
                rank, part = 1.0, describe_object(chain.referrer)

            if isinstance(chain.referrer, types.ModuleType):
                chain = chain.reduce(part, rank=2.00 * rank, action=ACCEPT)
            elif hasattr(chain.referrer, "__describe__"):
                chain = chain.reduce(part, rank=2.00 * rank, action=ACCEPT)
            elif isinstance(chain.referrer, type):
                chain = chain.reduce(part, rank=0.10 * rank, action=ACCEPT)
            else:
                chain = chain.reduce(part, rank=0.80 * rank)

            return chain.modify("...", action=ACCEPT) if cycle else chain

    def complete(chains):
        for chain in chains:
            if len(chain) > 2:
                yield chain
            else:
                referrers = gc.get_referrers(chain[-1])
                local_exclude = {id(chains), id(referrers), id(sys._getframe())}
                exclude.update(local_exclude)
                try:
                    counter = 0
                    for referrer in referrers:
                        if (isinstance(referrer, Chain)
                                or id(referrer) in exclude
                                or (chain.depth > 1
                                    and id(referrer) in modules
                                    and not isinstance(chain[-1], (tuple, list, set, frozenset, dict)))):
                            continue
                        yield chain.combine(referrer)
                        counter += 1
                    if counter == 0:
                        yield chain
                finally:
                    exclude.difference_update(local_exclude)
                    del referrers

    def iterate(chains):
        for chain in chains:
            chain = describe(chain)
            if chain.action is REJECT:
                continue
            elif chain.action is ACCEPT or chain.rank >= rank or chain.depth >= depth:
                if chain.parts:
                    ready.append((chain.rank, chain.depth, chain.parts))
                    if len(ready) == limit:
                        return
            else:
                yield chain

    if exclude:
        exclude = {id(object) for object in exclude}
    else:
        exclude = set()

    frame = sys._getframe()
    while frame:
        exclude.add(id(frame))
        frame = frame.f_back

    exclude.add(id(sys.modules))
    modules = set()
    for module in list(sys.modules.values()):
        if module is not None:
            modules.add(id(module.__dict__))

    ready, chains = [], (Chain((referent,)),)
    while chains:
        chains = tuple(iterate(complete(chains)))
        if len(ready) == limit:
            break

    return ready


# detectors

def is_builtin_object(object):
    return type(object).__module__ == "__builtin__"


def is_server_object(object, default=True):
    module_name = type(object).__module__
    if module_name == "__builtin__":
        return False
    else:
        try:
            module_location = sys.modules[module_name].__file__
            if os.path.isabs(module_location):
                return module_location.startswith(BINARY_PATH)
        except Exception:
            pass

        if module_name in WELL_KNOWN_MODULES:
            return False
        else:
            return default


# describers

def describe_exception(exception):
    name = type(exception).__name__

    try:
        if isinstance(exception, types.InstanceType):
            description = getattr(exception, "__str__")()
        else:
            try:
                description = str(exception)
            except Exception:
                description = str(exception).encode("ascii", "backslashreplace")
    except Exception:
        description = None

    if description:
        return "%s: %s" % (name, headline(description))
    else:
        return name


def describe_thread(thread=None):
    if thread is None:
        thread = threading.current_thread()
    extra = tuple([_f for _f in (
        "Daemon" if thread.daemon else None,
        "Stopping" if getattr(thread, "_stopping", None) else None) if _f])
    if extra:
        return "%s (%d: %s)" % (thread.name, thread.ident, ", ".join(extra))
    else:
        return "%s (%d)" % (thread.name, thread.ident)


def describe_object(value):
    try:
        describe = getattr(value, "__describe__", None)
    except Exception:
        pass
    else:
        if describe:
            try:
                return describe()
            except Exception:
                pass

    kind, details = type(value).__name__, "%08X" % id(value)
    if isinstance(value, type):
        name = value.__name__
        module = value.__module__
    elif isinstance(value, types.ModuleType):
        name = getattr(value, "__name__", "")
        module = ""
    elif isinstance(value, (types.BuiltinMethodType, types.BuiltinFunctionType)):
        name = value.__name__
        module = ""
    elif isinstance(value, types.FunctionType):
        name = value.__name__
        module = getattr(inspect.getmodule(value), "__name__", "")
        details = ""
    elif isinstance(value, types.CodeType):
        name = value.co_name
        module = getattr(inspect.getmodule(value), "__name__", "")
    elif isinstance(value, types.MethodType):
        name = value.__func__.__name__
        if value.__self__ is None:
            module = getattr(inspect.getmodule(value), "__name__", "")
        else:
            details = "bound to " + describe_object(value.__self__)
            module = ""
    elif isinstance(value, types.FrameType):
        name = value.f_code.co_name
        module = getattr(inspect.getmodule(value), "__name__", "")
    elif isinstance(value, types.InstanceType):
        name = value.__class__.__name__
        module = value.__module__
    elif type(value).__module__ == "__builtin__":
        name = ""
        module = ""
        if isinstance(value, (tuple, list, dict, set)):
            try:
                representation = repr(value)
            except Exception:
                details = "unrepresentable"
            else:
                details += " %s%s: %d" % (
                    fit(representation[:-1], REPRESENTATION_WIDTH - 2),
                    representation[-1],
                    len(value))
    else:
        kind = "object"
        name = type(value).__name__
        module = type(value).__module__

    if module:
        module = "from " + module

    return " ".join([_f for _f in (kind, name, details, module) if _f])


def describe_reference(value, limit=16, depth=32, rank=9, exclude=None, default=None):
    if value is None:
        return "None"
    else:
        references = collect_referrers(value, limit=limit, depth=depth, rank=rank, exclude=exclude)
        if references:
            _, _, parts = max(references, key=lambda x: x[0])
            return " < ".join(part for part in parts)
        else:
            return default


def describe_caller(recursion=True, statement=False):
    path, line, function, caller_statement = extract_caller(recursion=recursion)
    description = ":".join(map(str, (path, line, function)))
    if statement:
        return description, caller_statement
    else:
        return description


# formatting

def format_source_point(path, line, function, indent="", width=LOCATION_WIDTH):
    ending = fit(":%s:%s" % (line, function), NAME_WIDTH)
    fullname = fit(clarify_source_path(path), width - len(indent) - len(ending))
    return fullname + ending


def extract_trace(stack, limit=sys.maxsize):
    entries = islice(reversed(stack), limit) if DEEPER_LATER else stack[len(stack) - limit:]
    result = []
    for path, line, function, statement in entries:
        result.append((clarify_source_path(path), line, function, statement or UNKNOWN_STATEMENT))
    return result


def format_trace(stack, limit=sys.maxsize,
        statements=True, caption=None, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    width = LOCATION_WIDTH
    entries = islice(reversed(stack), limit) if DEEPER_LATER else stack[len(stack) - limit:]

    if caption:
        if compact:
            indent = indent + align(caption, CAPTION_WIDTH, " ", "." if limit > 1 else " ")
            indent = indent, " " * len(indent)
            filler = ".", filler
            width += CAPTION_WIDTH
        else:
            lines.append(indent + caption)
            indent += settings.LOGGING_INDENT

    indents, fillers = iterlast(indent), iterlast(filler)
    for path, line, function, statement in entries:
        indent, filler = next(indents), next(fillers)
        ending = fit(":%s:%s" % (line, function), NAME_WIDTH)
        fullname = fit(clarify_source_path(path), width - len(indent) - len(ending))
        location = fullname + ending
        if statements:
            lines.append("%s%s%s" % (indent,
                align(location, width - len(indent), " ", filler=filler),
                align(statement or UNKNOWN_STATEMENT, STATEMENT_WIDTH, "", filler=" ")))
        else:
            lines.append("%s%s" % (indent, location))

    if into is None:
        lines.append("")
        return "\n".join(lines)


def extract_thread_trace(thread=None, limit=sys.maxsize, skip=None, until=None):
    if thread is None:
        stack = extract_stack(skip=skip, until=until)
    else:
        try:
            frame = sys._current_frames()[thread.ident]
        except KeyError:
            return []
        else:
            stack = extract_stack(frame, skip=skip, until=until)

    return extract_trace(stack, limit=limit)


def format_thread_trace(thread=None, limit=sys.maxsize,
        statements=True, caption=None, header=False, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, skip=None, until=None, into=None):
    lines = [] if into is None else into

    if thread is None:
        stack = extract_stack(skip=skip, until=until)
    else:
        try:
            frame = sys._current_frames()[thread.ident]
        except KeyError:
            return "" if into is None else None
        else:
            stack = extract_stack(frame, skip=skip, until=until)

    if caption:
        lines.append(caption)

    if header:
        if thread is None:
            thread = threading.current_thread()
        caption = describe_thread(thread)
    else:
        caption = None

    format_trace(stack,
        limit=limit,
        statements=statements,
        caption=caption,
        compact=compact,
        indent=indent,
        filler=filler,
        into=lines)

    if into is None:
        lines.append("")
        return "\n".join(lines)


def extract_threads_trace(limit=sys.maxsize, current=True):
    current_thread = None if current else threading.current_thread()

    result = OrderedDict()
    for thread in threading.enumerate():
        if thread == current_thread:
            continue
        result[thread] = extract_thread_trace(thread, limit=limit, skip=None, until=None)

    return result


def format_threads_trace(limit=sys.maxsize,
        statements=True, compact=COMPACT_DEFAULT_MODE, current=True,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    current_thread = None if current else threading.current_thread()

    for thread in threading.enumerate():
        if thread == current_thread:
            continue
        format_thread_trace(thread,
            limit=limit,
            statements=statements,
            header=True,
            compact=compact,
            indent=indent,
            filler=filler,
            skip=None,
            until=None,
            into=lines)

    if into is None:
        lines.append("")
        return "\n".join(lines)


def extract_exception_locals(information=None, ignore_builtins=True):
    extype, exvalue, extraceback = information or sys.exc_info()
    frame = inspect.getinnerframes(extraceback)[-1][0]

    result = {}
    for name, value in frame.f_locals.items():
        if ignore_builtins and name == "__builtins__":
            description = "{...}"
        else:
            try:
                description = represent(value)
            except Exception as error:
                try:
                    message = str(error)
                except Exception:
                    message = type(error).__name__
                description = "Unable to represent: %s" % message
        result[name] = description

    return result


def format_exception_locals(information=None, ignore_builtins=True, caption=None,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    extype, exvalue, extraceback = information or sys.exc_info()
    frame = inspect.getinnerframes(extraceback)[-1][0]

    if caption:
        lines.append(indent + caption)
        indent += settings.LOGGING_INDENT

    for name, value in frame.f_locals.items():
        caption = align(name, NAME_WIDTH - len(indent), " ", filler=filler)
        if ignore_builtins and name == "__builtins__":
            description = "{...}"
        else:
            try:
                description = represent(
                    value, width=VALUE_WIDTH).replace("\n", "\n%s%s" % ("", NAME_WIDTH * " "))
            except Exception as error:
                try:
                    message = str(error)
                except Exception:
                    message = type(error).__name__
                description = "Unable to represent: %s" % message
        lines.append("%s%s%s" % (indent, caption, description))

    if into is None:
        lines.append("")
        return "\n".join(lines)


def extract_exception_trace(information=None, limit=sys.maxsize,
        locals=False, threads=False, separate_exception=False):
    extype, exvalue, extraceback = information = information or sys.exc_info()
    if exvalue is None:
        return

    stack = traceback.extract_tb(extraceback)
    description = describe_exception(exvalue)
    causes = extract_causes(exvalue)
    trace = extract_trace(stack, limit=limit)

    result = description, causes, trace
    if locals:
        result += extract_exception_locals(information),
    if threads:
        result += extract_threads_trace(limit=limit, current=False),

    return result


def format_exception_trace(information=None, limit=sys.maxsize,
        statements=True, caption=None, label=None, compact=COMPACT_DEFAULT_MODE,
        locals=False, threads=False, separate=False,
        indent="", filler=DEFAULT_FILLER, into=None):
    extype, exvalue, extraceback = information = information or sys.exc_info()
    if exvalue is None:
        return

    lines = [] if into is None else into
    stack = traceback.extract_tb(extraceback)

    if separate:
        separator = indent + \
            lfill("- ", LOCATION_WIDTH + STATEMENT_WIDTH + (CAPTION_WIDTH if compact else 0) - len(indent))
        lines.append(separator)

    if caption:
        lines.append(caption)
        indent += settings.LOGGING_INDENT

    description = describe_exception(exvalue)
    if label:
        description = "%s: %s" % (label, description)
    lines.append("%s%s" % (indent, description))

    causes = extract_causes(exvalue)
    for cause_type, cause_value, cause_traceback in causes:
        lines.append("%sCaused by: %s" % (indent, describe_exception(cause_value)))

    if locals:
        format_exception_locals(information, indent=indent + settings.LOGGING_INDENT, into=lines)

    format_trace(stack,
        limit=limit,
        statements=statements,
        compact=compact,
        caption=describe_thread(threading.current_thread()),
        indent=indent,
        filler=filler,
        into=lines)

    if threads:
        format_threads_trace(
            limit=limit,
            statements=statements,
            compact=compact,
            current=False,
            indent=indent,
            filler=filler,
            into=lines)

    if separate:
        lines.append(separator)

    if into is None:
        lines.append("")
        return "\n".join(lines)


# references

def format_referrers(referent, limit=16,
        caption=None, explain=True,
        indent="", into=None):
    lines = [] if into is None else into

    if caption:
        lines.append(indent + caption)
        indent += settings.LOGGING_INDENT

    if referent is not None:
        references = collect_referrers(referent, limit=limit, rank=9)
        if references:
            references.sort(cmp=lambda x, y: (-x[0] > -y[0]) - (-x[0] < -y[0]))
            for rank, depth, parts in references:
                lines.append(indent + parts[0])
                for part in parts[1:]:
                    lines.append("%s%s%s" % (indent, settings.LOGGING_INDENT, part))
        else:
            lines.append(indent + "no significant referrers")

    if into is None:
        lines.append("")
        return "\n".join(lines)


# miscellaneous

def enumerate_thread_trace(thread=None):
    if thread is None:
        stack = traceback.extract_stack()
    else:
        frame = sys._current_frames()[thread if isinstance(thread, int) else thread.ident]
        stack = traceback.extract_stack(frame)
    for path, line, function, statement in stack:
        yield clarify_source_path(path), line, function, statement


def get_thread_trace(thread=None):
    return tuple(enumerate_thread_trace(thread))


def enumerate_threads_trace():
    for thread in threading.enumerate():
        yield thread, enumerate_thread_trace(thread)


def get_threads_trace():
    return tuple((thread, tuple(trace)) for thread, trace in enumerate_threads_trace())


# wrappers

def show_trace(stack, limit=sys.maxsize,
        statements=True, caption=None, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stdout).write(format_trace(
        stack, limit, statements, caption, compact, indent, filler))


def show_thread_trace(thread=None, limit=sys.maxsize,
        statements=True, caption=None, header=False, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, skip=None, until=None, output=None):
    (output or sys.stdout).write(format_thread_trace(
        thread, limit, statements, caption, header, compact, indent, filler, skip, until))


def show_threads_trace(limit=sys.maxsize,
        statements=True, compact=COMPACT_DEFAULT_MODE, current=True,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stdout).write(format_threads_trace(
        limit, statements, compact, current, indent, filler))


def show_exception_locals(information=None, ignore_builtins=True, caption=None,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stderr).write(format_exception_locals(
        information, ignore_builtins, caption, indent, filler))


def show_exception_trace(information=None, limit=sys.maxsize,
        statements=True, caption=None, label=None, compact=COMPACT_DEFAULT_MODE,
        locals=False, threads=False, separate=False,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stderr).write(format_exception_trace(
        information, limit, statements, caption, label, compact,
        locals, threads, separate, indent, filler))


def show_referrers(referent, limit=16,
        caption=None, explain=True,
        indent="", output=None):
    (output or sys.stdout).write(format_referrers(
        referent, limit, caption, explain, indent))
