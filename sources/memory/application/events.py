
import sys
if sys.version_info[0] < 3:
    from collections import MutableMapping
else:
    from collections.abc import MutableMapping
from utils.properties import lazy, weak, roproperty
from ..generic import MemoryBase
from .catalogs import MemoryEventsCatalog, MemoryEventsDynamicCatalog
from .event import MemoryEventSketch, MemoryEventRestorationSketch


@weak("_owner")
class MemoryEvents(MemoryBase, MutableMapping):

    @lazy
    def _items(self):
        return {}

    @lazy
    def _all_items(self):
        return self._owner.application.events.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryEventsCatalog(self)
        else:
            return MemoryEventsDynamicCatalog(self)

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")

    def on_complete(self, item, restore):
        with self._owner.lock:
            self._items[item.source_object.id, item._name] = item
            if not self._owner.virtual:
                self._all_items[item.source_object.id, item._name] = item

    def new_sketch(self, name, restore=False):
        return (MemoryEventRestorationSketch if restore
            else MemoryEventSketch)(self, name)

    def new(self, name):
        item = self.new_sketch(name)
        return ~item

    def clear(self):
        with self._owner.lock:
            if not self._owner._virtual:
                for key in self._items:
                    del self._all_items[key]
            self._items.clear()
            self._owner.autosave()

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new event")

    def __delitem__(self, key):
        with self._owner.lock:
            if not self._owner._virtual:
                del self._all_items[key]
            del self._items[key]
            self._owner.autosave()

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "events of %s" % self._owner
