
from builtins import str
from builtins import object
import sys
if sys.version_info[0] < 3:
    from collections import MutableMapping
else:
    from collections.abc import MutableMapping
from uuid import uuid4

from utils.properties import lazy, weak, roproperty

from ..generic import MemoryBase
from ..naming import UniqueNameDictionary
from .catalogs import MemoryActionsCatalog, MemoryActionsDynamicCatalog
from .action import MemoryActionSketch, MemoryActionRestorationSketch, MemoryActionDuplicationSketch


NAME_BASE = "action"
EMPTY_DICTIONARY = {}


@weak("_owner")
class MemoryActions(MemoryBase, MutableMapping):

    class MemoryActionsItemsProperty(object):

        def __get__(self, instance, owner=None):
            with instance._owner.lock:
                instance.__dict__.setdefault("_items_by_name", UniqueNameDictionary())
                return instance.__dict__.setdefault("_items", {})

    class MemoryActionsItemsByNameProperty(object):

        def __get__(self, instance, owner=None):
            with instance._owner.lock:
                instance.__dict__.setdefault("_items", {})
                return instance.__dict__.setdefault("_items_by_name", UniqueNameDictionary())

    _items = MemoryActionsItemsProperty()
    _items_by_name = MemoryActionsItemsByNameProperty()

    @lazy
    def _all_items(self):
        return self._owner.application.actions.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryActionsCatalog(self)
        else:
            return MemoryActionsDynamicCatalog(self)

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")
    generic = roproperty("_generic")
    names = property(lambda self: self.__dict__.get("_items_by_name", EMPTY_DICTIONARY).key())

    def on_rename(self, item, name):
        with self._owner.lock:
            if name in self._items_by_name:
                raise KeyError
            self._items_by_name[name] = item
            del self._items_by_name[item._name]

    def on_complete(self, item, restore):
        with self._owner.lock:
            if item._id is None:
                item._id = str(uuid4())
            if item._name is None or item._name in self._items_by_name:
                item._name = self._items_by_name.generate(item._name, NAME_BASE)

            self._items[item._id] = item
            self._items_by_name[item._name] = item
            if not self._owner.virtual:
                self._all_items[item._id] = item

    def new_sketch(self, restore=False, handler=None):
        return (MemoryActionRestorationSketch if restore
            else MemoryActionSketch)(self, handler=handler)

    def new(self, name=None, source_code=None, handler=None):
        item = self.new_sketch(handler=handler)
        item.id = str(uuid4())
        item.name = name
        if source_code is not None:
            item.source_code = source_code
        return ~item

    # unsafe
    def compose(self, ident=u"", file=None):
        actions = tuple(action for action in self._items.values()
            if action.source_code or action.name not in self._owner.generic)
        if actions:
            file.write(u"%s<Actions>\n" % ident)
            for action in actions:
                action.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Actions>\n" % ident)

    def clear(self):
        if "_items" in self.__dict__:
            with self._owner.lock:
                contexts = set(self._items)
                contexts.update(self._items_by_name)

                if not self._owner.virtual:
                    for uuid in self._items:
                        del self._all_items[uuid]
                del self._items
                del self._items_by_name

                self._owner.invalidate(contexts=contexts, downward=True, upward=True)
                self._owner.autosave()

    def replicate(self, another):
        if isinstance(another, MemoryActionSketch):
            enumeration = another,
        elif isinstance(another, MemoryActions):
            if "_items" in another.__dict__:
                enumeration = iter(another._items.values())
            else:
                enumeration = ()
        else:
            raise ValueError("Action or actions collection required")

        with self._owner.lock:
            copy = None

            contexts = set()
            for item in enumeration:
                copy = MemoryActionDuplicationSketch(self, item)
                copy.id = str(uuid4())
                ~copy
                contexts.update({item.id, item.name})
            self._owner.invalidate(contexts=contexts, downward=True, upward=True)

        return copy

    def __getitem__(self, key):
        return self._items.get(key) or self._items_by_name[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new action")

    def __delitem__(self, key):
        with self._owner.lock:
            item = self._items.get(key) or self._items_by_name[key]

            del self._items[item.id]
            del self._items_by_name[item.name]
            if not self._owner.virtual:
                del self._all_items[item.id]

            self._owner.invalidate(contexts=(item.id, item.name), downward=True, upward=True)
            self._owner.autosave()

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "actions of %s" % self._owner
