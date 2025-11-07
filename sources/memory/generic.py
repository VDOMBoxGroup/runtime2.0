
from utils.properties import constant


class MemoryBase(object):

    is_type = constant(False)
    is_application = constant(False)
    is_object = constant(False)
    is_library = constant(False)

    is_action = constant(False)
    is_binding = constant(False)
    is_event = constant(False)
    is_callees = constant(False)

    def __invert__(self):
        raise NotImplementedError

    def __repr__(self):
        return "<memory %s at 0x%08X>" % (self, id(self))

    def __describe__(self):
        return "memory " + str(self)
