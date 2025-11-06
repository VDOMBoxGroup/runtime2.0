from __future__ import unicode_literals
import codecs
from utils.properties import weak, roproperty, rwproperty
from ..generic import MemoryBase


@weak("_collection")
class MemoryTypeEventParameterSketch(MemoryBase):

    _name = None
    _description = ""
    _order = 0

    def __init__(self, collection):
        self._collection = collection

    owner = property(lambda self: self._collection.owner)

    name = rwproperty("_name")
    description = rwproperty("_description")
    order = rwproperty("_order")

    def __invert__(self):
        if self._name is None:
            raise Exception("Event parameter require name")

        self.__class__ = MemoryTypeEventParameter
        self._collection.on_complete(self)
        return self

    def __str__(self):
        return " ".join([_f for _f in ("parameter", self._name,
            "sketch of %s" % self._collection.owner if self._collection else None) if _f])


class MemoryTypeEventParameter(MemoryTypeEventParameterSketch):

    def __init__(self):
        raise Exception("Use 'new' to create new parameter")

    name = roproperty("_name")
    description = roproperty("_description")
    order = roproperty("_order")

    def compose(self, ident="", file=None):
        file.write("%s<Parameter Name=\"%s\" Description=\"%s\" Order=\"%s\"/>\n" %
            (ident, self._name, codecs.encode(self._description, "xml"), self._order))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in ("parameter", self._name,
            "of %s" % self._collection.owner if self._collection else None) if _f])
