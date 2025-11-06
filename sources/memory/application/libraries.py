
from weakref import ref
import sys
if sys.version_info[0] < 3:
    from collections import MutableMapping
else:
    from collections.abc import MutableMapping

from utils.properties import lazy, weak, roproperty

from ..generic import MemoryBase
from ..naming import UniqueNameDictionary
from .library import MemoryLibrarySketch, MemoryLibraryRestorationSketch


NAME_BASE = "library"


@weak("_owner")
class MemoryLibraries(MemoryBase, MutableMapping):

    @lazy
    def _items(self):
        return UniqueNameDictionary()

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")

    def on_rename(self, item, name):
        with self._owner.lock:
            if name in self._items:
                raise KeyError
            self._items[name] = item
            del self._items[item._name]

    def on_complete(self, item, restore):
        with self._owner.lock:
            if item._name is None or item._name in self._items:
                item._name = self._items.generate(item._name, NAME_BASE)
            self._items[item._name] = item

    def new_sketch(self, restore=False):
        return (MemoryLibraryRestorationSketch if restore
            else MemoryLibrarySketch)(self)

    def new(self, name=None):
        item = self.new_sketch()
        item.name = name
        return ~item

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False):
        libraries = tuple(library for library in self._items.values())
        if libraries:
            file.write(u"%s<Libraries>\n" % ident)
            for library in libraries:
                library.compose(ident=ident + u"\t", file=file, shorter=shorter)
            file.write(u"%s</Libraries>\n" % ident)

    def clear(self):
        if "_items" in self.__dict__:
            with self._owner.lock:
                del self._items

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new library")

    def __delitem__(self, key):
        with self._owner.lock:
            item = self._items[key]
            item.cleanup(remove=True)
            del self._items[item.name]

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "libraries of %s" % self._owner
