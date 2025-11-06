
from builtins import next
import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from ...generic import MemoryBase
from .auxiliary import subtree, check_subtree


MISSING = "MISSING"


class MemoryObjectsCatalog(MemoryBase, Mapping):

    def __init__(self, collection):
        self._collection = collection
        self._items = {}

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "objects catalog of %s" % self._collection._owner


class MemoryObjectsDynamicCatalog(MemoryBase, Mapping):

    def __init__(self, collection):
        self._collection = collection

    def __getitem__(self, key):
        item = self._collection.owner.application.objects.catalog.get(key)
        if item and check_subtree(item.parent, self._collection.owner):
            return item
        else:
            KeyError(key)

    def __iter__(self):
        iterator = subtree(self._collection.owner)
        next(iterator)
        for subobject in iterator:
            yield subobject.id

    def __len__(self):
        return sum((1 for subobject in subtree(self._collection.owner)), -1)

    def __str__(self):
        return "objects dynamic catalog of %s" % self._collection._owner
