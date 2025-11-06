
from builtins import object
import sys
if sys.version_info[0] < 3:
    from collections import Sequence
else:
    from collections.abc import Sequence

from collections import deque

import settings

from logs import log
from utils.properties import lazy, roproperty, rwproperty
from .analyzer import analyze_script_structure


class CompilationProfileEntity(object):

    def __init__(self, origin, context):
        self._origin = origin
        self._context = context

        self._stateful = origin.stateful
        self._hierarchy = origin.hierarchy

    origin = roproperty("_origin")
    context = roproperty("_context")

    stateful = roproperty("_stateful")
    hierarchy = roproperty("_hierarchy")


class CompilationProfileEntry(CompilationProfileEntity):

    def __init__(self, origin, context,
            on_initialize, on_execute, on_render, on_wysiwyg,
            dynamic, mapping):
        super(CompilationProfileEntry, self).__init__(origin, context)

        self._klass = origin.factory(context, dynamic=dynamic, mapping=mapping)  # also need to calculate dynamic

        self._dynamic = self._klass._dynamic
        self._optimization_priority = self._klass._optimization_priority

        self._on_initialize = on_initialize
        self._on_execute = on_execute
        self._on_render = on_render
        self._on_wysiwyg = on_wysiwyg

    klass = roproperty("_klass")

    dynamic = roproperty("_dynamic")
    optimization_priority = roproperty("_optimization_priority")

    on_initialize = rwproperty("_on_initialize")
    on_execute = rwproperty("_on_execute")
    on_render = rwproperty("_on_render")
    on_wysiwyg = rwproperty("_on_wysiwyg")


class CompilationProfileEntries(Sequence):

    def __init__(self, profile):
        self._profile = profile
        self._items = deque()

    def new(self, origin,
            on_initialize=None, on_execute=None, on_render=None, on_wysiwyg=None,
            dynamic=None):
        submapping = self._profile._mapping.get(origin.name, self)
        if submapping is self:
            item = CompilationProfileEntry(
                origin, self._profile._context,
                on_initialize, on_execute, on_render, on_wysiwyg,
                dynamic, None)
        else:
            item = CompilationProfileEntry(
                origin, self._profile._context,
                on_initialize, on_execute, on_render, on_wysiwyg,
                1, submapping)
        self._items.append(item)
        return item

    def normalize(self):
        self._items = sorted(self._items, key=lambda item: (item.hierarchy, item.optimization_priority))

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)


class CompilationProfileEmptyEntries(Sequence):

    def normalize(self):
        pass

    def __getitem__(self, index):
        raise IndexError

    def __len__(self):
        return 0


class CompilationProfileEmptyMapping(object):

    def get(self, name, default):
        return None


class CompilationProfile(CompilationProfileEntity):

    _empty_entries = CompilationProfileEmptyEntries()
    _empty_mapping = CompilationProfileEmptyMapping()

    @lazy
    def _mapping(self):
        if self._action and settings.ANALYZE_SCRIPT_STRUCTURE:
            return analyze_script_structure(self._action.source_code, self._action.scripting_language, self._source_mapping)
        else:
            return self._source_mapping or self._empty_mapping

    @lazy
    def _entries(self):
        if self._origin.objects:
            entries = CompilationProfileEntries(self)
            for child in self._origin.objects.values():
                if child.type.invisible:
                    continue
                entries.new(child)
            return entries
        else:
            return self._empty_entries

    def __init__(self, origin, context, dynamic=None, mapping=None):
        super(CompilationProfile, self).__init__(origin, context)

        self._dynamic = dynamic or origin.type.dynamic
        self._source_mapping = mapping
        self._optimization_priority = origin.type.optimization_priority

        self._action = origin.actions.get(context)
        self._class_name = "_".join((origin.type.class_name, origin.id.replace("-", "_"), context.replace("-", "_")))

    def __enter__(self):
        self._entries = CompilationProfileEntries(self)
        return self._entries

    def __exit__(self, extype, exvalue, extraceback):
        pass

    def _set_dynamic(self, value):
        if value < self._dynamic:
            raise Exception("Dynamic can't be lowered")
        if value > 1:
            raise ValueError("Dynamic must be 0 or 1")
        if settings.DETAILED_LOGGING:
            log.write("Change profile to %s for %s in %s context" % (("dynamic" if self._dynamic else "NOT dynamic"), self._origin, self._context))
        self._dynamic = value

    def _set_optimization_priority(self, value):
        if value < 0 or value > 1:
            raise ValueError("Optimization priority must be 0 or 1")
        self._optimization_priority = value

    dynamic = rwproperty("_dynamic", _set_dynamic)
    optimization_priority = rwproperty("_optimization_priority", _set_optimization_priority)

    action = roproperty("_action")
    class_name = rwproperty("_class_name")
    entries = roproperty("_entries")

    def normalize(self):
        self._entries.normalize()

        # already dynamic
        if self._dynamic:
            return

        # check action and enable dynamic if exists
        if self._action and self._action.source_code:
            if settings.DETAILED_LOGGING:
                log.write("Enable dynamic for %s due to %s action presence" % (self._origin, self._action.name))
            self._dynamic = 1
            return

        # check stateful attribute
        if self._stateful:
            if settings.DETAILED_LOGGING:
                log.write("Enable dynamic for %s due to stateful attribute" % self._origin)
            self._dynamic = 1
            return

        for child in self._entries:
            # object with dynamic child must be dynamic
            if child.dynamic:
                if settings.DETAILED_LOGGING:
                    log.write("Enable dynamic for %s due to child dynamic attribute" % self._origin)
                self._dynamic = 1
                return

            # object with handlers must be dynamic too
            if child.on_initialize or child.on_execute or child.on_render or child.on_wysiwyg:
                if settings.DETAILED_LOGGING:
                    log.write("Enable dynamic for %s due to handler(s) presence" % self._origin)
                self._dynamic = 1
                return
