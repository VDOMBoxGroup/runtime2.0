
from .. import errors
from .generic import generic


class nothing(generic):

    def __call__(self, *arguments, **keywords):
        raise errors.object_variable_not_set

    name = property(lambda self: "Nothing")

    is_nothing = property(lambda self: self is v_nothing)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo={}):
        return self

    def __repr__(self):
        return "NOTHING@%08X" % id(self)


v_nothing = nothing()
