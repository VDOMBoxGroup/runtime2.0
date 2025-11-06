
from weakref import ref
from functools import wraps


def verificator(function):

    def check(value):
        try:
            function(value)
        except ValueError:
            return False
        else:
            return True

    function.check = check
    return function


def cache_by_argument(function):
    cache = {}

    @wraps(function)
    def wrapper(key):
        try:
            return cache[key]
        except KeyError:
            return cache.setdefault(key, function(key))

    return wrapper


def attributes(**keywords):

    def wrapper(function):
        for name, value in keywords.items():
            setattr(function, name, value)
        return function

    return wrapper


def weaker(bound):
    instance, function = ref(bound.__self__), bound.__func__

    @wraps(function)
    def wrapper(*attributes, **keywords):
        return function(instance(), *attributes, **keywords)

    return wrapper
