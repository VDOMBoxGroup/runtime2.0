import codecs

from utils.properties import weak, constant, roproperty, rwproperty
from ..generic import MemoryBase
from .bindingparameters import MemoryBindingParameters


@weak("_collection")
class MemoryBindingSketch(MemoryBase):

    is_binding = constant(True)

    _restore = False

    _id = None
    _top = 0
    _left = 0
    _state = False

    def __init__(self, collection, target_object, name, parameters=None):
        self._collection = collection  # MemoryBindings or MemoryEventCallees
        self._target_object = target_object
        self._name = name
        self._parameters = MemoryBindingParameters(self, parameters)

    owner = property(lambda self: self._collection.owner)

    id = rwproperty("_id")
    target_object = roproperty("_target_object")
    name = roproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    parameters = roproperty("_parameters")

    def __invert__(self):
        restore = self._restore
        self.__class__ = MemoryBinding
        self._collection.on_complete(self, restore)
        if not restore:
            owner = self._collection.owner
            if owner.is_event:
                owner = owner.owner
            owner.invalidate(upward=True)
            if not self._target_object.virtual:
                owner.autosave()
        return self

    def __str__(self):
        return " ".join([_f for _f in (
            "binding",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._target_object) if _f])


class MemoryBindingRestorationSketch(MemoryBindingSketch):

    _restore = True


class MemoryBinding(MemoryBindingSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new binding")

    def _set_top(self, value):
        self._top = value
        self._target_object.autosave()

    def _set_left(self, value):
        self._left = value
        self._target_object.autosave()

    def _set_state(self, value):
        self._state = value
        self._target_object.autosave()

    id = roproperty("_id")
    target_object = roproperty("_target_object")
    name = roproperty("_name")
    top = rwproperty("_top", _set_top)
    left = rwproperty("_left", _set_left)
    state = rwproperty("_state", _set_state)
    parameters = roproperty("_parameters")

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\" ObjTgtID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._id, self._target_object.id, self._name, self._top, self._left, self._state)
        if self._parameters:
            file.write(u"%s<Action %s>\n" % (ident, information))
            for name, value in self._parameters.items():
                file.write(u"%s\t<Parameter Name=\"%s\">%s</Parameter>\n" % (ident, name, codecs.encode(value, "xml")))
            file.write(u"%s</Action>\n" % ident)
        else:
            file.write(u"%s<Action %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in (
            "binding",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._target_object) if _f])
