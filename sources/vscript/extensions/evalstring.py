
from builtins import next
from builtins import str
from types import MethodType
from collections import defaultdict
from threading import local

import re
import ast

from .. import errors
from ..primitives import primitive
from ..subtypes import generic, integer, double, string, boolean, date, dictionary, v_mismatch, v_nothing
from ..variables import shadow
from ..conversions import pack
from .jsons import v_asjson, v_tojson


SYSTEM_TYPE = string("system")
NUMERIC_TYPE = string("numeric")
STRING_TYPE = string("string")
DATE_TYPE = string("date")
BOOLEAN_TYPE = string("boolean")

DEFAULT_VALUE = string("null")

TRUE_BOOLEAN = boolean(True)
FALSE_BOOLEAN = boolean(False)
EMPTY_STRING = string("")
VALUE_STRING = string("value")
TYPE_STRING = string("type")

SPLIT_REGEX_TEMPLATE = "%(open)s(\=?.*?)%(close)s"
DEFAULT_DELIMITERS = "{", "}"
DEFAULT_SPLIT_REGEX = re.compile(
    SPLIT_REGEX_TEMPLATE % {"open": re.escape(DEFAULT_DELIMITERS[0]), "close": re.escape(DEFAULT_DELIMITERS[1])},
    re.MULTILINE)
SOURCE_STRING = "<evalstring expression>"


contexts = local()


class IntTransformer(ast.NodeTransformer):

    def visit_Num(self, node):
        return ast.copy_location(ast.Call(
            func=ast.Name(id='integer' if isinstance(node.n, int) else 'double', ctx=ast.Load(), lineno=0, col_offset=0),
            keywords=[],
            starargs=None,
            kwargs=None,
            args=[ast.Num(node.n, lineno=0, col_offset=0)]),
            node)

    def visit_Str(self, node):
        return ast.copy_location(ast.Call(
            func=ast.Name(id='string', ctx=ast.Load(), lineno=0, col_offset=0),
            keywords=[],
            starargs=None,
            kwargs=None,
            args=[ast.Str(node.s.decode("utf8"), lineno=0, col_offset=0)]),
            node)

    def visit_Name(self, node):
        if node.id in ('True', 'False'):
            return ast.copy_location(ast.Call(
                func=ast.Name(id='boolean', ctx=ast.Load(), lineno=0, col_offset=0),
                keywords=[],
                starargs=None,
                kwargs=None,
                args=[ast.Name(id='True' if node.id == 'True' else 'False', ctx=ast.Load(), lineno=0, col_offset=0)]),
                node)
        else:
            return node


class InstancesDict(defaultdict):

    def __missing__(self, key):
        return key()


