
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
        for name, value in keywords.iteritems():
            setattr(function, name, value)
        return function

    return wrapper
