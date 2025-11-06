
from utils.properties import weak, constant, roproperty, rwproperty
from ..generic import MemoryBase
from .eventcallees import MemoryEventCalleesSketch


@weak("_collection")
class MemoryEventSketch(MemoryBase):

    is_event = constant(True)

    _restore = False

    _top = 0
    _left = 0
    _state = False

    def __init__(self, collection, name):
        self._collection = collection
        self._name = name
        self._callees = MemoryEventCalleesSketch(self)

    owner = source_object = property(lambda self: self._collection.owner)
    container = property(lambda self: self._collection.owner.container)
    key = property(lambda self: (self._collection.owner.id, self._name))

    name = rwproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    callees = roproperty("_callees")

    def __invert__(self):
        ~self._callees
        restore = self._restore
        self.__class__ = MemoryEvent
        self._collection.on_complete(self, restore)
        if not restore:
            self._collection.owner.autosave()
        return self

    def __str__(self):
        return " ".join([_f for _f in (
            "event",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._collection.owner) if _f])


class MemoryEventRestorationSketch(MemoryEventSketch):

    _restore = True


class MemoryEvent(MemoryEventSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new event")

    def _set_name(self, value):
        self._name = value
        self._collection.owner.autosave()

    def _set_top(self, value):
        self._top = value
        self._collection.owner.autosave()

    def _set_left(self, value):
        self._left = value
        self._collection.owner.autosave()

    def _set_state(self, value):
        self._state = value
        self._collection.owner.autosave()

    name = rwproperty("_name", _set_name)
    top = rwproperty("_top", _set_top)
    left = rwproperty("_left", _set_left)
    state = rwproperty("_state", _set_state)

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ContainerID=\"%s\" ObjSrcID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._collection.owner.container.id, self._collection.owner.id, self._name, self._top, self._left, self._state)
        if self._callees:
            file.write(u"%s<Event %s>\n" % (ident, information))
            for callee in self._callees:
                file.write(u"%s\t<Action ID=\"%s\"/>\n" % (ident, callee.id))
            file.write(u"%s</Event>\n" % ident)
        else:
            file.write(u"%s<Event %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in (
            "event",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._collection.owner) if _f])
