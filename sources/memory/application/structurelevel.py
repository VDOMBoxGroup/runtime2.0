import codecs
import sys
if sys.version_info[0] < 3:
    from collections import MutableSequence
else:
    from collections.abc import MutableSequence
from utils.properties import lazy, weak, roproperty, rwproperty
from ..generic import MemoryBase


EMPTY_LIST = []


@weak("_owner")
class MemoryStructureLevelSketch(MemoryBase, MutableSequence):

    @lazy
    def _items(self):
        return []

    def __init__(self, owner, name):
        self._owner = owner
        self._name = name

    owner = roproperty("_owner")
    name = rwproperty("_name")

    def insert(self, index, item):
        self._items.insert(index, item)

    def __getitem__(self, index):
        return self.__dict__.get("_items", EMPTY_LIST)[index]

    def __setitem__(self, index, item):
        self._items[index] = item

    def __delitem__(self, index):
        del self.__dict__.get("_items", EMPTY_LIST)[index]

    def __len__(self):
        return len(self.__dict__.get("_items", EMPTY_LIST))

    def __invert__(self):
        self.__class__ = MemoryStructureLevel
        return self

    def __str__(self):
        return " ".join([_f for _f in (
            "structure level",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._owner) if _f])


class MemoryStructureLevel(MemoryStructureLevelSketch):

    def _set_name(self, value):
        self._name = value
        self._owner.owner.autosave()

    name = rwproperty("_name", _set_name)

    def compose(self, ident=u"", file=None):
        items = self.__dict__.get("_items")
        attributes = u" Name=\"%s\"" % codecs.encode(self._name, "xml")
        if items:
            file.write(u"%s<Level%s>\n" % (ident, attributes))
            for item in items:
                file.write(u"%s\t<Object ID=\"%s\"/>\n" % (ident, item.id))
            file.write(u"%s</Level>\n" % ident)
        # else:
        #     file.write(u"%s<Level%s/>\n" % (ident, attributes))

    def insert(self, index, item):
        with self._owner.owner.lock:
            self._items.insert(index, item)
            self._owner.owner.autosave()

    def __setitem__(self, index, item):
        with self._owner.owner.lock:
            self._items[index] = item
            self._owner.owner.autosave()

    def __delitem__(self, index):
        with self._owner.owner.lock:
            del self.__dict__.get("_items", EMPTY_LIST)[index]
            self._owner.owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in (
            "structure level",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._owner) if _f])