class v_evalvariable(generic):

    def __init__(self):
        generic.__init__(self)
        self._value = DEFAULT_VALUE
        self._vartype = SYSTEM_TYPE

    value = property(lambda self: self._value)
    vartype = property(lambda self: self._vartype)

    def v_value(self, key=None, **keywords):
        if "let" in keywords:
            self.v_setvalue(keywords["let"])
        elif "set" in keywords:
            raise errors.object_has_no_property(u"value")
        else:
            return self.v_getvalue()

    def v_vartype(self, key=None, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property(u"vartype")
        else:
            return string(self._vartype)

    def v_isnull(self):
        if self._vartype is SYSTEM_TYPE:
            return boolean(self._value is DEFAULT_VALUE)
        else:
            return FALSE_BOOLEAN

    def v_getvalue(self):
        return self._value

    def v_setvalue(self, value):
        subtype = value.subtype
        if isinstance(subtype, (integer, double)):
            self._value = subtype
            self._vartype = NUMERIC_TYPE
        elif isinstance(subtype, string):
            self._value = subtype
            self._vartype = STRING_TYPE
        elif isinstance(subtype, date):
            self._value = subtype
            self._vartype = DATE_TYPE
        elif isinstance(subtype, boolean):
            self._value = subtype
            self._vartype = BOOLEAN_TYPE
        else:
            self._value = DEFAULT_VALUE
            self._vartype = SYSTEM_TYPE
        return v_mismatch

    def v_loadvalue(self, valueinfo):
        if TYPE_STRING in valueinfo and VALUE_STRING in valueinfo:
            subtype = valueinfo._items[VALUE_STRING]
            vartype = valueinfo._items[TYPE_STRING]
            if vartype in (NUMERIC_TYPE, STRING_TYPE, DATE_TYPE, BOOLEAN_TYPE):
                self._value = subtype
                self._vartype = vartype
            else:
                self._value = DEFAULT_VALUE
                self._vartype = SYSTEM_TYPE
        return v_mismatch

    def v_gettype(self):
        return self._vartype

    def v_convertto(self, new_type):
        value = new_type.as_string.lower()
        try:
            if value == NUMERIC_TYPE.value:
                self._value = double(self._value.value)
                self._vartype = NUMERIC_TYPE
                return TRUE_BOOLEAN
            elif value == STRING_TYPE.value:
                self._value = string(self._value.value)
                self._vartype = STRING_TYPE
                return TRUE_BOOLEAN
            elif value == DATE_TYPE.value:
                self._value = date(self._value.value)
                self._vartype = DATE_TYPE
                return TRUE_BOOLEAN
            elif value == BOOLEAN_TYPE.value:
                self._value = boolean(self._value.value)
                self._vartype = BOOLEAN_TYPE
                return TRUE_BOOLEAN
            else:
                return FALSE_BOOLEAN
        except:
            # NOTE: check this later
            return FALSE_BOOLEAN


class v_evalcontext(generic):

    def __init__(self):
        generic.__init__(self)
        self._variables = {}

    variables = property(lambda self: self._variables)

    def v_addvariable(self, name):
        name = name.as_string
        variable = self._variables.get(name)
        if variable is None:
            self._variables[name] = variable = v_evalvariable()
        if variable._vartype is SYSTEM_TYPE:
            variable._value = EMPTY_STRING
            variable._vartype = STRING_TYPE
        return v_mismatch

    v_vdim = v_addvariable

    def v_getvariable(self, name):
        name = name.as_string
        variable = self._variables.get(name)
        if variable is None:
            self._variables[name] = variable = v_evalvariable()
        return variable

    def v_setvariable(self, name, value):
        name = name.as_string
        variable = self._variables.get(name)
        if variable is None:
            self._variables[name] = variable = v_evalvariable()
        variable.v_setvalue(value)
        return v_mismatch

    def v_loadcontext(self, context):
        subtype = context.subtype

        try:
            if isinstance(subtype, string):
                items = v_asjson(context)
                if not isinstance(items, dictionary):
                    return FALSE_BOOLEAN
            elif isinstance(subtype, dictionary):
                items = context.as_dictionary
            else:
                return FALSE_BOOLEAN
            self._variables = {}
            for name, value in items.items.items():
                self._variables[name.as_string] = variable = v_evalvariable()
                variable.v_loadvalue(value)
            return TRUE_BOOLEAN
        except:
            # NOTE: check this later
            return FALSE_BOOLEAN

    def v_savecontext(self):
        return v_tojson(dictionary(
            {string(name): dictionary({VALUE_STRING: variable.value, TYPE_STRING: variable.vartype})
            for name, variable in self._variables.items()}))


def v_evalglobalcontext():
    return getattr(contexts, "current", v_nothing)


class v_evalstring(generic):

    def __init__(self):
        generic.__init__(self)
        self._regex = DEFAULT_SPLIT_REGEX
        self._instances = InstancesDict()
        self._context = None
        self._functions = {}

    def v_context(self, key=None, **keywords):
        if "let" in keywords:
            raise errors.object_has_no_property(u"context")
        elif "set" in keywords:
            self._context = keywords["set"].as_specific(v_evalcontext)
        else:
            return v_nothing if self._context is None else self._context

    v_evaluatorcontext = v_context

    def v_setdelimiters(self, open, close):
        self._regex = re.compile(
            SPLIT_REGEX_TEMPLATE % {"open": re.escape(open.as_string), "close": re.escape(close.as_string)},
            re.MULTILINE)

    def v_addfunction(self, klass, name):
        instance = self._instances[klass]
        name = name.as_string
        function = getattr(instance, "v_%s" % name)
        if not isinstance(function, MethodType):
            raise errors.expected_function

        def wrapper(*arguments):
            return function(*(argument if isinstance(argument, primitive) else pack(argument) for argument in arguments)).as_is

        self._functions[name] = wrapper
        return v_mismatch

    def v_addfunctions(self, klass):
        instance = self._instances[klass]
        for name in dir(instance):
            if name.startswith("v_") and isinstance(getattr(instance, name), MethodType):
                self.v_addfunction(klass, string(name[2:]))
        return v_mismatch

    v_addfunctionlib = v_addfunctions

    def v_compile(self, template):
        parts = self._regex.split(template.as_string)
        self._strings = parts[0::2]
        rw = IntTransformer()
        self._expressions = tuple(
            (True, compile(rw.visit(compile(expression[1:], SOURCE_STRING, "eval", flags=ast.PyCF_ONLY_AST)), SOURCE_STRING, "eval"))
            if expression.startswith("=") else
            (False, compile(rw.visit(compile(expression, SOURCE_STRING, "exec", flags=ast.PyCF_ONLY_AST)), SOURCE_STRING, "exec"))
            for expression in parts[1::2])
        return v_mismatch

    def v_eval(self):

        def generate():
            iterator = iter(self._strings)
            yield next(iterator)
            for evaluate, expression in self._expressions:
                if evaluate:
                    ret = eval(expression, namespace)
                    if isinstance(ret, primitive):
                        yield ret.as_string
                    else:
                        yield str(ret)
                else:
                    exec(expression, namespace)
                yield next(iterator)

        previous = getattr(contexts, "current", v_nothing)
        contexts.current = v_evalcontext() if self._context is None else self._context
        try:
            namespace = self._functions.copy()
            namespace.update({name: shadow(value, "_value") for name, value in self._context._variables.items()})
            namespace.update({vtype.__module__.rsplit('.')[2]: vtype for vtype in (integer, double, string, boolean, date)})
            return string(u"".join(generate()))
        finally:
            contexts.current = previous
