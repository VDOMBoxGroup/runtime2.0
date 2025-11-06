
import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
    
from ...generic import MemoryBase
from .auxiliary import subtree, check_subtree


MISSING = "MISSING"


class MemoryEventsCatalog(MemoryBase, Mapping):

    def __init__(self, collection):
        self._collection = collection
        self._items = {}

    # unsafe
    def compose(self, ident=u"", file=None):
        if self._items:
            file.write(u"%s<Events>\n" % ident)
            for event in self._items.values():
                event.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Events>\n" % ident)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "events catalog of %s" % self._collection._owner


class MemoryEventsDynamicCatalog(MemoryBase, Mapping):

    def __init__(self, collection):
        self._collection = collection

    def __getitem__(self, key):
        item = self._collection.owner.application.events.catalog.get(key)
        if item and check_subtree(item.owner, self._collection.owner):
            return item
        else:
            KeyError(key)

    def __iter__(self):
        for subobject in subtree(self._collection.owner):
            for item in subobject.events.__dict__.get("_items", ()):
                yield item

    def __len__(self):
        return sum(len(subobject.events.__dict__.get("_items", ())) for subobject in subtree(self._collection.owner))

    def __str__(self):
        return "events dynamic catalog of %s" % self._collection._owner
