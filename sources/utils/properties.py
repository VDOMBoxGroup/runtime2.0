
from builtins import object
from weakref import ref
from threading import RLock


MISSING = "MISSING"
WEAK_NAME_TEMPLATE = "_weak_%s"


class AbstractReadOnlyProperty(object):

    def __get__(self, instance, owner=None):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise AttributeError

    def __delete__(self, instance):
        raise AttributeError


class AbstractReadWriteProperty(object):

    def __get__(self, instance, owner=None):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def __delete__(self, instance):
        raise AttributeError


class ConstantProperty(object):

    def __init__(self, value):
        self._value = value

    def __get__(self, instance, owner=None):
        return self._value

    def __set__(self, instance, value):
        raise AttributeError

    def __delete__(self, instance):
        raise AttributeError


class LazyProperty(object):

    def __init__(self, initializer):
        self._initializer = initializer
        self._name = initializer.__name__
        self._lock = RLock()

    def __get__(self, instance, owner=None):
        with self._lock:
            value = instance.__dict__.get(self._name, MISSING)
            if value is MISSING:
                instance.__dict__[self._name] = value = self._initializer(instance)
            return value


class WeakProperty(object):

    def __init__(self, name):
        self._name = name

    def __get__(self, instance, owner=None):
        try:
            value = instance.__dict__[self._name]
        except KeyError:
            raise AttributeError(self._name)
        else:
            return None if value is None else value()

    def __set__(self, instance, value):
        instance.__dict__[self._name] = None if value is None else ref(value)

    def __delete__(self, instance):
        del instance.__dict__[self._name]


class WeakWithDefaultProperty(object):

    def __init__(self, name, default):
        self._name = name
        self._default = default

    def __get__(self, instance, owner=None):
        value = instance.__dict__.get(self._name, self._default)
        return None if value is None else value()

    def __set__(self, instance, value):
        instance.__dict__[self._name] = None if value is None else ref(value)

    def __delete__(self, instance):
        del instance.__dict__[self._name]


aroproperty = AbstractReadOnlyProperty
arwproperty = AbstractReadWriteProperty

# lazy = LazyProperty
constant = ConstantProperty

lazyproperties = {}
weakproperties = {}
readonly_properties = {}
readwrite_properties = {}


def quicker_constant(value):

    class ConstantProperty(object):

        def __get__(self, instance, owner=None):
            return value

        def __set__(self, instance, value):
            raise AttributeError

        def __delete__(self, instance):
            raise AttributeError

    return ConstantProperty()


def quicker_lazy(initializer):
    name = initializer.__name__
    lock = RLock()

    class LazyProperty(object):

        def __get__(self, instance, owner=None):
            with lock:
                try:
                    return instance.__dict__[name]
                except KeyError:
                    return instance.__dict__.setdefault(name, initializer(instance))

    return LazyProperty()


def weakproperty(name):
    if name in weakproperties:
        return weakproperties[name]()
    else:
        namespace = {"ref": ref}
        bytecode = compile("""
class WeakProperty(object):

    def __get__(self, instance, owner=None):
        value = instance.{name}
        return None if value is None else value()

    def __set__(self, instance, value):
        instance.{name} = None if value is None else ref(value)

    def __delete__(self, instance):
        del instance.{name}
            """.format(name=name), "<weakproperty:%s>" % name, "exec")

        exec(bytecode, namespace)
        return weakproperties.setdefault(name, namespace["WeakProperty"])()


def weak(*names, **names_with_values):

    def wrapper(cls):
        for name in names:
            setattr(cls, name, weakproperty(WEAK_NAME_TEMPLATE % name))
        for name, value in names_with_values.items():
            weak_name = WEAK_NAME_TEMPLATE % name
            setattr(cls, weak_name, ref(value))
            setattr(cls, name, weakproperty(weak_name))
        return cls

    return wrapper


def lazyproperty(name, initializer, lock=None, exclusive=True):
    try:
        return lazyproperties[name]()
    except KeyError:
        namespace = {"MISSING": MISSING, "initializer": initializer}
        if lock:
            lock = "instance." + lock
        else:
            namespace["lock"] = RLock()
            lock = "lock"
        if exclusive:
            bytecode = compile("""
    class LazyProperty(object):

    def __get__(self, instance, owner=None):
        with {lock}:
            value = instance.__dict__.get("{name}", MISSING)
            if value is MISSING:
                instance.__dict__["{name}"] = value = initializer(instance)
            return value
                """.format(name=name, lock=lock), "<lazyproperty:%s>" % name, "exec")
        else:
            bytecode = compile("""
    class LazyProperty(object):

    def __get__(self, instance, owner=None):
        with {lock}:
            return instance.__dict__.get("{name}", initializer(instance))
                """.format(name=name, lock=lock), "<lazyproperty:%s>" % name, "exec")

        exec(bytecode, namespace)
        return lazyproperties.setdefault(name, namespace["LazyProperty"])()


def lazy(initializer=None, lock=None):
    if lock:

        def wrapper(initializer):
            return lazyproperty(initializer.__name__, initializer, lock)

        return wrapper
    else:
        return LazyProperty(initializer)


def roproperty(name):
    if name in readonly_properties:
        return readonly_properties[name]()
    else:
        namespace = {}
        bytecode = compile("""
class ReadOnlyProperty(object):

    __module__ = "utils"

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        if instance.{name} is not value:  # hack to allow in-place operators
            raise AttributeError("{name}")

    def __delete__(self, instance):
        raise AttributeError
            """.format(name=name), "<roproperty:%s>" % name, "exec")

        exec(bytecode, namespace)
        return readonly_properties.setdefault(name, namespace["ReadOnlyProperty"])()


def rwproperty(name, setter=None):
    if (name, setter) in readwrite_properties:
        return readwrite_properties[name, setter]()
    else:
        if setter is None:
            namespace = {}
            assigment = "instance.%s = value" % name
        else:
            namespace = {"setter": setter}
            assigment = "setter(instance, value)"

        bytecode = compile("""
class ReadWriteProperty(object):

    __module__ = "utils"

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        {assigment}

    def __delete__(self, instance):
        raise AttributeError
            """.format(name=name, assigment=assigment),
            "<rwproperty:%s%s>" % (name, (":setter" if setter else "")), "exec")

        exec(bytecode, namespace)
        return readwrite_properties.setdefault((name, setter), namespace["ReadWriteProperty"])()
