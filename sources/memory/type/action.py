from __future__ import unicode_literals
import codecs
from utils.properties import weak, roproperty, rwproperty
from ..generic import MemoryBase
from .actionparameters import MemoryTypeActionParameters


@weak("_collection")
class MemoryTypeActionSketch(MemoryBase):

    _scope = None
    _name = None
    _display_name = None
    _description = ""
    _source_code = ""

    def __init__(self, collection):
        self._collection = collection
        self._parameters = MemoryTypeActionParameters(self)

    owner = property(lambda self: self._collection.owner)

    scope = rwproperty("_scope")
    name = rwproperty("_name")
    display_name = rwproperty("_display_name")
    description = rwproperty("_description")
    source_code = rwproperty("_source_code")
    parameters = roproperty("_parameters")

    def __invert__(self):
        if self._scope is None:
            raise Exception("Type action require scope")
        if self._name is None:
            raise Exception("Type action require name")

        if self._display_name is None:
            self._display_name = self._name

        self.__class__ = MemoryTypeAction
        self._collection.on_complete(self)
        return self

    def __str__(self):
        return " ".join([_f for _f in ("action", "\"%s\"" % self._name,
            "sketch of %s" % self._collection.owner if self._collection else None) if _f])


class MemoryTypeAction(MemoryTypeActionSketch):

    def __init__(self):
        raise Exception("User 'new_sketch' to create action")

    scope = roproperty("_scope")
    name = roproperty("_name")
    display_name = roproperty("_display_name")
    description = roproperty("_description")
    source_code = roproperty("_source_code")
    parameters = roproperty("_parameters")

    # unsafe
    def compose(self, ident="", file=None):
        file.write("%s<Action Name=\"%s\" DisplayName=\"%s\" Description=\"%s\">\n" %
            (ident, self._name, codecs.encode(self._display_name, "xml"), codecs.encode(self._description, "xml")))
        self._parameters.compose(ident=ident + "\t", file=file)
        file.write("%s\t<SourceCode>\n" % ident)
        file.write("%s\n" % codecs.encode(self._source_code.strip(), "cdata"))
        file.write("%s\t</SourceCode>\n" % ident)
        file.write("%s</Action>\n" % ident)

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in ("action", "\"%s\"" % self._name,
            "of %s" % self._collection.owner if self._collection else None) if _f])
