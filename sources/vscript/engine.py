
from builtins import str
import sys
import re

from weakref import WeakKeyDictionary
from threading import RLock
# from utils.mutex import VDOM_named_mutex_auto as auto_mutex
from utils.tracing import format_exception_trace
from . import errors, lexemes, syntax
from .variables import variant
from .essentials import exitloop
from .prepare import lexer, parser
from .subtypes import v_nothing
from .wrappers.environment import v_server, v_request, v_response, v_session, v_application
from .wrappers.scripting import v_vdomobject
from . import wrappers


vscript_source_string = u"<vscript>"
vscript_wrappers_name = "wrappers"

vscript_default_code = compile(u"", vscript_source_string, u"exec")
vscript_default_listing = ""
vscript_default_source = []

vscript_default_action_namespace = {
    u"v_server": v_server(),
    u"v_request": v_request(),
    u"v_response": v_response(),
    u"v_session": v_session(),
    u"v_application": v_application()}
vscript_default_environment = {
    u"v_this": None,
    u"v_server": None,
    u"v_request": None,
    u"v_response": None,
    u"v_session": None,
    u"v_application": None}

vscript_global_lock = RLock()
vscript_global_counter = 0
weakuses = WeakKeyDictionary()


for name in dir(wrappers):
    if name.startswith("v_"):
        vscript_default_environment.setdefault(name, vscript_wrappers_name)


def is_vscript(traceback):
    if traceback is not None:
        while traceback.tb_next is not None:
            traceback = traceback.tb_next
        return "__vscript__" in traceback.tb_frame.f_globals
    else:
        return False


def search_exception_place(error, traceback):
    result = None
    while traceback is not None:
        frame = traceback.tb_frame
        information = frame.f_globals.get("__vscript__")
        if information:
            result = None
        elif not result:
            code_name = frame.f_code.co_name
            if code_name.startswith("v_"):
                result = "Internal error in \"%s\" procedure" % code_name[2:]
            elif code_name == "__init__":
                instance = frame.f_locals.get("self", None)
                if instance is not None:
                    class_name = type(instance).__name__
                    if class_name.startswith("v_"):
                        result = "Internal error during \"%s\" initialization" % class_name[2:]
        traceback = traceback.tb_next
    return result


def check_exception(error, traceback, error_type):
    vtraceback = []
    while traceback is not None:
        frame = traceback.tb_frame
        information = frame.f_globals.get("__vscript__")
        if information:
            try:
                lineno = information[traceback.tb_lineno - 1][0]
            except:
                lineno = None
            try:
                library = frame.f_globals.get("__name__").partition(".")[2]
            except:
                library = None
            vtraceback.append((library, lineno))
        traceback = traceback.tb_next

    error.source = error_type
    error.traceback = vtraceback
    if vtraceback:
        error.library, error.line = vtraceback[-1]


