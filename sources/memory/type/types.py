import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from threading import RLock

import settings
import file_access
import managers

from utils import verificators
from utils.properties import weak, roproperty
from logs import log

from ..auxiliary import parse_index_line
from ..generic import MemoryBase
from .type import MemoryTypeSketch


NOT_LOADED = "NOT LOADED"


@weak("_owner")
class MemoryTypes(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._lock = RLock()  # owner._lock

        self._items = {}
        self._index = {}
        self._lazy = True

    owner = roproperty("_owner")
    lock = roproperty("_lock")

    def on_complete(self, item):
        with self._lock:
            self._items[item.id] = item
            self._index[item.name] = item.id

    def new_sketch(self, restore=False):
        return MemoryTypeSketch(self)

    def save(self):
        with self._lock:
            if self._lazy:
                self._discover(full=True)
            data = "\n".join("%s:%s" % (uuid, name) for name, uuid in self._index.items())
        managers.file_manager.write(file_access.FILE, None, settings.INDEX_LOCATION, data)

    # unsafe
    def _load(self, uuid):
        try:
            item = self._owner.load_type(uuid, silently=True)
        except IOError:
            log.warning("Unable to load type: %s" % uuid)
            return None
        else:
            self._items[uuid] = item
            self._index[item.name] = uuid
            return item

    # unsafe
    def _discover(self, full=False, load=False):
        if managers.file_manager.exists(file_access.FILE, None, settings.INDEX_LOCATION):
            data = managers.file_manager.read(file_access.FILE, None, settings.INDEX_LOCATION)
            for line in data.splitlines():
                try:
                    uuid, name = parse_index_line(line)
                except ValueError:
                    log.warning("Ignore erroneous index entry: %s" % line)
                    continue
                self._items.setdefault(uuid, NOT_LOADED)
                self._index.setdefault(name, uuid)

        # additionally check directories
        listing = managers.file_manager.list(file_access.TYPE)
        for uuid in listing:
            try:
                verificators.uuid(uuid)
            except ValueError:
                log.warning("Ignore non-type directory: %s" % uuid)
                continue
            self._items.setdefault(uuid, NOT_LOADED)

        # load ONLY types that has no record in index
        if full and len(self._items) > len(self._index):
            unknown = set(self._items.keys()) - set(self._index.values())
            for uuid in unknown:
                self._load(uuid)

        # load all types that's not loaded yet
        if load:
            for uuid, item in self._items.items():
                if item is NOT_LOADED:
                    self._load(uuid)

        self._lazy = False

    def search(self, uuid_or_name, autocomplete=False):
        if uuid_or_name[8:9] == "-":
            return self.get(uuid_or_name)
        else:
            uuid_or_name = uuid_or_name.lower()
            try:
                uuid = self._index[uuid_or_name]
            except KeyError:
                if self._lazy:
                    with self._lock:
                        if self._lazy:
                            self._discover(full=True)
                        try:
                            uuid = self._index[uuid_or_name]
                        except KeyError:
                            if autocomplete:
                                for name, uuid in self._index.items():
                                    if name.lower().startswith(uuid_or_name):
                                        return self.get(uuid)
                            return None
                        else:
                            return self.get(uuid)
                if autocomplete:
                    with self._lock:
                        for name, uuid in self._index.items():
                            if name.lower().startswith(uuid_or_name):
                                return self.get(uuid)
                return None
            else:
                return self.get(uuid)

    def unload(self, uuid, remove=False):
        with self._lock:
            if remove:
                name = self._items.pop(uuid).name
                self._index.pop(name, None)
                self.save()
            else:
                self._items[uuid] = NOT_LOADED

    def __getitem__(self, uuid):
        if uuid in self._items:
            item = self._items[uuid]
        else:
            # TODO: check to perform full discovery here
            if self._lazy and managers.file_manager.exists(file_access.TYPE, uuid, settings.TYPE_FILENAME):
                with self._lock:
                    item = self._items.get(uuid, KeyError)
                    if item in (KeyError, NOT_LOADED):
                        return self._load(uuid)
                    else:
                        return item
            else:
                raise
            
        if item is NOT_LOADED:
            with self._lock:
                item = self._items[uuid]
                if item is NOT_LOADED:
                    return self._load(uuid)
                else:
                    return item
        else:
            return item

    def __iter__(self):
        with self._lock:
            if self._lazy:
                self._discover(load=True)
            return iter(self._items)

    def __len__(self):
        with self._lock:
            if self._lazy:
                self._discover()
            return len(self._items)

    def __str__(self):
        return "types%s" % ":lazy" if self._lazy else ""
