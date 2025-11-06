import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from utils.properties import weak, roproperty
from ..generic import MemoryBase
from .event import MemoryTypeEventSketch


@weak("_owner")
class MemoryTypeEvents(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._items = {}

    owner = roproperty("_owner")

    def on_complete(self, item):
        self._items[item.name] = item

    def new_sketch(self, restore=False):
        return MemoryTypeEventSketch(self)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "events of %s" % self._owner


class MemoryTypeUserInterfaceEvents(MemoryTypeEvents):

    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<UserInterfaceEvents>\n" % ident)
            for event in self._items.values():
                event.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</UserInterfaceEvents>\n" % ident)

    def __str__(self):
        return "user interface events of %s" % self._owner


class MemoryTypeObjectEvents(MemoryTypeEvents):

    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<ObjectEvents>\n" % ident)
            for event in self._items.values():
                event.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</ObjectEvents>\n" % ident)

    def __str__(self):
        return "object events of %s" % self._owner
