from ..primitives import variable
from ..subtypes import v_empty


class permanent(variable):

    def __init__(self, value=v_empty):
        self._value = value

    def __call__(self, *arguments, **keywords):
        if "let" in keywords:
            return self._value(*arguments, **keywords)
        elif "set" in keywords:
            return self._value(*arguments, **keywords)
        else:
            return self._value(*arguments, **keywords)

    subtype = property(lambda self: self._value.subtype)
    copy = property(lambda self: self._value.copy)
    exception = property(lambda self: self._value.exception)
    value = property(lambda self: self._value.value)

    def __repr__(self):
        return "INVARIABLE@%08X:%s" % (id(self), repr(self._value))
