import sys
if sys.version_info[0] < 3:
    from collections import Sequence
else:
    from collections.abc import Sequence

from utils.properties import weak, roproperty
from ..generic import MemoryBase
from .actionparameter import MemoryTypeActionParameterSketch


@weak("_owner")
class MemoryTypeActionParameters(MemoryBase, Sequence):

    def __init__(self, owner):
        self._owner = owner
        self._items = []

    owner = roproperty("_owner")

    def on_complete(self, item):
        self._items.append(item)

    def new_sketch(self, restore=False):
        return MemoryTypeActionParameterSketch(self)

    # unsafe
    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<Parameters>\n" % ident)
            for parameter in self._items:
                parameter.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Parameters>\n" % ident)

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "parameters of %s" % self._owner
