
from builtins import str
from builtins import object
from weakref import ref
from collections import OrderedDict
import sys
if sys.version_info[0] < 3:
    from collections import MutableMapping
else:
    from collections.abc import MutableMapping
from itertools import islice
from uuid import uuid4

import managers
import security

from utils.exception import VDOMSecurityError
from utils.properties import lazy, weak, roproperty

from ..generic import MemoryBase
from ..naming import UniqueNameDictionary
from .catalogs import MemoryObjectsCatalog, MemoryObjectsDynamicCatalog


EMPTY_DICTIONARY = {}


@weak("_owner")
class MemoryObjects(MemoryBase, MutableMapping):

    class MemoryObjectsItemsProperty(object):

        def __get__(self, instance, owner=None):
            with instance._owner.lock:
                instance.__dict__.setdefault("_items_by_name", UniqueNameDictionary())
                return instance.__dict__.setdefault("_items", OrderedDict())

    class MemoryObjectsItemsByNameProperty(object):

        def __get__(self, instance, owner=None):
            with instance._owner.lock:
                instance.__dict__.setdefault("_items", OrderedDict())
                return instance.__dict__.setdefault("_items_by_name", UniqueNameDictionary())

    _items = MemoryObjectsItemsProperty()
    _items_by_name = MemoryObjectsItemsByNameProperty()

    @lazy
    def _all_items(self):
        return self._owner.application.objects.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryObjectsCatalog(self)
        else:
            return MemoryObjectsDynamicCatalog(self)

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")
    names = property(lambda self: list(self.__dict__.get("_items_by_name", EMPTY_DICTIONARY).keys()))

    def on_rename(self, item, name):
        with self._owner.lock:
            if name in self._items_by_name:
                raise KeyError
            self._items_by_name[name] = item
            if item._original_name:
                del item._original_name
            del self._items_by_name[item._name]

    def on_complete(self, item, restore):
        with self._owner.lock:
            if item._id is None:
                item._id = str(uuid4())
            if item._name is None or item._name in self._items_by_name:
                if item._name is not None:
                    item._original_name = item._name
                item._name = self._items_by_name.generate(item._name, item._type.name)
            item._order = len(self._items)

            if item._virtual == self._owner.virtual:
                self._items[item._id] = item
                self._items_by_name[item._name] = item
                self._items_by_name[item._name.lower()] = item
                if not item._virtual:
                    self._all_items[item._id] = item
            else:
                try:
                    option = managers.session_manager.current
                except Exception:
                    option = None
                managers.memory.track(item, sync=option)

            if not restore:
                if self._owner.is_object and item._virtual == self._owner.virtual:
                    managers.dispatcher.dispatch_handler(self._owner, "on_insert", item)
                    managers.dispatcher.dispatch_handler(self._owner, "on_layout", item)

    def on_delete(self, item):
        with self._owner.lock:
            # dispatch events
            if self._owner.is_object and item.virtual == self._owner.virtual:
                managers.dispatcher.dispatch_handler(self._owner, "on_remove", item)
                managers.dispatcher.dispatch_handler(self._owner, "on_layout", item)
            managers.dispatcher.dispatch_handler(item, "on_delete")

            # delete all child objects
            item.objects.clear()

            # cleanup structure
            if self._owner.is_application and not item.virtual:
                for container in self._owner.objects.values():
                    if item is container:
                        continue
                    for level in container.structure.values():
                        if item in level:
                            level.remove(item)

            # remove events
            item.events.clear()
            bindings = tuple(binding for binding in item.container.bindings.catalog.values()
                if binding.target_object == item)
            for event in item.container.events.catalog.values():
                for binding in bindings:
                    while binding in event.callees:
                        event.callees.remove(binding)
            for binding in bindings:
                del binding.target_object.container.bindings[binding.id]

            # delete resources
            # NOTE: currently invalidate do this
            # managers.resource_manager.invalidate_resources(item.id)

            if item.virtual == self._owner.virtual:
                # recalculate order for following objects
                index = list(self._items.keys()).index(item.id)
                for another in islice(iter(self._items.values()), index + 1, None):
                    another._order -= 1

                # remove from dictionaries
                del self._items[item.id]
                del self._items_by_name[item.name]
                if not item.virtual:
                    del self._all_items[item.id]

            # delete source code and autosave
            item.invalidate(upward=True)
            item.autosave()

            # mark as obsolete to avoid further usage
            item.__class__ = MemoryObjectGhost

    def new_sketch(self, type, virtual=False, attributes=None, restore=False):
        return (MemoryObjectRestorationSketch if restore
                else MemoryObjectSketch)(self, type,
            self._owner.application, None if self._owner.is_application else self._owner,
            virtual=virtual or self._owner.virtual, attributes=attributes)

    def new(self, type, name=None, virtual=False, attributes=None):
        item = self.new_sketch(type, virtual=virtual, attributes=attributes)
        item.id = str(uuid4())
        item.name = name
        return ~item

    def select(self, *names):
        result = self._owner
        for name in names:
            result = result.objects._items_by_name.get(name)
            if result is None:
                return None
        return result

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False, excess=False):
        with self._owner.lock:
            if self.__dict__.get("_items"):
                file.write(u"%s<Objects>\n" % ident)
                for object in self._items.values():
                    object.compose(ident=ident + u"\t", file=file, shorter=shorter, excess=excess)
                file.write(u"%s</Objects>\n" % ident)

    def replicate(self, another):
        with self._owner.lock:
            copy = None

            if isinstance(another, MemoryObjectSketch):
                enumeration = another,
            elif isinstance(another, MemoryObjects):
                if "_items" in another.__dict__:
                    enumeration = iter(another._items.values())
                else:
                    enumeration = ()
            else:
                raise ValueError("Object or objects collection required")

            for item in enumeration:
                copy = MemoryObjectDuplicationSketch(self,
                    self._owner.application, None if self._owner.is_application else self._owner,
                    item)
                copy.id = str(uuid4())
                copy.name = item.name
                ~copy

                copy.objects.replicate(item.objects)
                copy.actions.replicate(item.actions)

                managers.dispatcher.dispatch_handler(copy, "on_create")
                if self._owner.is_object and copy.virtual == self._owner.virtual:
                    managers.dispatcher.dispatch_handler(self._owner, "on_insert", copy)
                    managers.dispatcher.dispatch_handler(self._owner, "on_layout", copy)

            if copy:
                if self._owner.is_object and self._owner.virtual == copy.virtual:
                    self._owner.invalidate(upward=True)
                copy.autosave()

        return copy

    def __getitem__(self, key):
        return self._items.get(key) or self._items_by_name[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new object")

    def __delitem__(self, key):
        self.on_delete(self._items.get(key) or self._items_by_name[key])

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "objects of %s" % self._owner


from .object import MemoryObjectSketch, MemoryObjectRestorationSketch, MemoryObjectDuplicationSketch, MemoryObjectGhost
