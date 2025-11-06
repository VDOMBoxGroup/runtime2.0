from __future__ import unicode_literals
import codecs
from utils.properties import weak, roproperty, rwproperty
from ..generic import MemoryBase
from .eventparameters import MemoryTypeEventParameters


@weak("_collection")
class MemoryTypeEventSketch(MemoryBase):

    _name = None
    _description = u""

    def __init__(self, collection):
        self._collection = collection
        self._parameters = MemoryTypeEventParameters(self)

    owner = property(lambda self: self._collection.owner)

    name = rwproperty("_name")
    description = rwproperty("_description")
    parameters = roproperty("_parameters")

    def __invert__(self):
        if self._name is None:
            raise Exception(u"Event require name")

        self.__class__ = MemoryTypeEvent
        self._collection.on_complete(self)
        return self

    def __str__(self):
        return " ".join([_f for _f in ("event", self._name,
            "sketch of %s" % self._collection.owner if self._collection else None) if _f])


class MemoryTypeEvent(MemoryTypeEventSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new event")

    name = roproperty("_name")
    description = roproperty("_description")
    parameters = roproperty("_parameters")

    def compose(self, ident=u"", file=None):
        information = u"Name=\"%s\" Description=\"%s\"" % \
            (self._name, codecs.encode(self._description, "xml"))
        if self._parameters:
            file.write(u"%s<Event %s>\n" % (ident, information))
            self._parameters.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Event>\n" % ident)
        else:
            file.write(u"%s<Event %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in ("event", self._name,
            "of %s" % self._collection.owner if self._collection else None) if _f])
