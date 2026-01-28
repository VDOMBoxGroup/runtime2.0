# from __future__ import absolute_import
import codecs


from threading import RLock

import settings
import managers

from logs import log
from utils.properties import lazy, weak, constant, roproperty, rwproperty
from utils import verificators

from ..constants import NON_CONTAINER, CONTAINER, TOP_CONTAINER, RENDER_CONTEXT
from ..generic import MemoryBase
from ..empties import ChangeEmptyError, EmptySet

from .attributes import MemoryAttributesSketch
from .actions import MemoryActions

from .events import MemoryEvents
from .bindings import MemoryBindings
from .structure import MemoryStructureSketch, MemoryStructure


@weak("_collection", "_parent", "_application")
class MemoryObjectSketch(MemoryBase):

    is_object = constant(True)

    is_non_container = property(lambda self: self._type.container == NON_CONTAINER)
    is_container = property(lambda self: CONTAINER <= self._type.container <= TOP_CONTAINER)
    is_top_container = property(lambda self: self._type.container == TOP_CONTAINER)

    _restore = False

    generic = RENDER_CONTEXT,

    @lazy
    def _primary(self):
        if self._virtual:
            result = self
            while result._parent and result._parent.virtual:
                result = result._parent
            return result
        else:
            return self._application

    @lazy
    def _bindings(self):
        return MemoryBindings(self)

    @lazy
    def _structure(self):
        return None if self._parent or self._virtual else MemoryStructureSketch(self)

    _order = None
    _id = None
    _name = None
    _original_name = None

    _dependents = EmptySet()

    def __init__(self, collection, type, application, parent, virtual=False, attributes=None):
        self._collection = collection
        self._virtual = virtual
        self._application = application
        self._parent = parent

        # initialize lock
        if parent:
            if virtual == parent.virtual:
                self._lock = parent.lock
            else:
                self._lock = RLock()
        else:
            self._lock = application.lock

        # generic characteristics
        self._type = type

        # collections
        self._attributes = MemoryAttributesSketch(self, values=attributes)
        self._objects = MemoryObjects(self)
        self._events = MemoryEvents(self)
        self._actions = MemoryActions(self)

        # internal
        self._classes = {}

    # lock = property(lambda self: self._application.lock)
    lock = roproperty("_lock")
    order = rwproperty("_order")
    is_virtual = virtual = roproperty("_virtual")
    application = rwproperty("_application")
    container = property(lambda self: self._parent.container if self._parent else self)
    parent = rwproperty("_parent")
    primary = roproperty("_primary")

    type = rwproperty("_type")
    id = rwproperty("_id")
    name = rwproperty("_name")
    original_name = roproperty("_original_name")

    attributes = roproperty("_attributes")
    objects = roproperty("_objects")
    events = roproperty("_events")
    actions = roproperty("_actions")
    bindings = roproperty("_bindings")

    structure = roproperty("_structure")

    stateful = property(lambda self: int(self._attributes.get("stateful", 0)))
    hierarchy = property(lambda self: int(self._attributes.get("hierarchy", 0)))

    def select(self, name, *names):
        if self._name == name:
            return self._objects.select(*names)
        else:
            return None

    def select_original(self, name, *names):
        if self._original_name or self._name == name:
            return self._objects.select(*names)
        else:
            return None

    def __invert__(self):
        ~self._attributes
        if self.__dict__.get("_structure") is not None:
            ~self._structure

        restore = self._restore
        self.__class__ = MemoryObject
        self._collection.on_complete(self, restore)
        if not restore:
            managers.dispatcher.dispatch_handler(self, "on_create")
            if self._parent and self._virtual == self._parent.virtual:
                self._parent.invalidate(upward=True)
            self.autosave()
        return self

    def __str__(self):
        return " ".join([_f for _f in (
            "virtual" if getattr(self, "_virtual", None) else None,
            "object",
            ":".join([_f for _f in (getattr(self, "_id", None), getattr(self, "_name", None)) if _f]),
            "sketch") if _f])


class MemoryObjectRestorationSketch(MemoryObjectSketch):

    _restore = True


class MemoryObjectDuplicationSketch(MemoryObjectSketch):

    def __init__(self, collection, application, parent, another):
        super(MemoryObjectDuplicationSketch, self).__init__(collection,
            another.type, application, parent,
            virtual=parent.virtual if parent else False,
            attributes=another.attributes)


class MemoryObjectGhost(MemoryBase):

    def __str__(self):
        return " ".join([_f for _f in (
            "obsolete",
            "virtual" if self._virtual else None,
            "object",
            ":".join([_f for _f in (self._id, self._name) if _f])) if _f])