def vcompile(script=None, let=None, set=None, filename=None, bytecode=1, package=None,
             lines=None, environment=None, use=None, anyway=1, quiet=None, listing=False, safe=None):
    global vscript_global_counter
    if script is None:
        if let is not None:
            script = "result=%s" % let
        elif set is not None:
            script = "set result=%s" % set
        else:
            return vscript_default_code, vscript_default_source
    if not safe:
        # mutex = auto_mutex("vscript_engine_compile_mutex")
        vscript_global_lock.acquire()
        if vscript_global_counter:
            vscript_global_lock.release()
            raise errors.lock_error
        vscript_global_counter += 1
    try:
        source = None
        if not quiet and listing:
            debug("- - - - - - - - - - - - - - - - - - - -")
            for line, statement in enumerate(script.split("\n")):
                debug((u"  %s      %s" % (str(line + 1).ljust(4), statement.expandtabs(4))).encode("ascii", "backslashreplace"))
            debug("- - - - - - - - - - - - - - - - - - - -")
        lexer.lineno = 1
        try:
            parser.package = package
            parser.environment = vscript_default_environment if environment is None else environment
            source = parser.parse(script, lexer=lexer, debug=0, tracking=0).compose(0)
        finally:
            parser.package = None
            parser.environment = None
        if lines:
            source[0:0] = ((None, 0, line) for line in lines)
        if not quiet and listing:
            for line, data in enumerate(source):
                debug((u"  %s %s %s%s" % (str(line + 1).ljust(4),
                        str("" if data[0] is None else data[0]).ljust(4),
                    "    " * data[1], data[2].expandtabs(4))).encode("ascii", "backslashreplace"))
            debug("- - - - - - - - - - - - - - - - - - - -")
        code = u"\n".join([u"%s%s" % (u"\t" * ident, string) for line, ident, string in source])
        if bytecode:
            code = compile(code, filename or vscript_source_string, u"exec")
        if use:
            use_code, use_source = vcompile(use, package=package, environment=environment, safe=True)
            weakuses[code] = use_code, use_source
        return code, source
    except errors.generic:
        error_class, error, traceback = sys.exc_info()
        try:
            check_exception(error, traceback, errors.generic.compilation)
            if error.line is None:
                error.line = lexer.lineno
                if isinstance(error, errors.unknown_syntax_error):
                    position = getattr(parser.symstack[-1], "lexpos", None)
                    if position is not None:
                        newline_position = script.rfind("\n", 0, position)
                        if newline_position < 0:
                            newline_position = 0
                        character, column = script[position], (position - newline_position) or 1
                        error.near = (column, character) if ' ' <= character <= '~' else column
            if anyway:
                if bytecode:
                    return vscript_default_code, vscript_default_source
                else:
                    return vscript_default_listing, vscript_default_source
            else:
                raise
        finally:
            del traceback
    finally:
        if not safe:
            # del mutex
            vscript_global_counter -= 1
            vscript_global_lock.release()


def vexecute(code, source, object=None, namespace=None, environment=None, use=None, quiet=None):
    try:
        try:
            if namespace is None:
                namespace = {}
            if environment is None:
                namespace[u"v_this"] = v_vdomobject(object) if object else v_nothing
                namespace.update(vscript_default_action_namespace)
            else:
                namespace.update(environment)
            if use:
                use_code, use_source = weakuses[code]
                vexecute(use_code, use_source, namespace=namespace, environment=environment)
            namespace["__vscript__"] = source
            exec(code, namespace)
        except exitloop:
            error_class, error, traceback = sys.exc_info()
            try:
                raise errors.invalid_exit_statement.with_traceback(traceback)
            finally:
                del traceback
        except AttributeError:
            error_class, error, traceback = sys.exc_info()
            try:
                if is_vscript(traceback):
                    result = re.search(".+ has no attribute \'(.+)\'", str(error))
                    if result:
                        raise errors.object_has_no_property(name=result.group(1)).with_traceback(traceback)
                raise
            finally:
                del traceback
        except ValueError:
            error_class, error, traceback = sys.exc_info()
            try:
                if is_vscript(traceback):
                    raise errors.type_mismatch.with_traceback(traceback)
                raise
            finally:
                del traceback
        except TypeError:
            error_class, error, traceback = sys.exc_info()
            try:
                if is_vscript(traceback):
                    result = re.search("(.+)\(\) (?:takes no arguments)|(?:takes exactly \d+ arguments) \(\d+ given\)", str(error))
                    if result:
                        raise errors.wrong_number_of_arguments(name=result.group(1)).with_traceback(traceback)
                    elif re.match("__init__\(\) got an unexpected keyword argument 'set'", str(error)):
                        raise errors.illegal_assigment
                raise
            finally:
                del traceback
    except errors.generic:
        error_class, error, traceback = sys.exc_info()
        try:
            check_exception(error, traceback, errors.generic.runtime)
            raise
        finally:
            del traceback
    except errors.python:
        error_class, error, traceback = information = sys.exc_info()
        try:
            report = format_exception_trace(information=information, locals=True)
            new_error = errors.internal_error(replace=search_exception_place(error, traceback), cause=information, report=report)
            check_exception(new_error, traceback, errors.generic.runtime)
            raise new_error.with_traceback(traceback)
        finally:
            del traceback


def vevaluate(code, source, object=None, namespace=None, environment=None, use=None, quiet=None, result=None):
    if result is None:
        result = variant()
    if namespace is None:
        namespace = {"v_result": result}
    else:
        namespace["v_result"] = result
    vexecute(code, source, object=object, namespace=namespace, environment=environment, use=use, quiet=quiet)
    return namespace["v_result"].subtype
