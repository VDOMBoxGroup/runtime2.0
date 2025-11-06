import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from utils.exception import VDOMSecurityError
from utils.properties import lazy, weak, roproperty, rwproperty
from ..generic import MemoryBase
from .structurelevel import MemoryStructureLevel, MemoryStructureLevelSketch


@weak("_owner")
class MemoryStructureSketch(MemoryBase, Mapping):

    @lazy
    def _items(self):
        return {}

    _resource = None
    _top = 0
    _left = 0
    _state = 0

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")
    resource = rwproperty("_resource")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")

    def __invert__(self):
        if "_items" in self.__dict__:
            for item in self._items.values():
                ~item
        self.__class__ = MemoryStructure
        return self

    def __getitem__(self, name):
        try:
            return self._items[name]
        except KeyError:
            return self._items.setdefault(name, MemoryStructureLevelSketch(self, name))

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "structure sketch of %s" % self._owner


class MemoryStructure(MemoryStructureSketch):

    def _set_resource(self, value):
        if self._resource == value:
            return

        self._resource = value
        self._owner.autosave()

    def _set_top(self, value):
        if self._top == value:
            return

        self._top = value
        self._owner.autosave()

    def _set_left(self, value):
        if self._left == value:
            return

        self._left = value
        self._owner.autosave()

    def _set_state(self, value):
        if self._state == value:
            return

        self._state = value
        self._owner.autosave()

    resource = rwproperty("_resource", _set_resource)
    top = rwproperty("_top", _set_top)
    left = rwproperty("_left", _set_left)
    state = rwproperty("_state", _set_state)

    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\"%s Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._owner.id, u" ResourceID=\"%s\"" % self._resource if self._resource else u"",
                self._top, self._left, self._state)
        if self.__dict__.get("_items"):
            file.write(u"%s<Object %s>\n" % (ident, information))
            for item in self._items.values():
                item.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Object>\n" % ident)
        else:
            file.write(u"%s<Object %s/>\n" % (ident, information))

    def __getitem__(self, key):
        with self._owner.lock:
            try:
                return self._items[key]
            except KeyError:
                return self._items.setdefault(key, MemoryStructureLevel(self, key))

    def __str__(self):
        return "structure of %s" % self._owner
