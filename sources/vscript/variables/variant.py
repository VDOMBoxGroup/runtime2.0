from ..primitives import variable
from ..subtypes import v_empty


class variant(variable):

    def __init__(self, value=v_empty):
        self._value = value

    def __call__(self, *arguments, **keywords):
        if "let" in keywords:
            if arguments:
                return self._value(*arguments, **keywords)
            else:
                self._value = keywords["let"].as_simple
        elif "set" in keywords:
            if arguments:
                return self._value(*arguments, **keywords)
            else:
                self._value = keywords["set"].as_complex
        else:
            return self._value(*arguments, **keywords)

    subtype = property(lambda self: self._value.subtype)
    copy = property(lambda self: self._value.copy)
    exception = property(lambda self: self._value.exception)
    value = property(lambda self: self._value.value)

    def __repr__(self):
        return "VARIANT@%08X:%s" % (id(self), repr(self._value))
