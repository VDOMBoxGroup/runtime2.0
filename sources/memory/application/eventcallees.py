
from builtins import str
import sys
if sys.version_info[0] < 3:
    from collections import MutableSequence
else:
    from collections.abc import MutableSequence
from uuid import uuid4
from utils.properties import lazy, weak, constant, roproperty
from ..generic import MemoryBase
from .binding import MemoryBindingSketch, MemoryBindingRestorationSketch


EMPTY_LIST = []


@weak("_owner")
class MemoryEventCalleesSketch(MemoryBase, MutableSequence):

    is_callees = constant(True)

    @lazy
    def _items(self):
        return []

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")

    def on_complete(self, item, restore):
        self._items.append(item)

    def new_sketch(self, target_object, name, parameters=None, restore=False):
        return (MemoryBindingRestorationSketch if restore
            else MemoryBindingSketch)(self, target_object, name, parameters=parameters)

    def insert(self, index, callee):
        self._items.insert(index, callee)

    def __getitem__(self, index):
        return self.__dict__.get("_items", EMPTY_LIST)[index]

    def __setitem__(self, index, callee):
        self._items[index] = callee

    def __delitem__(self, index):
        del self.__dict__.get("_items", EMPTY_LIST)[index]

    def __len__(self):
        return len(self.__dict__.get("_items", EMPTY_LIST))

    def __invert__(self):
        self.__class__ = MemoryEventCallees
        return self

    def __str__(self):
        return "callees sketch of %s" % self._owner


class MemoryEventCallees(MemoryEventCalleesSketch):

    def new(self, target_object, name, parameters=None):
        item = self.new_sketch(target_object, name, parameters=parameters)
        item.id = str(uuid4())
        return ~item

    def insert(self, index, callee):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).insert(index, callee)
            if not callee.target_object.virtual:
                self._owner.owner.autosave()

    def __setitem__(self, index, callee):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).__setitem__(index, callee)
            if not callee.target_object.virtual:
                self._owner.owner.autosave()

    def __delitem__(self, index):
        with self._owner.owner.lock:
            item = self.__dict__.get("_items", EMPTY_LIST).pop(index)
            if not item.target_object.virtual:
                self._owner.owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return "callees of %s" % self._owner
