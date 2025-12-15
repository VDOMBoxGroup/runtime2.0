
from ..primitives import subtype


class binary(subtype):

    def __init__(self, value):
        self._value = value

    value = property(lambda self: self._value)

    code = property(lambda self: 19)
    name = property(lambda self: "Binary")

    as_simple = property(lambda self: self)
    as_binary = property(lambda self: self._value)

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return "BINARY@%08X" % id(self)
