
import types
from .. import errors
from ..subtypes import generic
from ..conversions import pack, unpack


def wrap(value):
    return pack(value)


class wrapper(generic):

    def __init__(self, object=None):
        self._object = object

    def __getattr__(self, name):
        # entity=self._object.__class__.__dict__[name]
        try:
            entity = getattr(self._object.__class__, name)
        except KeyError:
            raise errors.object_has_no_property(name)

        def invoke(*arguments, **keywords):
            if isinstance(entity, property):
                try:
                    setattr(self._object, name, unpack(
                        keywords["get"].as_simple))
                except KeyError:
                    try:
                        setattr(self._object, name,
                                keywords["set"].as_specific(wrapper)._object)
                    except KeyError:
                        return wrap(getattr(self._object, name))
            elif isinstance(entity, types.FunctionType):
                if keywords:
                    raise errors.illegal_assigment
                arguments = (arguments[0],) + (unpack(argument) for argument in arguments[1:])

        return invoke
