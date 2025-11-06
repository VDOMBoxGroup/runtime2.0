
#from builtins import str
from builtins import object
import marshal
import json

import settings
import managers
import file_access

from utils.properties import aroproperty, roproperty

from .constants import LISTING, SYMBOLS, BYTECODE
from .exceptions import CompilationError


class Bytecode(object):

    __slots__ = "_bytecode", "_symbols"

    source_extension = aroproperty()
    extensions = aroproperty()

    @classmethod
    def cleanup(cls, executable):
        if settings.STORE_BYTECODE:
            for entity, extension in cls.extensions.items():
                if extension:
                    location = executable.locate(entity)
                    if location:
                        managers.file_manager.delete(file_access.FILE, None, location + extension)

    @classmethod
    def compile(cls, executable):
        raise NotImplementedError

    @classmethod
    def restore(cls, executable):
        bytecode, symbols = None, None

        if settings.STORE_BYTECODE:
            extension = cls.extensions.get(BYTECODE)
            if extension:
                location = executable.locate(BYTECODE)
                if location:
                    bytecode = managers.file_manager.read(file_access.FILE, None, location + extension, default=None)
                    if bytecode:
                        bytecode = marshal.loads(bytecode)

                        extension = cls.extensions.get(SYMBOLS)
                        if extension:
                            location = executable.locate(SYMBOLS)
                            if location:
                                symbols = managers.file_manager.read(file_access.FILE, None, location + extension, default=None)
                                if symbols:
                                    symbols = json.loads(symbols)

        if bytecode:
            return cls(executable, bytecode, listing=None, symbols=symbols, store=False)
        else:
            return None

    def __init__(self, executable, bytecode, listing=None, symbols=None, store=True):
        self._bytecode = bytecode
        self._symbols = symbols

        if store and settings.STORE_BYTECODE:
            extension = self.extensions.get(BYTECODE)
            if extension:
                location = executable.locate(BYTECODE)
                if location:
                    managers.file_manager.write(file_access.FILE, None, location + extension, marshal.dumps(bytecode))

            if listing:
                extension = self.extensions.get(LISTING)
                if extension:
                    location = executable.locate(LISTING)
                    if location:
                        managers.file_manager.write(file_access.FILE, None, location + extension, listing)

            if symbols:
                extension = self.extensions.get(SYMBOLS)
                if extension:
                    location = executable.locate(LISTING)
                    if location:
                        managers.file_manager.write(file_access.FILE, None, location + extension, json.dumps(symbols))

    bytecode = roproperty("_bytecode")
    symbols = roproperty("_symbols")

    def explain(self):
        pass

    def execute(self, context, namespace, arguments):
        raise NotImplementedError


class ErrorBytecode(Bytecode):

    __slots__ = ("_name", "_source", "_cause")

    source_extension = ()
    extensions = {}

    def __init__(self, executable, cause=None):
        self._name = executable.name
        self._source = str(executable)
        self._cause = cause

    def execute(self, context, namespace, arguments):
        raise CompilationError("Unable to compile \"%s\"" % self._name, self._source, self._cause)
