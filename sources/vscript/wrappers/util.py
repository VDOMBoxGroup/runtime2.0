
from ..subtypes import array, boolean, date, double, empty, binary, integer, \
    nothing, null, string, v_empty, dictionary, v_nothing
from ..primitives import primitive
from ..subtypes.date import decode_date, encode_date
from .. import errors
from datetime import datetime
from types import FunctionType, MethodType, BuiltinFunctionType


class Nothing(object):

    __instance = None

    def __new__(cls, *args, **kwargs):
        if Nothing.__instance is None:
            Nothing.__instance = object.__new__(cls, *args, **kwargs)
        return Nothing.__instance

    def __bool__(self):
        return False


nothing_inst = Nothing()


def unknowntype(value):
    return value


def method_type(method):
    raise errors.object_has_no_property(method.__name__)


unwrappers = {
    null: lambda value: None,
    empty: lambda value: None,
    nothing: lambda value: None,
    integer: lambda value: value.as_integer,
    double: lambda value: value.as_double,
    string: lambda value: value.as_string,
    boolean: lambda value: value.as_boolean,
    date: lambda value: datetime(*decode_date(value)),
    array: lambda value: unwrapp_array(value),
    dictionary: lambda value: unwrapp_dictionary(value),
    binary: lambda value: value.as_binary
}

wrappers = {
    int: lambda value: integer(value),
    float: lambda value: double(value),
    str: lambda value: string(value),
    type(None): lambda value: v_empty,
    Nothing: lambda value: v_nothing,
    list: lambda value: wrapp_array(value),
    tuple: lambda value: wrapp_array(value),
    dict: lambda value: wrapp_dict(value),
    bool: lambda value: boolean(value),
    FunctionType: lambda value: method_type(value),
    MethodType: lambda value: method_type(value),
    BuiltinFunctionType: lambda value: method_type(value),
    datetime: lambda value: date(encode_date(*list(value.timetuple())[:6])),
}


def safe_as_complex(arg):
    try:
        return arg.as_complex
    except (errors.object_required, AttributeError):
        return None

def unwrapp(arg):
    obj = arg if not isinstance(arg, primitive) else safe_as_complex(arg) or arg.as_simple
    return unwrappers.get(type(obj), unknowntype)(obj)


def unwrapp_array(args):
    return [unwrapp(arg) for arg in args]


def unwrapp_dictionary(args):
    return dict([(unwrapp(key), unwrapp(args(key))) for key in args])


def unwrapp_kwargs(kwargs):
    return {key: unwrapp(value) for key, value in kwargs.items()}


def wrapp(arg):
    return wrappers.get(type(arg), unknowntype)(arg)


def wrapp_array(args):
    return array([wrapp(arg) for arg in args])


def wrapp_dict(args):
    return dictionary({wrapp(key): wrapp(value) for key, value in args.items()})


def convert(method, args, single=False):

    if method == unwrapp_kwargs:
        return method(args)

    if single:
        args = (args, )
    result = method(args)

    if not single:
        return result
    elif type(result) is list:
        return result[0]
    else:
        return result(integer(0))


def convert_input_args(args):
    return convert(unwrapp_array, args)


def convert_input_kwargs(kwargs):
    return convert(unwrapp_kwargs, kwargs)


def convert_output_arg(arg):
    return convert(wrapp_array, arg, True)


def AutoCast(method):
    def wrapper(*args, **kwargs):
        return convert_output_arg(method(*convert_input_args(args),
                                         **convert_input_kwargs(kwargs)))
    return wrapper


#######################################
# Cached Property Class
#######################################
class CachedProperty(object):
    def __init__(self, func, autocast=False):
        self.auto_cast = autocast
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = \
            convert_output_arg(self.func(instance)) if self.auto_cast \
            else self.func(instance)

        return result


def AutoCastCachedProperty(func):
    return CachedProperty(func, True)


#######################################
# VScript decorators
#######################################
def v_PropertySimple(func):
    def wrapper(*args, **kwargs):
        if "let" in kwargs:
            return func(value=kwargs["let"], retVal=False, *args)
        elif "set" in kwargs:
            raise errors.object_has_no_property(func.__name__)
        else:
            return func(value=None, retVal=True, *args)
    return wrapper


def v_PropertyComplex(func):
    def wrapper(*args, **kwargs):
        if "set" in kwargs:
            return func(value=kwargs["set"], retVal=False, *args)
        elif "let" in kwargs:
            raise errors.object_has_no_property(func.__name__)
        else:
            return func(value=None, retVal=True, *args)
    return wrapper


def v_PropertyReadOnly(func):
    def wrapper(*args, **kwargs):
        if "let" in kwargs or "set" in kwargs:
            raise errors.object_has_no_property(func.__name__)
        return func(*args, **kwargs)
    return wrapper


#######################################
# Help functions
#######################################
def is_string(value):
    return isinstance(value, str)


def is_byte_string(value):
    return isinstance(value, bytes)


def is_unicode_string(value):
    return isinstance(value, str)


def is_array(value):
    return isinstance(value, (list, tuple))


def is_dict(value):
    return isinstance(value, dict)


def encodeUTF8(value):
    return value.encode("utf8")


def decodeUTF8(value):
    return value.decode("utf8")


# Enums
def enum(*sequential, **named):
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    enums["enums"] = enums
    return type('Enum', (), enums)
