import codecs
from builtins import str
import sys

import settings
import managers
import file_access

from utils.properties import weak, constant, rwproperty
from utils import verificators
from scripting.executable import SOURCE_CODE, Executable

from ..generic import MemoryBase


@weak("_collection")
class MemoryLibrarySketch(MemoryBase, Executable):

    is_library = constant(True)

    _restore = False

    _name = None
    _top = 0
    _left = 0
    _state = False

    def __init__(self, collection):
        self._collection = collection

    lock = property(lambda self: self._collection.owner.lock)
    owner = property(lambda self: self._collection.owner)
    application = property(lambda self: self._collection.owner.application)

    scripting_language = property(lambda self: str(self._collection.owner.application.scripting_language))
    package = property(lambda self: str(self._collection.owner.application.id))
    signature = property(lambda self: "<%s library %s>" % (self.scripting_language, self.name.lower()))

    name = rwproperty("_name")

    def locate(self, entity):
        if entity is SOURCE_CODE or settings.STORE_BYTECODE:
            return managers.file_manager.locate(file_access.LIBRARY, self.application.id, self.name)
        else:
            return None

    def __invert__(self):
        restore = self._restore
        self.__class__ = MemoryLibrary
        self._collection.on_complete(self, restore)
        if not restore:
            self._collection.owner.autosave()
        return self

    def __str__(self):
        return " ".join([_f for _f in (
            "library",
            "\"%s\"" % self._name if self._name else None,
            "sketch",
            " of %s" % self._collection.owner if self._collection else None) if _f])


class MemoryLibraryRestorationSketch(MemoryLibrarySketch):

    _restore = True


class MemoryLibrary(MemoryLibrarySketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new library")

    def _set_name(self, value):
        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Invalid name: %r" % value)

        with self._collection.owner.lock:
            self._collection.on_rename(self, value)
            source_code = self.source_code
            self.cleanup(remove=True)
            self._name = value
            self.source_code = source_code
            self._collection.owner.autosave()

    name = rwproperty("_name")

    def cleanup(self, remove=False):
        with self.lock:
            super(MemoryLibrary, self).cleanup(remove=remove)
            self.unimport()

    def unimport(self):
        sys.modules.pop("%s.%s" % (self.application.id, self._name), None)

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False):
        information = u"Name=\"%s\"" % codecs.encode(self._name, "xml")
        if not shorter and self.source_code:
            file.write(u"%s<Library %s>\n" % (ident, information))
            file.write(u"%s\n" % codecs.encode(self.source_code, "cdata"))
            file.write(u"%s</Library>\n" % ident)
        else:
            file.write(u"%s<Library %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in (
            "library",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._collection.owner if self._collection else None) if _f])
