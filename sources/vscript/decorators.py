

import types
from . import errors
from .subtypes import binary, boolean, double, generic, integer, string, v_mismatch
from .conversions import pack, unpack


__all__ = ["auto", "native", "ignore", "vclass",
           "vfunction", "vsub", "vproperty", "vcollection"]


class auto(object):
    pass


class native(object):
    pass


class ignore(object):
    pass


wrappers = {
    auto: pack,
    ignore: lambda value: value,
    native: lambda value: value,
    generic: lambda value: value,
    integer: lambda value: integer(int(value)),
    string: lambda value: string(str(value)),
    binary: lambda value: binary(value if isinstance(value, bytes) else str(value)),
    boolean: lambda value: boolean(bool(value)),
    double: lambda value: double(float(value))}

unwrappers = {
    auto: unpack,
    ignore: lambda value: value,
    native: lambda value: value.as_is,
    generic: lambda value: value.as_generic,
    integer: lambda value: value.as_integer,
    string: lambda value: value.as_string,
    binary: lambda value: value.as_binary,
    boolean: lambda value: value.as_boolean,
    double: lambda value: value.as_double}


def unwrap(*arguments):
    handlers = tuple((argument, unwrappers[argument])
                     for argument in arguments)

    def unwrapper(value):
        for subtype, handler in handlers:
            if isinstance(value.subtype, subtype):
                return handler(value)
        else:
            raise errors.type_mismatch
    return unwrapper


def get_function_wrapper(arguments, result, function):
    if not isinstance(function, (types.FunctionType, types.MethodType)):
        raise errors.python("Require function to decorate")
    maximal = function.__code__.co_argcount
    varnames = function.__code__.co_varnames
    leading = 1 if varnames and varnames[0] == "self" else 0
    if len(arguments) + leading - maximal:
        raise errors.python("Incorrect number of arguments")
    try:
        handlers = tuple(unwrap(*argument) if isinstance(argument, tuple) else unwrappers[argument]
                         for argument in arguments)
        controller = wrappers[result] if result else None
    except KeyError:
        raise errors.python("Incorrect argument value")
    if leading:
        if getattr(function, "__self__", None) is None:  # VAILS: Py3 (ex-`im_self`)
            handlers = (lambda self: self,) + handlers
        else:
            maximal -= 1
    defaults = function.__defaults__
    minimal = maximal - (len(defaults) if defaults else 0)

    def wrapper(*arguments, **keywords):
        if keywords:
            raise errors.type_mismatch
        if not minimal <= len(arguments) <= maximal:
            raise errors.wrong_number_of_arguments(function.__name__)
        arguments = tuple(handler(argument)
                          for handler, argument in zip(handlers, arguments))
        result = function(*arguments)
        return controller(result) if controller else v_mismatch
    return wrapper


def get_property_wrapper(arguments, result, getter, letter, setter):
    if letter and result is generic:
        raise errors.python("Value must not be generic when letter")
    if letter and setter and result is not native:
        raise errors.python("Value must be native when letter and setter")
    if setter and result is not generic:
        raise errors.python("Value must be generic when setter")
    getter = get_function_wrapper(
        arguments, result, getter) if getter else None
    letter = get_function_wrapper(
        arguments + (result,), None, letter) if letter else None
    setter = get_function_wrapper(
        arguments + (result,), None, setter) if setter else None

    def wrapper(*arguments, **keywords):
        if "let" in keywords:
            if letter:
                letter(*(arguments + (keywords["let"],)))
            else:
                raise errors.object_has_no_property
        elif "set" in keywords:
            if setter:
                setter(*(arguments + (keywords["set"],)))
            else:
                raise errors.object_has_no_property
        else:
            if getter:
                return getter(*arguments)
            else:
                raise errors.object_has_no_property
    return wrapper


