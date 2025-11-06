
import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from collections import OrderedDict
from utils.properties import weak
from ..generic import MemoryBase


@weak("_owner")
class MemoryBindingParameters(MemoryBase, Mapping):

    def __init__(self, owner, items):
        self._owner = owner
        if items is None:
            self._items = OrderedDict()
        elif isinstance(items, OrderedDict):
            self._items = OrderedDict(items)
        else:
            self._items = OrderedDict(("parameter%d" % index, value) for index, value in enumerate(items, 1))

        # TODO: check for strict accordance to type action parameters
        #       to do this need to obtain appropriate container id
        #       to select correct action. We can have many action with
        #       similar name for different (HTML, Flash) containers

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "parameters of %s" % self._owner
