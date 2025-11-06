
from builtins import str
from builtins import next
from weakref import ref
import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from itertools import chain
from threading import RLock, Event
from uuid import uuid4

import settings
import managers
import file_access

from utils import verificators
from utils.verificators import complies
from utils.properties import lazy, weak, roproperty
from logs import log

from ..constants import DEFAULT_APPLICATION_NAME
from ..generic import MemoryBase
from .application import MemoryApplicationSketch, MemoryApplicationRestorationSketch, MemoryApplicationGhost


@weak("_owner")
class MemoryApplications(MemoryBase, Mapping):

    @lazy
    def default(self):
        try:
            return self[settings.DEFAULT_APPLICATION or next(iter(self))]
        except (KeyError, StopIteration):
            return None

    def __init__(self, owner):
        self._owner = owner
        self._lock = owner._lock
        self._items = {}
        self._queue = False
        self._event = Event()
        self._known = set()

    owner = roproperty("_owner")
    lock = roproperty("_lock")

    def on_complete(self, item, restore):
        with self._lock:
            if item._id is None:
                item._id = str(uuid4())
            if item._name is None:
                item._name = DEFAULT_APPLICATION_NAME

            try:
                self._known.remove(item._id)
            except KeyError:
                self._event.set()

            self._items[item._id] = item

    def new_sketch(self, restore=False):
        return (MemoryApplicationRestorationSketch if restore
            else MemoryApplicationSketch)(self)

    def new(self, name=None):
        item = self.new_sketch()
        item.id = str(uuid4())
        item.name = name
        return ~item

    def _explore(self):
        self._queue = {filename for filename
            in managers.file_manager.list(file_access.APPLICATION)
            if complies(filename, verificators.uuid)} - set(self._items.keys())
        if not self._queue:
            self._queue = None

    def search(self, uuid_or_name, autocomplete=False):
        try:
            return self[uuid_or_name]
        except KeyError:
            if autocomplete:
                with self._lock:
                    for item in self.values():
                        if item.name.lower().startswith(uuid_or_name):
                            return item
            return None

    def unload(self, uuid, remove=False):
        with self._lock:
            try:
                application = self._items[uuid]
            except KeyError:
                if self._queue is None:
                    raise
                elif self._queue is False:
                    if not managers.file_manager.exists(file_access.APPLICATION, uuid, settings.APPLICATION_FILENAME):
                        self._explore()
                        raise
                elif uuid not in self._queue:
                    raise

                if remove:
                    self._queue.remove(uuid)
                    self._event.set()
            else:
                managers.engine.threads.stop(uuid)
                application.unimport_libraries()
                del self._items[uuid]
                application.__class__ = MemoryApplicationGhost

                if remove:
                    self._event.set()
                else:
                    if self._queue is None:
                        self._queue = {uuid}
                    elif self._queue is False:
                        pass
                    else:
                        self._queue.add(uuid)

    def __getitem__(self, uuid):
        try:
            return self._items[uuid]
        except KeyError:
            if self._queue is None:
                raise
            else:
                on_start = None
                try:
                    with self._lock:
                        try:
                            return self._items[uuid]
                        except KeyError:
                            if self._queue is None:
                                raise
                            elif self._queue is False:
                                if not managers.file_manager.exists(file_access.APPLICATION, uuid, settings.APPLICATION_FILENAME):
                                    self._explore()
                                    raise
                            else:
                                self._queue.remove(uuid)

                            self._known.add(uuid)
                            self._items[uuid] = item = self._owner.load_application(uuid, silently=True)
                            on_start = item.on_start
                            return item
                finally:
                    if on_start:
                        on_start()

    def __iter__(self):
        with self._lock:
            self._event.clear()
            if self._queue is False:
                self._explore()

            items = list(self._items.keys())
            if self._queue:
                items += self._queue

        for item in items:
            if self._event.is_set():
                raise RuntimeError("dictionary changed size during iteration")
            yield item

    def __len__(self):
        with self._lock:
            if self._queue is False:
                self._explore()
            return len(self._items) + len(self._queue) if self._queue else len(self._items)

    def __str__(self):
        return "applications"