def get_collection_wrapper(arguments, result, master, getter, letter, setter):
    if letter and result is generic:
        raise errors.python("Value must not be generic when letter")
    if letter and setter and result is not native:
        raise errors.python("Value must be native when letter and setter")
    if setter and result is not generic:
        raise errors.python("Value must be generic when setter")
    varnames = master.__code__.co_varnames
    leading = 1 if varnames and varnames[0] == "self" else 0
    if len(varnames) > leading:
        raise errors.python("Master section has incorrect number of arguments")
    try:
        controller = wrappers[result] if result else None
    except KeyError:
        raise errors.python("Incorrect argument value")
    getter = get_function_wrapper(
        arguments, result, getter) if getter else None
    letter = get_function_wrapper(
        arguments + (result,), None, letter) if letter else None
    setter = get_function_wrapper(
        arguments + (result,), None, setter) if setter else None

    class collection(generic):
        def __init__(self, instance, wrapper):
            self._instance = instance
            self._wrapper = wrapper

        def __call__(self, *arguments, **keywords):
            return self._wrapper(self._instance, *arguments, get=1, **keywords)

        def __iter__(self):
            for item in master(self._instance):
                yield controller(item)

    class global_collection(generic):
        def __init__(self, wrapper):
            self._wrapper = wrapper

        def __call__(self, *arguments, **keywords):
            return self._wrapper(*arguments, get=1, **keywords)

        def __iter__(self):
            for item in master():
                yield controller(item)

    def wrapper(*arguments, **keywords):
        let, set = keywords.get("let"), keywords.get("set")
        if let is not None:
            if letter:
                return letter(*(arguments + (let,)))
            else:
                raise errors.object_has_no_property
        elif set is not None:
            if setter:
                return setter(*(arguments + (set,)))
            else:
                raise errors.object_has_no_property
        else:
            if len(arguments) > leading or keywords.get("get"):
                if getter:
                    return getter(*arguments)
                else:
                    raise errors.object_has_no_property
            else:
                return collection(arguments[0], wrapper) if leading \
                    else global_collection(wrapper)
    return wrapper


def vclass(cls):
    if not isinstance(cls, type):
        raise errors.python("Require class as argument")
    vclass = type(cls.__name__,
                  (generic, ) + tuple(ancestor for ancestor in cls.__bases__ if ancestor is not object),
                  cls.__dict__.copy())
    return vclass


def vfunction(*arguments, **keywords):
    result = keywords.get("result")

    def decorator(function):
        return get_function_wrapper(arguments, result, function)
    if arguments and isinstance(arguments[0], types.FunctionType):
        if not result:
            raise errors.python("Incorrect number of arguments")
        return get_function_wrapper((), result, arguments[0])
    else:
        if not result:
            if not arguments:
                raise errors.python("Incorrect number of arguments")
            arguments, result = arguments[:-1], arguments[-1]
        return decorator


def vsub(*arguments, **keywords):
    if "result" in keywords:
        raise errors.python("Incorrect number of arguments")

    def decorator(function):
        return get_function_wrapper(arguments, None, function)
    if arguments and isinstance(arguments[0], types.FunctionType):
        return get_function_wrapper((), None, arguments[0])
    else:
        return decorator


def vproperty(*arguments, **keywords):
    result = keywords.get("result")

    def decorator(cls):
        if isinstance(cls, type):
            getter = cls.__dict__.get("get")
            letter = cls.__dict__.get("let")
            setter = cls.__dict__.get("set")
        else:
            raise errors.python("Require class or funciton to decorate")
        if not (getter or letter or setter):
            raise errors.python("Require getter, letter or setter")
        return get_property_wrapper(arguments, result, getter, letter, setter)
    if arguments and isinstance(arguments[0], type) and result:
        if not result:
            raise errors.python("Incorrect number of arguments")
        return decorator(arguments[0])
    else:
        if not result:
            if not arguments:
                raise errors.python("Incorrect number of arguments")
            arguments, result = arguments[:-1], arguments[-1]
        getter = keywords.get("getter")
        letter = keywords.get("letter")
        setter = keywords.get("setter")
        if getter or letter or setter:
            return get_property_wrapper(arguments, result, getter, letter, setter)
        else:
            return decorator


def vcollection(*arguments, **keywords):
    result = keywords.get("result")

    def decorator(cls):
        if isinstance(cls, type):
            master = cls.__dict__.get("all")
            getter = cls.__dict__.get("get")
            letter = cls.__dict__.get("let")
            setter = cls.__dict__.get("set")
        else:
            raise errors.python("Require class or funciton to decorate")
        if not master or not (getter or letter or setter):
            raise errors.python("Require getter, letter or setter")
        return get_collection_wrapper(arguments, result, master, getter, letter, setter)
    if arguments and isinstance(arguments[0], type):
        if not result:
            raise errors.python("Incorrect number of arguments")
        return decorator(arguments[0])
    else:
        if not result:
            if not arguments:
                raise errors.python("Incorrect number of arguments")
            arguments, result = arguments[:-1], arguments[-1]
        master = keywords.get("master")
        getter = keywords.get("getter")
        letter = keywords.get("letter")
        setter = keywords.get("setter")
        if master and (getter or letter or setter):
            return get_collection_wrapper(arguments, result, master, getter, letter, setter)
        else:
            return decorator
