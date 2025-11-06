from builtins import object
import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from collections import OrderedDict
from utils.properties import weak, lazy, roproperty
from ..generic import MemoryBase
from .attribute import MemoryTypeAttributeSketch


class MemoryTypeAttributesValues(object):

    def __str__(self):
        return self._description

    def __repr__(self):
        return "<memory %s at 0x%08X>" % (self, id(self))


@weak("_owner")
class MemoryTypeAttributes(MemoryBase, Mapping):

    @lazy
    def klass(self):
        names = tuple(self._items)
        namespace = {name: attribute.default_value for name, attribute in self._items.items()}
        namespace.update({
            "__module__": "memory.type.attributes",
            "_description": "attributes values of %s" % self._owner,
            "_enumeration": names,
            "_set": frozenset(names)})
        return type("AttributesValues", (MemoryTypeAttributesValues,), namespace)

    def __init__(self, owner):
        self._owner = owner
        self._items = OrderedDict()

    owner = roproperty("_owner")

    def on_complete(self, item):
        self._items[item.name] = item

    def new_sketch(self, restore=False):
        return MemoryTypeAttributeSketch(self)

    # unsafe
    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<Attributes>\n" % ident)
            for attribute in self._items.values():
                attribute.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Attributes>\n" % ident)

    def __getitem__(self, name):
        return self._items[name]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "attributes of %s" % self._owner
