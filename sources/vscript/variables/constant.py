
from .. import errors
from ..primitives import variable
from ..subtypes import v_empty


class constant(variable):

    def __init__(self, value=v_empty):
        self._value = value

    def __call__(self, *arguments, **keywords):
        if "let" in keywords:
            raise errors.illegal_assigment
        elif "set" in keywords:
            raise errors.illegal_assigment
        else:
            return self._value(*arguments, **keywords)

    subtype = property(lambda self: self._value.subtype)
    copy = property(lambda self: self._value.copy)
    exception = property(lambda self: self._value.exception)
    value = property(lambda self: self._value.value)

    def __repr__(self):
        return "CONSTANT@%08X:%s" % (id(self), repr(self._value))