class MemoryObject(MemoryObjectSketch):

    @lazy
    def _structure(self):
        return None if self._parent or self._virtual else MemoryStructure(self)

    def __init__(self):
        raise Exception(u"Use 'new' to create new object")

    def _set_name(self, value):
        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Invalid name: %r" % value)

        with self.lock:
            self._collection.on_rename(self, value)
            managers.dispatcher.dispatch_handler(self, "on_rename", value)
            self._name = value
            self.invalidate(upward=True)
            self.autosave()

    type = roproperty("_type")
    id = roproperty("_id")
    name = rwproperty("_name", _set_name)

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False, excess=False):
        information = u"ID=\"%s\" Name=\"%s\" Type=\"%s\"" % (self._id, codecs.encode(self._name, "xml"), self._type.id)
        if self._attributes or self._objects or self._actions:
            file.write(u"%s<Object %s>\n" % (ident, information))
            self._attributes.compose(ident=ident + u"\t", file=file, shorter=shorter, excess=excess)
            self._objects.compose(ident=ident + u"\t", file=file, shorter=shorter, excess=excess)
            self._actions.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Object>\n" % ident)
        else:
            file.write(u"%s<Object %s/>\n" % (ident, information))

    def autosave(self):
        if not self._virtual:
            self._application.autosave()

    def invalidate(self, contexts=None, downward=False, upward=False):
        with self.lock:
            # cleanup compiled classes
            if "_classes" in self.__dict__:
                if contexts:
                    if isinstance(contexts, str):
                        if settings.DETAILED_LOGGING:
                            log.write("Invalidate %s in %s context" % (self, contexts))
                        self._classes.pop(contexts, None)
                    else:
                        if settings.DETAILED_LOGGING:
                            log.write("Invalidate %s in %s contexts" % (self, ", ".join(contexts)))
                        for context in contexts:
                            self._classes.pop(context, None)
                else:
                    if settings.DETAILED_LOGGING:
                        log.write("Invalidate %s" % self)
                    self._classes = {}

            # NOTE: this can delete compiled e2vdom scripts
            # TODO: check necessity of resource invalidation
            #       possible this must be done on object delete
            # NOTE: cleanup=False to avoid excessive file operations

            # cleanup resources
            managers.resource_manager.invalidate_resources(self._id, cleanup=False)

            # perform downward invalidation
            if downward:
                for child in self._objects.values():
                    child.invalidate(contexts=contexts, downward=True)

            # perform upward invalidation
            if upward:
                # NOTE: this can cause issues in case when
                #       virtual objects will be stored between render
                #       it may be worth adding a special attribute
                #       that break invalidate chain for dynamic objects

                # validate only same (non-)virtual objects in chain
                if self._parent and self._virtual == self._parent.virtual:
                    self._parent.invalidate(contexts=contexts, upward=True)
                for dependent in self._dependents:
                    if settings.DETAILED_LOGGING:
                        log.write("Invalidate %s dependent %s" % (self, dependent))
                    dependent.invalidate(contexts=contexts, upward=True)

            # update factory counter to indicate a change
            if self._factory_calls:
                self._factory_invalidates += 1

    def attach(self, object):
        with self.lock:
            try:
                self._dependents.add(object)
            except ChangeEmptyError:
                self._dependents = {object}

    def detach(self, object):
        with self.lock:
            self._dependents.remove(object)

    _factory_calls = 0
    _factory_invalidates = 0

    def factory(self, context, dynamic=None, mapping=None, probe=False):
        # we are busy
        managers.memory._operations += 1

        # check if already exists
        if dynamic is None:
            try:
                klass = self._classes[context]
            except KeyError:
                if probe:
                    return None
            else:
                if dynamic is None or dynamic <= klass._dynamic:
                    return klass

        # remember invalidate count
        with self.lock:
            self._factory_calls += 1
            invalidates = self._factory_invalidates

        # start main loop
        while 1:
            try:
                new_klass = managers.compiler.compile(self, context, dynamic=dynamic, mapping=mapping)
            except BaseException:
                # just decrease calls counter on error
                with self.lock:
                    self._factory_calls -= 1
                raise
            else:
                # on successfull compilation...
                with self.lock:
                    if invalidates == self._factory_invalidates:
                        # if has no changes
                        if self._factory_calls > 1:
                            # decrease calls counter
                            self._factory_calls -= 1
                        else:
                            # or remove to free memory if no other calls
                            del self._factory_calls
                            self.__dict__.pop("_factory_invalidates", None)

                        # update klass if needed and return
                        klass = self._classes.get(context)
                        if klass is None or (dynamic or 0) > klass._dynamic:
                            self._classes[context] = klass = new_klass
                        return klass
                    else:
                        # or just update stored value
                        invalidates = self._factory_invalidates

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in (
            "virtual" if self._virtual else None,
            "object",
            ":".join([_f for _f in (self._id, self._name) if _f])) if _f])


from .objects import MemoryObjects
