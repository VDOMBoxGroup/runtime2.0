
from ..primitives import subtype


class mismatch(subtype):

    code = property(lambda self: 9999)
    name = property(lambda self: "Mismatch")

    as_simple = property(lambda self: self)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo={}):
        return self

    def __repr__(self):
        return "MISMATCH@%08X" % id(self)


v_mismatch = mismatch()
